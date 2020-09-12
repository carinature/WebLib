
import pandas as pd
import numpy as np
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from flask_app import db

from utilities.models import *
from properties import SQLALCHEMY_DATABASE_URI

from time import time


def csv_to_mysql():  # todo consider NOT using try

    # Create engine
    # engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=False, pool_recycle=3600)
    engine = db.engine
    # engine = db.engine

    # Create All Tables
    Base.metadata.create_all(engine)

    # Create the session
    Session = sessionmaker(bind=engine)
    session = Session()
    # session = scoped_session(Session())

    t = time()


    # try:
    # models = Base.__subclasses__()
    models = [TextText]
    for model in models:
        for src_file in model.src_scv:
            with open(src_file) as csv_file:
                for dataframe in pd.read_csv(csv_file,
                                        dtype=model.dtype_dic_csv2py,
                                        header=0,
                                        names=model.col_names,
                                        chunksize=1000
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
                    except Exception as e:
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
    csv_to_mysql()
