import pandas as pd
import sqlalchemy

from flask_app import db
import numpy as np

from utilities.models import *
from properties import SQLALCHEMY_DATABASE_URI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def csv_to_mysql(): #todo consider NOT using try
    try:
        models = Base.__subclasses__()  # fixme change to generic list (use Metadate...?)
        for model in models:
            for src_file in model.src_scv:
                with open(src_file) as csv_file:
                    dataframe = pd.read_csv(csv_file, header=0, dtype=model.dtype_dic_csv2py)
                    df_nonone = dataframe.replace(np.nan, '',
                                                  regex=True)  # to handle cases of empty cell (e.g when val,val,,val in csv file
                    session.bulk_insert_mappings(model, df_nonone.to_dict(orient='records'))
                    session.commit()
                    # todo the next two is another good WORKING option - find out which of the 3 is faster
                    # db.engine.execute(model.__table__.insert(), df_nonone.to_dict('records'))
                    # dataframe.to_sql(name=model.__tablename__, con=engine, if_exists='replace', index=False,
                    #                  index_label='book_bibliographic_info', dtype=dtype_dic_py2sql)
    except Exception as e:
        print('Error: {}'.format(str(e)))

    finally:
        session.close()


if __name__ == '__main__':

    # Create engine
    engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=False)
    # engine = db.engine

    # Create All Tables
    Base.metadata.create_all(engine)

    # Create the session
    Session = sessionmaker(bind=engine)
    session = Session()

    # Load all CSV files to the DB
    csv_to_mysql()

    # t = time()
    #
    # # Create the database
    # engine = create_engine('sqlite:///csv_test.db')
    # Base.metadata.create_all(engine)
    #
    # # Create the session
    # session = sessionmaker()
    # session.configure(bind=engine)
    # s = session()
    #
    # try:
    #     file_name = "t.csv"  # sample CSV file used:  http://www.google.com/finance/historical?q=NYSE%3AT&ei=W4ikVam8LYWjmAGjhoHACw&output=csv
    #     data = Load_Data(file_name)
    #
    #     for i in data:
    #         record = Price_History(**{
    #             'date': datetime.strptime(i[0], '%d-%b-%y').date(),
    #             'opn': i[1],
    #             'hi': i[2],
    #             'lo': i[3],
    #             'close': i[4],
    #             'vol': i[5]
    #         })
    #         s.add(record)  # Add all the records
    #
    #     s.commit()  # Attempt to commit all the records
    # except:
    #     s.rollback()  # Rollback the changes on error
    # finally:
    #     s.close()  # Close the connection
    # print
    # "Time elapsed: " + str(time() - t) + " s."
