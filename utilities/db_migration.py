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
