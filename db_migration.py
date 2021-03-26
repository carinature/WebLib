from typing import Tuple

from flask import current_app as app
from sqlalchemy import create_engine, inspect, sql

from app import create_app
from app.models import *
from app.utilities import c_sum

import pandas as pd
import numpy as np
from sqlalchemy.orm import sessionmaker, Query

from time import time


# models: List[Base] = Base.__subclasses__()
# models: List[Base.__subclasses__()] = [BookRef, Title, TextSubject]  # , TextText]
# models = [BookRef]
# models = [TextSubject]
# models = [Title]
# models = [TextText]


class DBMigration:  # singleton class

    # models: List[Base] = Base.__subclasses__()
    models = [TextSubject]

    def __init__(self):
        engine = db.engine  # todo or?    # with app.app_context(): engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        Base.metadata.create_all(engine)  # todo or? db.create_all(engine)
        self.session = sessionmaker(bind=engine)()  # todo or    ? session = scoped_session(Session())
        self.CHUNK_SIZE = app.config['CHUNK_SIZE_DB']

        self.faulty_lines_exceptions_dict: Dict[str, Tuple[Base, Exception]] = {}

    # Finds the line in the data that throws exception during bulk_insert_mapping on data.
    # Recursivly attemps to insert smaller chunks of data until finds a faulty line.
    #   Recieves:
    #       df_dict - a pd.DataFrame.to_dict(orient='records')
    #       i0 - #line in the current chunk of data - for logging (so you can remove)
    #   Return exceptions_dict (type Dict[str, Tuple[Base, Exception]])
    def exclude_faulty_lines(self, model, df_dict: collections.abc.Mapping, i0: int = 0) -> Dict[
        str, Tuple[Base, Exception]]:
        df_len = df_dict.__len__()
        if not df_len: return {}  # faulty_lines_exceptions_dict

        first_row: model = model(**df_dict[0])
        # todo only take the columns that are part of the (final) model
        try:  # insert 1st line
            self.session.add(first_row)
            self.session.commit()

        except Exception as add_line_error:
            prime_key_name = inspect(model).primary_key[0].name
            self.session.rollback()  # & self.session.flush() ?
            prime_key_val = str(first_row.__dict__[prime_key_name])
            self.faulty_lines_exceptions_dict[str(prime_key_val)] = (first_row, add_line_error)
            # self.log_faulty_line(first_row, add_line_error, prime_key_name)

        half_len = int(df_len / 2)

        try:  # insert whole df
            self.session.bulk_insert_mappings(model, df_dict[1:])
            self.session.commit()  # & self.session.rollback() ?

        except Exception as e_bulk_insert:
            # print(f'\t(Exception thrown) Bad line in chunk ({int(math.log((CHUNK_SIZE / df_len), 2))} sub-chunk)'
            #       f' - Trying smaller data chunks, size: {half_len}')  # print(e_bulk_insert)
            self.session.rollback()  # self.session.flush()

            # smaller chunks
            # 1st half of data
            exceptions_dict_1st_half = self.exclude_faulty_lines(model, df_dict[1:half_len + 1], i0 + 1)

            # 2nd half of data
            exceptions_dict_2nd_half = self.exclude_faulty_lines(model, df_dict[half_len + 1:], half_len + 1)
            # todo merge faulty_lines_exceptions_dict  # return exclude_faulty_lines

        # finally:
        #     self.session.rollback()

        return self.faulty_lines_exceptions_dict
        # return exceptions_dict_ 2nd _half   +   exceptions_dict_ 2nd _half

    def load_full_db(self) -> Dict[str, Tuple[Base, Exception]]:
        t_total = time()  # for logging
        with open('flask_python_log.txt', 'a') as f:
            f.writelines('\n=' * 55 + str(time()))

        model: Base.__subclasses__()
        for model in self.models:
            t_per_model = time()

            self.load_single(model)
            # self.faulty_lines_exceptions_dict.update(self.load_single(model))
            #
            # print('-' * 6 + '  Model ' + str(model) + ' time: ' + str(time() - t_per_model) + ' s.')
            # with open('flask_python_log.txt', 'a') as f:
            #     f.writelines('-' * 6 + '  Model ' + str(model) + ' time: ' + str(time() - t_per_model) + ' s.\n')

            # except Exception as e:
            #     print('~' * 5 + ' In model ' + str(model) + '~' * 5)
            #     print(f'Error: {e}')
            #     print(str(dataframe))
            #
            #     with open('flask_python_log.txt', 'a') as f:
            #         f.writelines('~' * 5 + ' In model ' + str(model) + '~' * 5)
            #         f.writelines(f'Error: {e}')
            #         f.writelines(dataframe)

        self.session.close()  # todo where should this be? in load_single?
        #
        # print('=' * 12 + ' Total Time elapsed: ' + str(time() - t_total) + ' s.')
        # with open('flask_python_log.txt', 'a') as f:
        #     f.writelines('=' * 12 + ' Total Time elapsed: ' + str(time() - t_total) + ' s.')
        #     f.writelines('=' * 55)
        return self.faulty_lines_exceptions_dict

    def load_single(self, model) -> Dict[str, Tuple[Base, Exception]]:
        f_l_exc_dict: Dict[str, Tuple[Base, Exception]] = {}
        for src_file in model.src_scv:
            t_per_src = time()
            self.load_src_file(model, src_file)
            # f_l_exc_dict.update(self.load_src_file(model, src_file))
            # #   logging
            # print('.' * 3 + ' SRC File ' + src_file + ' time: ' + str(time() - t_per_src) + ' s.')
            # with open('flask_python_log.txt', 'a') as f:
            #     f.writelines('.' * 3 + ' SRC File ' + src_file + ' time: ' + str(time() - t_per_src) + ' s.')
            return f_l_exc_dict

    def load_src_file(self, model, src_file, LOGGING_FILE=None) -> Dict[str, Tuple[Base, Exception]]:
        prime_key_name = inspect(model).primary_key[0].name
        with open(src_file) as csv_file:
            chunk_num = 0
            exit_flag = False

            while not exit_flag:
                try:  # this for-loop is inside `try` for cases of commas (`,`) in `subject` col without brackets (`"`)

                    dataframe: pd.DataFrame
                    for dataframe in pd.read_csv(csv_file,
                                                 dtype=model.dtype_dic_csv2py,
                                                 header=0,
                                                 names=model.col_names,
                                                 na_values=['x', '#VALUE!', '', 'Unknown'],
                                                 chunksize=app.config['CHUNK_SIZE_DB'],
                                                 # fixme change back to app.config
                                                 # todo consider striping the brackets (qoutation marks regular & special)
                                                 # skiprows=skip  # todo remove
                                                 ):
                        df_clean: pd.DataFrame = dataframe[[col.key for col in model.__table__.c if 'Csum' != col.key]]
                        if TextSubject == model:
                            df_clean['Csum'] = df_clean['C'].apply(c_sum)
                        df_clean = df_clean.drop_duplicates(prime_key_name)
                        df_clean = df_clean.replace(np.nan, None)  # , regex=True)

                        # handle numeric (int) columns (centend, centstart, number, biblio)
                        numeric_cols = [col.name for col in model.__table__.c if
                                        isinstance(col.type, sql.sqltypes.Integer)]
                        for col in numeric_cols:
                            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')

                        df_clean = df_clean.astype(object).where(pd.notnull(df_clean), None)  # this is explained in:
                        # https://stackoverflow.com/questions/45395729/unknown-column-nan-in-field-list-python-pandas
                        try:
                            self.session.bulk_insert_mappings(model, df_clean.to_dict(orient='records'))
                            self.session.commit()  # raises an Exception if problem with data
                        except Exception as e:  # todo catch different kinds of exceptions
                            self.session.rollback()  # self.session.flush()
                            self.faulty_lines_exceptions_dict = self.exclude_faulty_lines(
                                    model,
                                    df_clean.to_dict(orient='records'))
                        finally:
                            # print(f' - Finshed')
                            chunk_num += 1

                    exit_flag = True

                except Exception as e_read_csv:
                    print(f'{e_read_csv.args[0]}')
                    print(f'{e_read_csv}')
                    print(f'\nNote: The whole chunk #{chunk_num} was not inserted!\n')
                    #     TypeError: Cannot cast array data from dtype('O') to dtype('float64') according to the rule 'safe'
                    # ValueError: could not convert string to float: ' 155 n. 6'
                    chunk_num += 1  # todo this might cause a problem (or skipping chunks)
                    exit_flag = False

        if self.faulty_lines_exceptions_dict:  # todo log into a file
            print(f'Bad News:')
            print(f'In {model}, file {src_file}, chunk #{chunk_num}')
            print(f'There are {self.faulty_lines_exceptions_dict.__len__()} faulty lines in the source data')
            print(f'Check Out the log file ({LOGGING_FILE})')
            # log_faulty_lines(faulty_lines_exceptions_dict)

        else: print(f'Everything is fine and dandy')

        return self.faulty_lines_exceptions_dict


if __name__ == '__main__':
    app = create_app()
    ctx = app.app_context()
    ctx.push()

    dbmigration = DBMigration()
    dbmigration.load_full_db()  # Load all CSV files to the DB
    print(f'Fin!')

    ctx.pop()
