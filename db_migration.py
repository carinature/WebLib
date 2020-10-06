from flask import current_app as app
from sqlalchemy import create_engine

from app import create_app
from app.models import *

import pandas as pd
import numpy as np
from sqlalchemy.orm import sessionmaker, Query

from time import time


def csv_to_mysql():  # todo consider NOT using try

    # Create engine
    engine = db.engine  # todo or?
    # with app.app_context():
    #     engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

    # Create All Tables
    Base.metadata.create_all(engine)  # todo or? db.create_all(engine)

    # Create the session
    Session = sessionmaker(bind=engine)
    session = Session()  # todo or? session = scoped_session(Session())

    t = time()

    # try:
    # models = Base.__subclasses__()
    # for model in models:
    for model in [TextSubject]:
        for src_file in model.src_scv:
            with open(src_file) as csv_file:
                for dataframe in pd.read_csv(csv_file,
                                             dtype=model.dtype_dic_csv2py,
                                             header=0,
                                             names=model.col_names,
                                             chunksize=app.config['CHUNK_SIZE_DB']
                                             ):
                    # next line is to handle cases of empty cell (e.g when val,val,,val in csv file
                    df_nonone = dataframe.replace(np.nan, '', regex=True)
                    try:
                        session.bulk_insert_mappings(model, df_nonone.to_dict(orient='records'))
                        # todo the next two is another good WORKING option - find out which of the 3 is faster
                        # db.engine.execute(model.__table__.insert(), df_nonone.to_dict('records'))
                        # dataframe.to_sql(name=model.__tablename__, con=engine, if_exists='replace', index=False,
                        #                  index_label='book_bibliographic_info', dtype=dtype_dic_py2sql)
                        session.commit()
                        if TextSubject == model:
                            sunject_list = session.query(TextSubject).all()
                            for row in sunject_list:
                                # print(row)
                                # print(row.C)
                                csum = 0
                                clist = str(row.C).split(',')
                                # print('clist')
                                # print(clist)
                                for c in clist:
                                    cc = c.split('-')
                                    # print('cc')
                                    # print(cc)
                                    if 2 == len(cc):
                                        csum += int(cc[1]) - int(cc[0])
                                    csum += 1
                                row.Csum = csum
                        session.commit()
                    except Exception as e:
                        print('~'*5, ' In model << ', model, ' >> ', '~'*5)
                        print('Error: {}'.format(str(e)))
                        print(dataframe)
    session.close()

    # except Exception as e:
    #     print('Error: {}'.format(str(e)))
    #     # s.rollback()  # Rollback the changes on error
    # finally:
    #     session.close()
    print("Time elapsed: " + str(time() - t) + " s.")


if __name__ == '__main__':
    # Load all CSV files to the DB
    app = create_app()
    ctx = app.app_context()
    ctx.push()
    csv_to_mysql()
    ctx.pop()

# printout:
#     /home/fares/.virtualenvs/WebLib/bin/python /home/fares/PycharmProjects/WebLib/utilities/db_migration.py
#     Time elapsed: 243.15527486801147 s.
#
#     Process finished with exit code 0