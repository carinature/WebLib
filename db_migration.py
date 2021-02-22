from flask import current_app as app
from sqlalchemy import create_engine

from app import create_app
from app.models import *

import pandas as pd
import numpy as np
from sqlalchemy.orm import sessionmaker, Query

from time import time


def csv_to_mysql():
    print('csv_to_mysql()')
    # Create engine
    engine = db.engine  # todo or?    # with app.app_context(): engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    # Create All Tables
    Base.metadata.create_all(engine)  # todo or? db.create_all(engine)
    # Create the session
    Session = sessionmaker(bind=engine)
    session = Session()  # todo or? session = scoped_session(Session())

    t_total = time()
    with open('flask_python_log.txt', 'a') as f:
        f.write('\n')
        f.write('\n')
        f.write("=" * 55 + str(time()))
        f.write('\n')

    # try:
    # models = Base.__subclasses__()
    # models = [BookRef, Title, TextSubject, TextText]
    # models = [BookRef]
    # models = [Title]
    # models = [TextText]
    models = [TextSubject]
    for model in models:
        t_per_model = time()
        for src_file in model.src_scv:
            t_per_src = time()
            with open(src_file) as csv_file:
                for dataframe in pd.read_csv(csv_file,
                                             dtype=model.dtype_dic_csv2py,
                                             header=0,
                                             names=model.col_names,
                                             chunksize=app.config['CHUNK_SIZE_DB'],
                                             # converters={'number': int},
                                             na_values=['x', '#VALUE!', '']
                                             # todo consider striping the brackets (qoutation marks regular & special)
                                             ):
                    # next line is to handle cases of empty cell (e.g when val,val,,val in csv file
                    df_nonone = dataframe.replace(np.nan, '', regex=True)
                    # df_nonone = dataframe.where((pd.notnull(dataframe)), None)
                    # # df_nonone = dataframe
                    # df_nonone['number'] = pd.to_numeric(df_nonone['number'], errors='coerce')
                    # df_nonone = df_nonone.dropna(subset=['number'])
                    # df_nonone['number'] = df_nonone['number'].astype(int)
                    try:
                        session.bulk_insert_mappings(model, df_nonone.to_dict(orient='records'))
                        # todo the next two is another good WORKING option - find out which of the 3 is faster
                        # db.engine.execute(model.__table__.insert(), df_nonone.to_dict('records'))
                        # dataframe.to_sql(name=model.__tablename__, con=engine, if_exists='replace', index=False,
                        #                  index_label='book_bibliographic_info', dtype=dtype_dic_py2sql)
                        session.commit()
                        # in TextSubject table add the Csum (#references) column
                        if TextSubject == model:
                            sunject_list = session.query(TextSubject).all()
                            # i=0
                            for row in sunject_list:
                                # i+=1
                                csum = 0
                                clist = str(row.C).split(',')
                                for c in clist:
                                    cc = c.split('-')
                                    # print('-- ', i, ' -- ' , cc)
                                    if 2 == len(cc):
                                        csum += int(cc[1]) - int(cc[0])
                                    csum += 1
                                row.Csum = csum
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
                f.write('.' * 3 + ' SRC File ' + src_file + ' time: ' + str(time() - t_per_src) + ' s.')
                f.write('\n')

        print('-' * 6 + '  Model ' + str(model) + ' time: ' + str(time() - t_per_model) + ' s.')
        with open('flask_python_log.txt', 'a') as f:
            f.write('-' * 6 + '  Model ' + str(model) + ' time: ' + str(time() - t_per_model) + ' s.')
            f.write('\n')
            f.write('\n')

    session.close()

    # except Exception as e:
    #     print('Error: {}'.format(str(e)))
    #     # s.rollback()  # Rollback the changes on error
    # finally:
    #     session.close()
    print('=' * 12 + ' Total Time elapsed: ' + str(time() - t_total) + ' s.')
    with open('flask_python_log.txt', 'a') as f:
        f.write('=' * 12 + ' Total Time elapsed: ' + str(time() - t_total) + ' s.')
        f.write('\n')
        f.write('=' * 55)
        f.write('\n')
        f.write('\n')


def csv_clean_up(filename):
    pass
    print('-' * 10, ' csv_clean_up ', '-' * 10)
    import csv

    def row_factory(row):
        return [x if x not in ('', 'x', '#VALUE!') else 'NaN' for x in row]

    # with open(filename, 'r', newline='') as f:
    with open(filename, 'r') as f, open('cleand.csv', 'wb') as csvfile:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            print(row_factory(row))
        # Using csv.writer() by default will not add these quotes to the entries.
        # In order to add them, we will have to use another optional parameter called quoting.
        # Let's take an example of how quoting can be used around the non-numeric values and ; as delimiters.
        # writer = csv.writer(file, quoting=csv.QUOTE_NONNUMERIC, delimiter=';')
        # filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        # filewriter.writerow(['Name', 'Profession'])
        # filewriter.writerow(['Derek', 'Software Developer'])
        # filewriter.writerow(['Steve', 'Software Developer'])
        # filewriter.writerow(['Paul', 'Manager'])


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
