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
