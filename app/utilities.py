from typing import Dict

from flask_wtf import FlaskForm

from . import forms
from . import models

from flask import request


def init_search_bar() -> Dict[str, FlaskForm]:
    return {'subject_form': forms.SearchSubject(request.form),
            'reference_form': forms.SearchReference(request.form),
            'filter_form': forms.FilterForm(request.form),
            'radio_buttons': forms.SearchTypeChoice(request.form)}


# count the references in a row
import math
from typing import Tuple


def c_sum(row):
    csum = 0
    clist = str(row.C).split(',')
    for c in clist:
        cc = c.split('-')
        if 2 == len(cc):
            csum += int(cc[1]) - int(cc[0])
        csum += 1
    return csum


###################################################################

import pandas as pd
from sqlalchemy.orm import sessionmaker

from app import create_app

from app.models import *

from sqlalchemy import create_engine, inspect, sql
import numpy as np

app = create_app()
faulty_lines_exceptions_dict: Dict[str, Tuple[Base, Exception]] = {}
model: Base = TextText

import logging

time_n_date = 'TODO SET TIME AND DATE'
LOGGING_FILE = 'db_migration.log'
logging.basicConfig(filename=LOGGING_FILE,
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',  # todo change, use as template
                    datefmt='%H:%M:%S',
                    level=logging.INFO)
logging.info(f'DB migration - {time_n_date}')


# # OPTION B
# 
# # create logger with 'spam_application'
# logger = logging.getLogger('spam_application')
# logger.setLevel(logging.DEBUG)
# # create file handler which logs even debug messages
# fh = logging.FileHandler(LOGGING_FILE)
# fh.setLevel(logging.DEBUG)
# logger.addHandler(fh)


# logs faulty lines into the file and return the str
def log_faulty_line(faulty_line: model,
                    exception: Exception,
                    prime_key_name: str = inspect(model).primary_key[0].name,
                    file: str = 'db_migration_log.txt'):  # file:TextIOWrapper='db_migration_log.txt'):
    prime_key_val = str(faulty_line.__dict__[prime_key_name])
    massage = f'\n{prime_key_name}  -  {prime_key_val}: ' \
              f'\n\tEntry: {faulty_line}' \
              f'\n\tError: {exception}'  # .args[0]}'
    print(massage)  # fixme # file.write(massage)
    # logging.info
    return massage


# def log_faulty_lines(rows_dict, file='db_migration_log.txt'):
#     for prime_key_val, faulty_line in rows_dict.items():
#         print(log_faulty_line(faulty_line[0], faulty_line[1], prime_key_name, file))


# Finds the line in the data that throws exception during bulk_insert_mapping on data.
# Recursivly attemps to insert smaller chunks of data until finds a faulty line.
#   Recieves:
#       df_dict - a pd.DataFrame.to_dict(orient='records')
#       i0 - #line in the current chunk of data - for logging (so you can remove)
#   Return exceptions_dict (type Dict[str, Tuple[Base, Exception]])
def exclude_faulty_lines(df_dict: collections.abc.Mapping, i0: int = 0) -> Dict[str, Tuple[Base, Exception]]:
    df_len = df_dict.__len__()
    if not df_len: return {}  # faulty_lines_exceptions_dict

    first_row: model = model(**df_dict[0])
    try:  # insert 1st line
        session.add(first_row)
        session.commit()

    except Exception as add_line_error:
        session.rollback()  # & session.flush() ?
        prime_key_val = str(first_row.__dict__[prime_key_name])
        faulty_lines_exceptions_dict[str(prime_key_val)] = (first_row, add_line_error)
        log_faulty_line(first_row, add_line_error, prime_key_name)

    half_len = int(df_len / 2)

    try:  # insert whole df
        session.bulk_insert_mappings(model, df_dict[1:])
        session.commit()  # & session.rollback() ?

    except Exception as e_bulk_insert:
        # print(f'\t(Exception thrown) Bad line in chunk ({int(math.log((CHUNK_SIZE / df_len), 2))} sub-chunk)'
        #       f' - Trying smaller data chunks, size: {half_len}')  # print(e_bulk_insert)
        session.rollback()  # session.flush()

        # smaller chunks
        # 1st half of data
        exceptions_dict_1st_half = exclude_faulty_lines(df_dict[1:half_len + 1], i0 + 1)

        # fixme check if there is actually a second half
        #  - like in the case of array of size 2:
        #  you check the 1st row,
        #  then the 1st half after her, which in this case is the 2nd line
        #  and then you move to the 3rd row (only it doesn't exists)
        # todo you can do the len check here - and return statement
        #  or in the beginning of find row - and then you call the next line but exit imidiatly
        #       and then you can also remove the other if (1>=def line return NOLINE

        # 2nd half of data
        exceptions_dict_2nd_half = exclude_faulty_lines(df_dict[half_len + 1:], half_len + 1)
        # todo merge faulty_lines_exceptions_dict  # return exclude_faulty_lines

    # finally:
    #     session.rollback()

    return faulty_lines_exceptions_dict
    # return exceptions_dict_ 2nd _half   +   exceptions_dict_ 2nd _half


if '__main__' == __name__:
    ctx = app.app_context()
    ctx.push()
    engine = db.engine  # todo or? # with app.app_context(): engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    Base.metadata.create_all(engine)  # todo or? db.create_all(engine)
    session = sessionmaker(bind=engine)()  # todo or? session = scoped_session(Session())

    CHUNK_SIZE = app.config['CHUNK_SIZE_DB']  # todo sould be app.config['chunk..']
    prime_key_name = inspect(model).primary_key[0].name

    chunk_num = 0
    exit_flag = False

    while not exit_flag:
        try:  # this for-loop is inside `try` for cases of commas (`,`) in `subject` col without brackets (`"`)
            for df in pd.read_csv(model.src_scv[0],
                                  dtype=model.dtype_dic_csv2py,
                                  header=0,
                                  names=model.col_names,
                                  na_values=['x', '#VALUE!', 'Unknown', ''],
                                  chunksize=CHUNK_SIZE,
                                  skiprows=CHUNK_SIZE * chunk_num,  # DONT REMOVE this - for cases of read exceptions
                                  # nrows=CHUNK_SIZE,
                                  ):
                print(f'Data chunk number #{chunk_num}', end=" ")
                df_clean: pd.DataFrame = df.drop_duplicates(prime_key_name)
                df_clean = df_clean.replace(np.nan, None)

                numeric_cols = [col1.name for col1 in model.__table__.c if isinstance(col1.type, sql.sqltypes.Integer)]
                for col in numeric_cols:
                    if 'Csum' != col: df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')

                df_clean = df_clean.astype(object).where(pd.notnull(df_clean), None)  # this is explained in:
                # https://stackoverflow.com/questions/45395729/unknown-column-nan-in-field-list-python-pandas
                try:
                    session.bulk_insert_mappings(model, df_clean.to_dict(orient='records'))
                    session.commit()  # raises an Exception
                except Exception as e:  # todo catch different kinds of exceptions
                    session.rollback()  # session.flush()
                    faulty_lines_exceptions_dict = exclude_faulty_lines(df_clean.to_dict(orient='records'))
                finally:
                    print(f' - Finshed')
                    chunk_num += 1

            exit_flag = True

        except Exception as e_read_csv:
            print(f'{e_read_csv.args[0]}')
            print(f'{e_read_csv}')
            print(f'\nNote: The whole chunk #{chunk_num} was not inserted!\n')
            #     TypeError: Cannot cast array data from dtype('O') to dtype('float64') according to the rule 'safe'
            # ValueError: could not convert string to float: ' 155 n. 6'
            chunk_num += 1  # todo this might cause a problem (or skipping chunks)
            exit_flag = False

    if faulty_lines_exceptions_dict:  # todo log into a file
        print(f'Bad News:')
        print(f'There are {faulty_lines_exceptions_dict.__len__()} faulty lines in the source data')
        print(f'Check Out the log file ({LOGGING_FILE})')
        # log_faulty_lines(faulty_lines_exceptions_dict)

    else: print(f'Everything is fine and dandy')

    ctx.pop()
