import pandas as pd
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

    textsa_files = [
        '../raw_data/textsa2.csv',
        '../raw_data/textsa5.csv',
        '../raw_data/textsa3.csv',
        '../raw_data/textsa19.csv',
    ]
    csv_to_mysql(
        csv_file_path=textsa_files[0],
        table_name='textsa',
        engine=engine,
        if_exists='append',
    )

    titlesa = '../raw_data/titlesa.csv'
    csv_to_mysql(
        csv_file_path=titlesa,
        table_name='titlesa',
        engine=engine,
        if_exists='replace',
    )

    texts_subjects = '../raw_data/texts_subjects2.csv'
    csv_to_mysql(
        csv_file_path=texts_subjects,
        table_name='texts_subjects',
        engine=engine,
        if_exists='replace',
    )

    book_references = '../raw_data/bookreferences2.csv'
    csv_to_mysql(
        csv_file_path=book_references,
        table_name='book_references',
        engine=engine,
        if_exists='replace',
    )

    t = time()

    #Create the database
    engine = create_engine('sqlite:///csv_test.db')
    Base.metadata.create_all(engine)

    #Create the session
    session = sessionmaker()
    session.configure(bind=engine)
    s = session()

    try:
        file_name = "t.csv" #sample CSV file used:  http://www.google.com/finance/historical?q=NYSE%3AT&ei=W4ikVam8LYWjmAGjhoHACw&output=csv
        data = Load_Data(file_name)

        for i in data:
            record = Price_History(**{
                'date' : datetime.strptime(i[0], '%d-%b-%y').date(),
                'opn' : i[1],
                'hi' : i[2],
                'lo' : i[3],
                'close' : i[4],
                'vol' : i[5]
            })
            s.add(record) #Add all the records

        s.commit() #Attempt to commit all the records
    except:
        s.rollback() #Rollback the changes on error
    finally:
        s.close() #Close the connection
    print "Time elapsed: " + str(time() - t) + " s."