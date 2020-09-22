from flask import current_app as app
from app.models import *

import pandas as pd
import numpy as np
from sqlalchemy.orm import sessionmaker

from time import time


def csv_to_mysql():  # todo consider NOT using try

    # Create engine
    engine = db.engine  # todo or? engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=False, pool_recycle=3600)

    # Create All Tables
    Base.metadata.create_all(engine)  # todo or? db.create_all(engine)

    # Create the session
    Session = sessionmaker(bind=engine)
    session = Session()  # todo or? session = scoped_session(Session())

    t = time()

    # try:
    models = Base.__subclasses__()
    for model in models:
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

# printout:
#     /home/fares/.virtualenvs/WebLib/bin/python /home/fares/PycharmProjects/WebLib/utilities/db_migration.py
#     Time elapsed: 243.15527486801147 s.
#
#     Process finished with exit code 0
