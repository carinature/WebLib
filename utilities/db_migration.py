import pandas as pd
import sqlalchemy

from flask_app import db


def csv_to_mysql(csv_file_path, table_name, engine, if_exists='append'):
    try:
        loaded_csv = pd.read_csv(csv_file_path, encoding='utf-8')
        loaded_csv.index.name = 'indexa'
        loaded_csv.to_sql(table_name, if_exists=if_exists, con=engine, chunksize=1000)
    except Exception as e:
        print('Error: {}'.format(str(e)))


if __name__ == '__main__':
    engine = db.engine

    # textsa_files = [
    #     '../raw_data/textsa2.csv',
    #     '../raw_data/textsa5.csv',
    #     '../raw_data/textsa3.csv',
    #     '../raw_data/textsa19.csv',
    # ]
    # csv_to_mysql(
    #     csv_file_path=textsa_files[0],
    #     table_name='textsa',
    #     engine=engine,
    #     if_exists='append',
    # )
    #
    # titlesa = '../raw_data/titlesa.csv'
    # csv_to_mysql(
    #     csv_file_path=titlesa,
    #     table_name='titlesa',
    #     engine=engine,
    #     if_exists='replace',
    # )
    #
    # texts_subjects = '../raw_data/texts_subjects2.csv'
    # csv_to_mysql(
    #     csv_file_path=texts_subjects,
    #     table_name='texts_subjects',
    #     engine=engine,
    #     if_exists='replace',
    # )
    #
    # book_references = '../raw_data/bookreferences2.csv'
    # csv_to_mysql(
    #     csv_file_path=book_references,
    #     table_name='book_references',
    #     engine=engine,
    #     if_exists='replace',
    # )

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

from utilities.models import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Create engine
engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=False)

# Create All Tables
Base.metadata.create_all(engine)

# Create the session
Session = sessionmaker(bind=engine)
session = Session()

# from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy.types import Integer, String, Text, DateTime, Float, Boolean, PickleType

import numpy as np

# models = [BookRef]  # , TextSubject, TextText] #fixme change to generic list (use Metadate...?)
models = [BookRef, Title, TextSubject, TextText] #fixme change to generic list (use Metadate...?)
for model in models:
    for src_file in model.src_scv:
        with open(src_file) as csv_file:
            #     # dataframe = pd.read_csv(file, usecols=['file', 'titleref'])[['titleref', 'file']]  # , 'gcode'])
            #     # dataframe = pd.read_csv(csv_file, header=0, names=['kaka', 'pipi'])[['pipi', 'kaka']]
            #     dataframe = pd.read_csv(csv_file, header=0, dtype=dtype_dic_csv2py) #dtype=BookRef)
            # dataframe = pd.read_csv(csv_file)
            # todo consider this option
            dataframe = pd.read_csv(csv_file, header=0, dtype=model.dtype_dic_csv2py)  # dtype=BookRef)
            # dataframe.fillna('non')
            # db.engine.execute(model.__table__.insert(), dataframe.to_dict('records'))

            df_nonone = dataframe.replace(np.nan, '', regex=True) # to handle cases of empty cell (e.g when val,val,,val in csv file
            # db.engine.execute(model.__table__.insert(), df_nonone.to_dict('records'))
#             # todo the next one is anpther good WORKING option - find out which of the 2 (or 3) is faster
#             # dataframe.to_sql(name=model.__tablename__, con=engine, if_exists='replace', index=False,
#             #                  index_label='book_bibliographic_info', dtype=dtype_dic_py2sql) #this one workd! dont delte
#             # fixme the next one should be the best option but it doesn't work. WHY??
            session.bulk_insert_mappings(model, df_nonone.to_dict(orient='records'))  # should work but doesnt. why?! dont delete
            # session.bulk_insert_mappings(model, dataframe.to_dict(orient='records'))  # should work but doesnt. why?! dont delete
#             # new_mapper = sqlalchemy.orm.mapper(model, local_table=model.__table__, non_primary=True)  # should work but doesnt
#             # session.bulk_insert_mappings(new_mapper, dataframe.to_dict('records'))  # should work but doesnt. why?! dont delete
            session.commit()
session.close()

# for DBG
# print('~~~~~~~~~~~~')
# print(dataframe.to_dict('records'))
# print('===============')
# print(dataframe.to_dict('index'))
# print('******************')
# print(dataframe.to_dict())
