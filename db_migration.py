
from flask import current_app as app
from sqlalchemy import create_engine, inspect, sql

from app import create_app
from app.models import *
from app.utilities import c_sum

import pandas as pd
from sqlalchemy.orm import sessionmaker, Query

from time import time, localtime

import logging
import logging.config


class DBMigration:  # singleton class

    # models: List[Base] = [TextText]
    models: List[Base] = Base.__subclasses__()

    # logging #todo consider creating different logs for each CSV_file/model
    tt = '-'.join([str(i) for i in localtime()])
    print(f'----- {tt} -------')
    logging.config.fileConfig('logging.conf',
                              defaults={
                                  'logfilename'    : f'logs/db_migration_{tt}.log',
                                  'fulllogfilename': f'logs/db_migration_full_{tt}.log',
                                  'querylogfilename': f"logs/q_{tt}_empty.log",
                                  }
                              )

    def __init__(self):
        self.logger = logging.getLogger('dbLogger')
        self.logger.info('=' * 10 + ' DB migration ' + '=' * 10)

        engine = db.engine  # todo with app.app_context(): engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        Base.metadata.create_all(engine)  # todo db.create_all(engine)
        self.session = sessionmaker(bind=engine)()  # todo session = scoped_session(Session())

        self.faulty_lines_exceptions_dict: Dict[str, Tuple[Base, Exception]] = {}

    def __del__(self):
        self.session.close()

    def load_full_db(self):
        t_total = time()  # for logging
        self.logger.info(F'Staring full DB migration ')
        for model in self.models:
            t_per_model = time()
            self.logger.info(f'Model {model.__name__}')
            self.load_single(model)  # <-----------------------------
            self.logger.info(f'Model {model.__name__} finished in {time() - t_per_model} s.')
        self.logger.info('=' * 12 + f' Total Time elapsed: {time() - t_total} s. ' + '=' * 12 + '\n')
        if self.faulty_lines_exceptions_dict:  # todo log into a file
            # self.logger.error(f'Bad News:\nIn {model.__name__}, file {src_file}, chunk #{chunk_num}')
            self.logger.error(f'There are {self.faulty_lines_exceptions_dict.__len__()} faulty lines in the src data')
            self.logger.debug(f'Check out the log file ({self.logger.handlers[0].__dict__["baseFilename"]})\n')
        else: self.logger.info(f'Everything is fine and dandy\n')

    def load_single(self, model: Base):
        for src_file in model.src_scv:
            t_per_src = time()
            self.logger.info(f'- CSV src file {src_file}')
            self.load_src_file(model, src_file)  # <-----------------------------
            self.logger.info(f'- CSV src file {src_file} finished in {time() - t_per_src} s.')

    def load_src_file(self, model: Base, src_file):
        prime_key_name, _ = get_prime_key(model)
        # with open(src_file) as csv_file:
        csv_file = open(src_file, 'r')
        chunk_num = 0
        exit_flag = False
        while not exit_flag:
            try:  # this for-loop is inside `try` for cases of commas (`,`) in `subject` col without brackets (`"`)
                for dataframe in pd.read_csv(csv_file,
                                             dtype=model.dtype_dic_csv2py,
                                             header=0,
                                             names=model.col_names,
                                             na_values=['x', '#VALUE!', '', 'Unknown'],
                                             chunksize=app.config['CHUNK_SIZE_DB'],
                                            #  skiprows=305868
                                             ):
                    self.logger.debug(f'{model.__name__} loading chunk #{chunk_num}')
                    model_cols = model.__table__.c
                    df_clean: pd.DataFrame = dataframe[[col.key for col in model_cols if 'Csum' != col.key]]
                    df_clean = df_clean.drop_duplicates(prime_key_name)
                    if TextSubject == model: df_clean['Csum'] = df_clean['C'].apply(c_sum)
                    for col in model_cols:
                        if isinstance(col.type, sql.sqltypes.Integer):
                            df_clean[col.name] = pd.to_numeric(df_clean[col.name], errors='raise')  # ='coerce')
                    df_clean = df_clean.astype(object).where(pd.notnull(df_clean), None)  # this is explained in:
                    # https://stackoverflow.com/questions/45395729/unknown-column-nan-in-field-list-python-pandas
                    try:
                        self.session.bulk_insert_mappings(model, df_clean.to_dict(orient='records'))
                        self.session.commit()  # raises an Exception if problem with data
                    except Exception as e:  # todo catch different kinds of exceptions ?
                        # (mysql.connector.errors.DataError) 1406 (22001): Data too long for column
                        # (mysql.connector.errors.IntegrityError) 1062 (23000): Duplicate entry
                        # (mysql.connector.errors.IntegrityError) 1452 (23000): Cannot add or update a child row:
                        #   a foreign key constraint fails
                        #   (`tryout`.`texts`,
                        #   CONSTRAINT `texts_ibfk_1` FOREIGN KEY (`number`) REFERENCES `titles` (`number`))
                        self.logger.debug(f'df chunk insert fail. trying \'exclude_faulty_lines\'')
                        self.logger.debug(f'{e.args[0]}')
                        self.session.rollback()  # self.session.flush()
                        self.exclude_faulty_lines(model, df_clean.to_dict(orient='records'))
                    finally:
                        chunk_num += 1

                exit_flag = True

            except Exception as e_read_csv:
                self.logger.error(f'{e_read_csv.args[0]}')
                self.logger.debug(f'{e_read_csv}')
                self.logger.critical(f'Note: The whole chunk #{chunk_num} was not inserted!\n'
                                     f'(lines {chunk_num * app.config["CHUNK_SIZE_DB"]}-'
                                     f'{chunk_num * (app.config["CHUNK_SIZE_DB"] + 1) - 1})')
                chunk_num += 1  # todo this might cause a problem (or skipping chunks)
                exit_flag = False
        csv_file.close()

    # Finds the line in the data that throws exception during bulk_insert_mapping on data.
    # Recursivly attemps to insert smaller chunks of data until finds a faulty line.
    #   Recieves:
    #       model - current model (table) into which loading data
    #       df_dict - a pd.DataFrame.to_dict(orient='records')
    #       i0 - #line in the current chunk of data - for logging (so you can remove)
    #   Return exceptions_dict (type Dict[str, Tuple[Base, Exception]])
    def exclude_faulty_lines(self, model: Base, df_dict: collections.abc.Mapping, i0: int = 0):
        df_len = df_dict.__len__()
        if not df_len: return {}  # faulty_lines_exceptions_dict

        first_row: model = model(**df_dict[0])
        try:  # insert 1st line
            self.session.add(first_row)
            self.session.commit()

        except Exception as add_line_error:
            self.session.rollback()  # & self.session.flush() ?
            prime_key_name, prime_key_val = get_prime_key(model, first_row)
            self.faulty_lines_exceptions_dict[str(prime_key_val)] = (first_row, add_line_error)
            self.logger.error(f'In \'{model.__name__}\' entry with \'{prime_key_name}\' key value: {prime_key_val}.')
            self.logger.debug(f'\t{add_line_error.args[0]}\n\t\tFull Entry: {first_row}\n')
            # self.logger.debug(f'{add_line_error}')

        half_len = int(df_len / 2)

        try:  # insert whole df
            self.session.bulk_insert_mappings(model, df_dict[1:])
            self.session.commit()  # & self.session.rollback() ?

        except:
            # except Exception as e_bulk_insert:
            # self.logger.debug(f'{e_bulk_insert.args[0]}')
            self.session.rollback()  # self.session.flush()
            # smaller chunks
            self.exclude_faulty_lines(model, df_dict[1:half_len + 1], i0 + 1)  # 1st half of data
            self.exclude_faulty_lines(model, df_dict[half_len + 1:], half_len + 1)  # 2nd half of data

        # finally:
        #     self.session.rollback()


if __name__ == '__main__':
    ctx = create_app().app_context()
    ctx.push()

    DBMigration().load_full_db()  # Load all CSV files to the DB

    ctx.pop()
    print(f'Fin!')
