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
def c_sum(row):
    csum = 0
    clist = str(row.C).split(',')
    for c in clist:
        cc = c.split('-')
        if 2 == len(cc):
            csum += int(cc[1]) - int(cc[0])
        csum += 1
    return csum
