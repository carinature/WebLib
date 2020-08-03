import pymysql
import pandas as pd
import sys
from sqlalchemy import create_engine


def csv_to_mysql(load_sql, host, user, password):
    '''
    This function load a csv file to MySQL table according to
    the load_sql statement.
    '''
    engine = create_engine("mysql+pymysql://{user}:{pw}@moblid.mysql.pythonanywhere-services.com/{db}"
                       .format(user="moblid",
                               pw="s4MYP9KSyYkZ6B6",
                               db="moblid$default"))

    try:
        textsa = pd.read_csv("/home/moblid/mysite/textsa19.csv", encoding='utf-8')
        titlesa = pd.read_csv("/home/moblid/mysite/titlesa.csv", encoding='utf-8')
        texts_subjects = pd.read_csv("/home/moblid/mysite/texts_subjects2.csv", encoding='utf-8')
        textsa.index.name = 'indexa'
        titlesa.index.name = 'indexa'
        texts_subjects.index.name = 'indexa'

        #allsef = pd.read_csv("/home/moblid/mysite/all_sefaria.csv", encoding='utf-8',dtype={'ref': str})
        #allsef.to_sql('fulltexts', if_exists = 'replace', con = engine, chunksize = 1000)
        textsa.to_sql('textsa', if_exists = 'append', con = engine, chunksize = 1000)
        titlesa.to_sql('titlesa', if_exists = 'replace', con = engine, chunksize = 1000)
        texts_subjects.to_sql('texts_subjects', if_exists = 'replace', con = engine, chunksize = 1000)

        print('Connected to DB: {}'.format(host))
        print('Succuessfully loaded the table from csv1.')
    except Exception as e:
        print('Error: {}'.format(str(e)))
        sys.exit(1)


def csv_to_mysql2(load_sql, host, user, password):
    '''
    This function load a csv file to MySQL table according to
    the load_sql statement.
    '''
    engine = create_engine("mysql+pymysql://{user}:{pw}@moblid.mysql.pythonanywhere-services.com/{db}"
                       .format(user="moblid",
                               pw="s4MYP9KSyYkZ6B6",
                               db="moblid$default"))

    try:
        textsa = pd.read_csv("/home/moblid/mysite/textsa2.csv", encoding='utf-8')
        textsa.index.name = 'indexa'
        textsa.to_sql('textsa', if_exists = 'append', con = engine, chunksize = 1000)

        print('Connected to DB: {}'.format(host))
        print('Succuessfully loaded the table from csv2.')

    except Exception as e:
        print('Error: {}'.format(str(e)))
        sys.exit(1)

def csv_to_mysql3(load_sql, host, user, password):
    '''
    This function load a csv file to MySQL table according to
    the load_sql statement.
    '''
    engine = create_engine("mysql+pymysql://{user}:{pw}@moblid.mysql.pythonanywhere-services.com/{db}"
                       .format(user="moblid",
                               pw="s4MYP9KSyYkZ6B6",
                               db="moblid$default"))

    try:
        textsa = pd.read_csv("/home/moblid/mysite/textsa3.csv", encoding='utf-8')
        textsa.index.name = 'indexa'
        textsa.to_sql('textsa', if_exists = 'append', con = engine, chunksize = 1000)

        print('Connected to DB: {}'.format(host))
        print('Succuessfully loaded the table from csv3.')

    except Exception as e:
        print('Error: {}'.format(str(e)))
        sys.exit(1)

def csv_to_mysql5(load_sql, host, user, password):
    '''
    This function load a csv file to MySQL table according to
    the load_sql statement.
    '''
    engine = create_engine("mysql+pymysql://{user}:{pw}@moblid.mysql.pythonanywhere-services.com/{db}"
                       .format(user="moblid",
                               pw="s4MYP9KSyYkZ6B6",
                               db="moblid$default"))

    try:
        textsa = pd.read_csv("/home/moblid/mysite/textsa5.csv", encoding='utf-8')
        textsa.index.name = 'indexa'
        textsa.to_sql('textsa', if_exists = 'append', con = engine, chunksize = 1000)

        print('Connected to DB: {}'.format(host))
        print('Succuessfully loaded the table from csv5.')

    except Exception as e:
        print('Error: {}'.format(str(e)))
        sys.exit(1)

if __name__=="__main__":
    list_dirs = ["/home/moblid/mysite/"]

    for file in list_dirs:
        table_name = file.split("/")[-1].split(".")[0]
        load_sql = """LOAD DATA LOCAL INFILE {} INTO TABLE {} FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"'
        LINES TERMINATED BY '\n'
        IGNORE 1 LINES;""".format(file,table_name)
        host = 'moblid.mysql.pythonanywhere-services.com'
        user = 'moblid'
        password = 's4MYP9KSyYkZ6B6'
        csv_to_mysql(load_sql, host, user, password)
        #csv_to_mysql2(load_sql, host, user, password)
        #csv_to_mysql3(load_sql, host, user, password)
        #csv_to_mysql5(load_sql, host, user, password)