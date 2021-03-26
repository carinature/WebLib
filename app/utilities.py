from typing import Dict, List, Tuple

from flask_wtf import FlaskForm

from . import forms
from . import models

from flask import request


def init_search_bar() -> Dict[str, FlaskForm]:
    return {
        'subject_form'  : forms.SearchSubject(request.form),
        'reference_form': forms.SearchReference(request.form),
        'filter_form'   : forms.FilterForm(request.form),
        'radio_buttons' : forms.SearchTypeChoice(request.form)
        }


def c_sum(clist: List[str]) -> int:
    csum: int = 0
    clist_exp: List[str] = str(clist).split(',')
    for c in clist_exp:
        cc = c.split('-')
        if 2 == len(cc):
            csum += int(cc[1]) - int(cc[0])
        csum += 1
    return csum


###################################################################


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


# # logs faulty lines into the file and return the str
# def log_faulty_line(faulty_line: model,
#                     exception: Exception,
#                     prime_key_name: str = inspect(model).primary_key[0].name,
#                     file: str = 'db_migration_log.txt'):  # file:TextIOWrapper='db_migration_log.txt'):
#     prime_key_val = str(faulty_line.__dict__[prime_key_name])
#     massage = f'\n{prime_key_name}  -  {prime_key_val}: ' \
#               f'\n\tEntry: {faulty_line}' \
#               f'\n\tError: {exception}'  # .args[0]}'
#     print(massage)  # fixme # file.write(massage)
#     # logging.info
#     return massage
# def log_faulty_lines(rows_dict, file='db_migration_log.txt'):
#     for prime_key_val, faulty_line in rows_dict.items():
#         print(log_faulty_line(faulty_line[0], faulty_line[1], prime_key_name, file))
