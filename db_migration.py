import random

from flask import current_app as app
from sqlalchemy import create_engine, inspect, sql

from app import create_app
from app.models import *
from app.utilities import c_sum

import pandas as pd
import numpy as np
from sqlalchemy.orm import sessionmaker, Query

from time import time


def csv_to_mysql():
    print('csv_to_mysql()')
    engine = db.engine  # todo or?    # with app.app_context(): engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    Base.metadata.create_all(engine)  # todo or? db.create_all(engine)
    session = sessionmaker(bind=engine)()  # todo or? session = scoped_session(Session())

    t_total = time()  # for logging
    with open('flask_python_log.txt', 'a') as f:
        f.writelines('\n=' * 55 + str(time()))

    # models = Base.__subclasses__()
    # models: List[Base.__subclasses__()] = [BookRef, Title, TextSubject] #, TextText]
    # models = [BookRef]
    # models = [TextSubject]
    # models = [Title]
    models = [TextText]
    model: Base.__subclasses__()
    for model in models:
        t_per_model = time()
        for src_file in model.src_scv:
            t_per_src = time()
            with open(src_file) as csv_file:
                dataframe: pd.DataFrame
                # todo remove next 3 lines -----------------------------------------------
                # n = sum(1 for line in csv_file) - 1  # number of records in file (excludes header)
                # s = 10000  # desired sample size
                # skip = sorted(
                #     random.sample(range(1, n + 1), n - s))  # the 0-indexed header will not be included in the skip list
                #  --------------------------------------------------------------------------------
                for dataframe in pd.read_csv(csv_file,
                                             dtype=model.dtype_dic_csv2py,
                                             header=0,
                                             names=model.col_names,
                                             chunksize=app.config['CHUNK_SIZE_DB'],
                                             na_values=['x', '#VALUE!', '', 'Unknown'],
                                             # todo consider striping the brackets (qoutation marks regular & special)
                                             # skiprows=skip #todo remove
                                             ):
                    try:
                        prime_key = inspect(model).primary_key[0].name
                        df_clean: pd.DataFrame = dataframe.drop_duplicates(prime_key)
                        df_clean = df_clean.replace(np.nan, '')  # , regex=True)
                        if TextSubject == model:
                            session.bulk_insert_mappings(model, df_clean.to_dict(orient='records'))  # session.commit()
                            # NOTE: dont use (raises timeout exception (slower?)) subject_list = TextSubject.query.all()
                            subject_list = session.query(TextSubject).all()
                            for row in subject_list:
                                row.Csum = c_sum(row)  # Add the `Csum` (#references) column
                        else:
                            # handle numeric (int) columns (centend, centstart, number, biblio)
                            numeric_cols = [col.name for col in model.__table__.c if
                                            isinstance(col.type, sql.sqltypes.Integer)]
                            for col in numeric_cols:
                                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce', downcast='unsigned')
                                df_clean[col] = df_clean[col].where(pd.notnull(df_clean[col]), None)
                                # df_clean[col] = df_clean[col].astype('Int64') #https://stackoverflow.com/questions/60377531/pandas-valueerror-integer-column-has-na-values-in-column-2
                                # df_clean = df_clean.replace(np.nan, sql.null())
                                # df_clean = df_clean.replace(np.nan, -21 if 'centend'==col else 21, regex=True)
                                # df_clean = df_clean.replace(None, 200)
                                # df_clean = df_clean.df.fillna(200)
                            # dataframe.to_sql(con=engine,
                            #                  if_exists='replace',
                            #                  name=model.__tablename__,
                            #                  index=False,
                            #                  # index_label='book_bibliographic_info',
                            #                  dtype=model.dtype_dic_py2sql)
                            session.bulk_insert_mappings(model, df_clean.to_dict(orient='records'))
                            # todo the next two is another good WORKING option - find out which of the 3 is faster
                            # db.engine.execute(model.__table__.insert(), df_clean.to_dict('records'))
                            # dataframe.to_sql(name=model.__tablename__, con=engine, if_exists='replace', index=False,
                            #                  index_label='book_bibliographic_info', dtype=dtype_dic_py2sql)
                        session.commit()

                    except Exception as e:
                        print('~' * 5 + ' In model ' + str(model) + '~' * 5)
                        print('Error: {}'.format(str(e)))
                        print(str(dataframe))
                        with open('flask_python_log.txt', 'a') as f:
                            f.writelines('~' * 5 + ' In model ' + str(model) + '~' * 5)
                            f.writelines('Error: {}'.format(str(e)))
                            f.writelines(dataframe)

            print('.' * 3 + ' SRC File ' + src_file + ' time: ' + str(time() - t_per_src) + ' s.')
            with open('flask_python_log.txt', 'a') as f:
                f.writelines('.' * 3 + ' SRC File ' + src_file + ' time: ' + str(time() - t_per_src) + ' s.')

        print('-' * 6 + '  Model ' + str(model) + ' time: ' + str(time() - t_per_model) + ' s.')
        with open('flask_python_log.txt', 'a') as f:
            f.writelines('-' * 6 + '  Model ' + str(model) + ' time: ' + str(time() - t_per_model) + ' s.\n')

    session.close()

    # except Exception as e:
    #     print('Error: {}'.format(str(e)))
    #     # s.rollback()  # Rollback the changes on error
    # finally:
    #     session.close()
    print('=' * 12 + ' Total Time elapsed: ' + str(time() - t_total) + ' s.')
    with open('flask_python_log.txt', 'a') as f:
        f.writelines('=' * 12 + ' Total Time elapsed: ' + str(time() - t_total) + ' s.')
        f.writelines('=' * 55)


if __name__ == '__main__':
    # Load all CSV files to the DB
    app = create_app()
    ctx = app.app_context()
    ctx.push()
    csv_to_mysql()
    ctx.pop()
    # textsfiles = [textsfile
    #               for textsfile in os.listdir(RAW_DATA_DIR)
    #               if textsfile.startswith('title')]
    # textsfiles = [textsfile for textsfile in os.listdir(RAW_DATA_DIR) if textsfile.startswith('bookreferences')]
    # filename = f'{RAW_DATA_DIR}/{textsfiles[0]}'
    # csv_clean_up(filename)

# printout:
#     /home/fares/.virtualenvs/WebLib/bin/python /home/fares/PycharmProjects/WebLib/utilities/db_migration.py
#     Time elapsed: 243.15527486801147 s.
#
#     Process finished with exit code 0
