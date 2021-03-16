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

# csv_file = '/home/fares/PycharmProjects/WebLib/app/raw_data/bookreferences2.csv'

app = create_app()
ctx = app.app_context()
ctx.push()
engine = db.engine  # todo or?    # with app.app_context(): engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
Base.metadata.create_all(engine)  # todo or? db.create_all(engine)
session = sessionmaker(bind=engine)()  # todo or? session = scoped_session(Session())

model: Base = TextText

NO_LINE = -1  # todo move to utils?


# Finds the line in the data that throws exception during bulk_insert_mapping on data
# return the number of the 1st problematic line, or -1 if no problem
# def find_row(df: pd.DataFrame , i0: int = 0, df_len: int = app.config['CHUNK_SIZE_DB']) -> int:
def find_row(df_dict: collections.abc.Mapping, i0: int = 0, df_len: int = app.config['CHUNK_SIZE_DB']) -> int:
    first_row: model = model(**df_dict[0])

    try:  # insert 1st line
        session.add(first_row)
        session.commit()
        print(f'after add-commit {first_row}')
        if 2 >= df_len:
            # print(f'    Line try - finally - df_len: {df_len} - real_df_len: {df.__len__()}')
            # return i0 if e else 0  #
            print(f'\tdf_len <= 2 : {df_len}')
            return NO_LINE  # success

    except Exception as e_1_row:
        print(f'{e_1_row}')
        prime_key = inspect(model).primary_key[0].name
        from sqlalchemy.ext.declarative import DeclarativeMeta
        # first_row.__table__: DeclarativeMeta
        print(f'\n    Problem is in line #{i0}: {first_row} \n')
        print(f'    {prime_key} key value - {first_row.__dict__[prime_key]}')
        # print(f'lines not uploaded to the DB: {df_dict[1:]}')
        # for line in df_dict[1:]:
        #     print(line)
        session.rollback()
        return i0
    # finally:
    #     # session.rollback()
    #     # session.flush()
    #     if 2 >= df_len:
    #         # print(f'    Line try - finally - df_len: {df_len} - real_df_len: {df.__len__()}')
    #         # return i0 if e else 0  #
    #         print(f'\tdf_len <= 2 : {df_len}')
    #         return -1  # success

    half_len = int(df_len / 2)
    # quart_len = int(half_len / 2)

    try:  # insert whole df
        print(f'    FULL try - i0: {i0} \tdf_len: {df_len} - real_df_len: {df_dict.__len__()}')
        print(f'    FULL try - df[1]: {df_dict[1]} ')
        session.bulk_insert_mappings(model, df_dict[1:])
        session.commit()
        # session.rollback()

    except Exception as e_bulk_insert:
        try:

            print(f'(Exception thrown - )    Trying smaller data chunks')
            print(e_bulk_insert)
            session.rollback()
            # session.flush()

            # smaller chunks
            print(' ---------- LEFT  ----------- ')
            first_bad_line = find_row(df_dict[1:half_len], i0 + 1, half_len)  # left quarter chunk
            if first_bad_line > NO_LINE:
                # print(f'first_bad_line: {first_bad_line}')
                return first_bad_line

            print(' -----------  RIGHT   ----------- ')
            first_bad_line = find_row(df_dict[half_len + 1:df_len], half_len + 1, half_len)  # right quarter chunk
            # print(f'first_bad_line: {first_bad_line}')
            # print(f'fin')
            return first_bad_line

        except Exception as ee:
            print('+' * 60)
            print(f'{ee}')

    # finally:
    #     session.rollback()

    print('~' * 15, ' fin ', '~' * 15, '\n')
    return NO_LINE


if '__main__' == __name__:
    df = pd.read_csv(model.src_scv[0],
                     dtype=model.dtype_dic_csv2py,
                     header=0,
                     names=model.col_names,
                     na_values=['x', '#VALUE!', 'Unknown', ''],
                     skiprows=20000,
                     nrows=30000
                     )  # , nrows=df_len)
    from sqlalchemy import create_engine, inspect, sql
    import numpy as np

    prime_key = inspect(model).primary_key[0].name
    df_clean: pd.DataFrame = df.drop_duplicates(prime_key)
    df_clean = df_clean.replace(np.nan, None)  # , regex=True)
    # df_clean = df_clean.replace(np.nan, '')  # , regex=True)
    # df_clean = df_clean.replace(np.nan, sql.null())

    numeric_cols = [col1.name for col1 in model.__table__.c if
                    isinstance(col1.type, sql.sqltypes.Integer)]
    for col in numeric_cols:
        if 'Csum' != col:
            # print(df[col])
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')  # , downcast='integer')
            # df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce', downcast='unsigned')

    df_clean = df_clean.astype(object).where(pd.notnull(df_clean), None)  # this is explained in:
    # df_clean = df_clean.where(pd.notnull(df_clean), None)  # this is explained in:
    # https://stackoverflow.com/questions/45395729/unknown-column-nan-in-field-list-python-pandas
    try:
        session.bulk_insert_mappings(model, df_clean.to_dict(orient='records'))
        # session.bulk_insert_mappings(model, df_clean.to_dict(orient='records').where(pd.notnull(df_clean), None))
        # session.bulk_insert_mappings(model, df_clean.to_dict(orient='records').astype(object).where(pd.notnull(df_clean), None))
        session.commit()
        # raise Exception
    except Exception as e:
        print('~~~~~~~~~~~~~~~')
        print(e)
        session.rollback()
        # session.flush()
        first_bad_row = find_row(df_clean.to_dict(orient='records'), 0, df_clean.__len__())
        # print(f'the 1st bad line is - #{first_bad_row}')
    # finally:
    #     ctx.pop()

ctx.pop()
