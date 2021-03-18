# from typing import Dict
#
# from flask_wtf import FlaskForm
#
# from . import forms
# from . import models
#
# from flask import request
#
#
# def init_search_bar() -> Dict[str, FlaskForm]:
#     return {'subject_form': forms.SearchSubject(request.form),
#             'reference_form': forms.SearchReference(request.form),
#             'filter_form': forms.FilterForm(request.form),
#             'radio_buttons': forms.SearchTypeChoice(request.form)}


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

# csv_file = '/home/fares/PycharmProjects/WebLib/app/raw_data/bookreferences2.csv'


app = create_app()
faulty_lines_exceptions_dict: Dict[str, Tuple[Base, Exception]] = {}
model: Base = TextText


# logs faulty lines into the file and return the str
def log_faulty_line(faulty_line: model,
                    exception: Exception,
                    prime_key_name: str = inspect(model).primary_key[0].name,
                    file='db_migration_log.txt'):
    prime_key_val = str(faulty_line.__dict__[prime_key_name])
    massage = f'\'{prime_key_name}\' value {prime_key_val}: ' \
              f'\n\tEntry: {faulty_line}' \
              f'\n\tError: {exception}'  # .args[0]}'
    print(massage)  # todo # file.write(massage)
    # faulty_lines_exceptions_dict[prime_key_val] = (faulty_line, exception)
    return massage


def log_faulty_lines(rows_dict, file='db_migration_log.txt'):
    with open(file, 'a') as f:
        for key, faulty_line in rows_dict.items():
            print(log_faulty_line(key, faulty_line, f))


# Finds the line in the data that throws exception during bulk_insert_mapping on data.
# Recursivly attemps to insert smaller chunks of data until finds a faulty line.
#   Recieves:
#       df_dict - a pd.DataFrame.to_dict(orient='records')
#       i0 - #line in the current chunk of data - for logging (so you can remove)
#   Return exceptions_dict (type Dict[str, Tuple[Base, Exception]])
def exclude_faulty_lines(df_dict: collections.abc.Mapping, i0: int = 0) -> Dict[str, Tuple[Base, Exception]]:
    df_len = df_dict.__len__()
    if not df_len: return NO_LINE
    first_row: model = model(**df_dict[0])
    try:  # insert 1st line
        session.add(first_row)
        session.commit()

    except Exception as add_line_error:
        session.rollback()  # & session.flush() ?
        prime_key_name = inspect(model).primary_key[0].name
        prime_key_val = first_row.__dict__[prime_key_name]
        log_faulty_line(first_row, add_line_error, prime_key_name)
        faulty_lines_exceptions_dict[str(prime_key_val)] = (first_row, add_line_error)

    half_len = int(df_len / 2)

    try:  # insert whole df
        session.bulk_insert_mappings(model, df_dict[1:])
        session.commit()  # & session.rollback() ?
        # todo maybe return exceptions_dict (instead of using global)

    except Exception as e_bulk_insert:
        print(f'\t(Exception thrown) Bad line in chunk ({int(math.log((CHUNK_SIZE / df_len), 2))} sub-chunk)'
              f' - Trying smaller data chunks, size: {half_len}')  # print(e_bulk_insert)
        session.rollback()  # session.flush()

        # smaller chunks
        # 1st half of data
        # todo maybe should be returning an exceptions_dict
        exceptions_dict_1st_half = exclude_faulty_lines(df_dict[1:half_len + 1], i0 + 1)
        # todo merge exceptions_dicts

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
        # todo merge exceptions_dicts  # return exceptions_dicts

    # finally:
    #     session.rollback()

    # todo return exceptions_dict
    return NO_LINE


if '__main__' == __name__:
    ctx = app.app_context()
    ctx.push()
    engine = db.engine  # todo or? # with app.app_context(): engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    Base.metadata.create_all(engine)  # todo or? db.create_all(engine)
    session = sessionmaker(bind=engine)()  # todo or? session = scoped_session(Session())

    NO_LINE = -1  # todo move to utils?
    CHUNK_SIZE = 100  # todo sould be app.config['chunk..']
    prime_key = inspect(model).primary_key[0].name

    chunk_num = 5083
    exit_flag = False

    while not exit_flag:
        try:
            # this for-loop is inside `try` for cases of commas (`,`) in `subject` col without brackets (`"`)
            for df in pd.read_csv(model.src_scv[0],
                                  dtype=model.dtype_dic_csv2py,
                                  header=0,
                                  names=model.col_names,
                                  na_values=['x', '#VALUE!', 'Unknown', ''],
                                  chunksize=CHUNK_SIZE,
                                  # chunksize=app.config['CHUNK_SIZE_DB'],
                                  skiprows=CHUNK_SIZE * chunk_num,
                                  nrows=CHUNK_SIZE,
                                  ):
                print(f'Data chunk number #{chunk_num}', end=" ")
                df_clean: pd.DataFrame = df.drop_duplicates(prime_key)
                df_clean = df_clean.replace(np.nan, None)

                numeric_cols = [col1.name for col1 in model.__table__.c if isinstance(col1.type, sql.sqltypes.Integer)]
                for col in numeric_cols:
                    if 'Csum' != col:
                        df_clean[col] = pd.to_numeric(df_clean[col],
                                                      errors='coerce')  # ,downcast='integer' or 'unsigned')

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
                    chunk_num += 1  # todo this might cause a problem (or skipping chunks)
            exit_flag = True
        except Exception as e_read_csv:
            print(f'{e_read_csv.args[0]}')
            print(f'\nNote: The whole chunk #{chunk_num} was not inserted!\n')
            #     TypeError: Cannot cast array data from dtype('O') to dtype('float64') according to the rule 'safe'
            # ValueError: could not convert string to float: ' 155 n. 6'
            chunk_num += 1
            exit_flag = False

    if faulty_lines_exceptions_dict:  # todo log into a file
        print(f'Bad rows:')
        log_faulty_lines(faulty_lines_exceptions_dict)
    else: print(f'Everything is fine and dandy')

    ctx.pop()
