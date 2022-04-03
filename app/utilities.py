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
from functools import wraps
from flask import request, Response


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == 'admin' and password == 'secret'

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated