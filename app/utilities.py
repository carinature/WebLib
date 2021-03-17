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
exceptions_dict: Dict[str, Tuple[Base, Exception]] = {}


# Finds the line in the data that throws exception during bulk_insert_mapping on data
# return the number of the 1st problematic line, or -1 if no problem
# def find_row(df: pd.DataFrame , i0: int = 0, df_len: int = app.config['CHUNK_SIZE_DB']) -> int:
# todo find_row should return exceptions_dict (type Dict[str, Tuple[Base, Exception]])
def find_row(df_dict: collections.abc.Mapping, i0: int = 0, df_len: int = app.config['CHUNK_SIZE_DB']) -> int:
    first_row: model = model(**df_dict[0])
    df_len = df_dict.__len__()
    try:  # insert 1st line
        session.add(first_row)
        session.commit()

    except Exception as e_1_row:
        prime_key = inspect(model).primary_key[0].name
        print(f'\n\tProblem is in line #{1000 * chunk_num + i0}:')
        print(f'\t cant insert {first_row} \n')
        print(f'\t{prime_key} (prime key) value - {first_row.__dict__[prime_key]}\n')
        print(f'{e_1_row.args[0]}\n')
        session.rollback()
        exceptions_dict[str(first_row.__dict__[prime_key])] = (first_row, e_1_row)
        # fixme you should keep going, instead of return
        # return i0
    finally:
        if 1 >= df_len:
            return NO_LINE  # success  # return i0 if e else 0  #
    #     # session.rollback()
    #     # session.flush()
    #     if 2 >= df_len:
    #         # print(f'    Line try - finally - df_len: {df_len} - real_df_len: {df.__len__()}')
    #         # return i0 if e else 0  #
    #         print(f'\tdf_len <= 2 : {df_len}')
    #         return -1  # success

    half_len = int(df_len / 2)

    try:  # insert whole df
        session.bulk_insert_mappings(model, df_dict[1:])
        session.commit()  # session.rollback()
        # todo return exceptions_dict

    except Exception as e_bulk_insert:
        print(f'(Exception thrown) Bad line in chunk ({int(math.log((1000 / df_len), 2))} sub-chunk) '
              f'\n - Trying smaller data chunks, size: {half_len}')
        # print(e_bulk_insert)
        session.rollback()
        # session.flush()

        # smaller chunks
        # 1st half of data
        # todo this should be returning an exceptions_dict
        first_bad_line = find_row(df_dict[1:half_len + 1], i0 + 1, half_len)  # left quarter chunk
        # if first_bad_line > NO_LINE:
        # fixme you should keep going, instead of return
        # todo merge exceptions_dicts
        # return first_bad_line

        # 2nd half of data
        first_bad_line = find_row(df_dict[half_len + 1:], half_len + 1, half_len)  # right quarter chunk
        # todo or maybe this
        # first_bad_line = find_row(df_dict[half_len + 1:df_len+1], half_len + 1, half_len)  # right quarter chunk
        # todo consider returning the list
        # todo merge exceptions_dicts
        # return first_bad_line


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
    model: Base = TextText

    NO_LINE = -1  # todo move to utils?
    # todo consider passing as an argument or returning from the function
    prime_key = inspect(model).primary_key[0].name

    chunk_num = 5083  # <----------------------------- todo for DBG
    exit_flag = False

    while not exit_flag:

        try:
            # this for-loop is inside `try` for cases of commas (`,`) in `subject` col without brackets (`"`)
            for df in pd.read_csv(model.src_scv[0],
                                  dtype=model.dtype_dic_csv2py,
                                  header=0,
                                  names=model.col_names,
                                  na_values=['x', '#VALUE!', 'Unknown', ''],
                                  chunksize=100,
                                  # chunksize=app.config['CHUNK_SIZE_DB'],
                                  skiprows=100 * chunk_num,
                                  nrows=100,
                                  ):
                print(f'Data chunk number #{chunk_num}')
                # chunk_num += 1
                # if 510 < chunk_num:  # fixme remove - DBG
                #     exit_flag = True
                #     raise Exception
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
                    session.commit()  # raise Exception
                except Exception as e:
                    print('~~~~~~~~~~~~~~~')
                    # print(e)
                    session.rollback()
                    # session.flush()
                    # todo find_row should return exceptions_dict
                    first_bad_row = find_row(df_clean.to_dict(orient='records'), 0,
                                             df_clean.__len__())  # finally:  # ctx.pop()
                finally:
                    chunk_num += 1
            exit_flag = True
        except Exception as e_read_csv:
            print(f'{e_read_csv.args[0]}')
            #     TypeError: Cannot cast array data from dtype('O') to dtype('float64') according to the rule 'safe'
            # ValueError: could not convert string to float: ' 155 n. 6'
            print()
            chunk_num += 1
            exit_flag = False

            pass  # todo handle case of chunk in read_csv and continue the for loop

    if exceptions_dict:
        print(f'Bad rows:')
        for key, bad_row in exceptions_dict.items():
            print(f'\'{prime_key}\' value {key}: '
                  f'\n\tEntry: {bad_row[0]}'
                  f'\n\tError: {bad_row[1]}')
        #     todo log into a file
    else:
        print(f'Everything is fine and dandy')
    ctx.pop()
