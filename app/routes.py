from datetime import time
from typing import List, Dict

from flask import current_app as app
from flask import render_template, make_response, redirect, url_for, request
from sqlalchemy.orm import Query
from wtforms import BooleanField
from wtforms.widgets import CheckboxInput

from db_migration import csv_to_mysql

from . import forms as f
from . import models as m
from . import utilities as utils

print('~' * 100)


# ++++++++++++  search results and filtering page ++++++++++++
@app.route('/search-results/<string:search_word>', methods=['GET', 'POST'])
@app.route('/search-results', methods=['GET', 'POST'])
def search_results(search_word=''):
    # todo put here the "waiting" bar/circle/notification (search "flashing/messages" in the flask doc)
    search_bar: Dict = utils.init_search_bar()
    subject_form = search_bar['subject_form']
    filter_form = search_bar['filter_form']

    # if 'GET' == request.method:
    if not subject_form.validate_on_submit():
        #     # print('^' * 13, ' not validated on submit ', '^' * 13)
        #     redirect(url_for('not_found'))

        print('-' * 13, ' GET ', '-' * 13)
        return render_template('search-results.html',
                               title='',
                               description="Tiresias: The Ancient Mediterranean Religions Source Database",
                               results=['THIS', 'SHOULD', 'BE', 'SOMETHING', 'ELSE'],
                               total=13,
                               search_bar=search_bar
                               )

    print('-' * 13, ' POST ', '-' * 13)
    search_word = subject_form.subject_keyword_1.data
    print(search_word)
    # search = f'%{search_word}%'
    search = '%{}%'.format(search_word)
    page = request.args.get('page', 1, type=int)
    subjects_query: Query = m.TextSubject.query
    subjects_filter: Query = subjects_query.filter(m.TextSubject.subject.like(search))
    subjects_ordered: Query = subjects_filter.order_by(m.TextSubject.Csum)
    print('*' * 13)
    print(subjects_query)
    print('*' * 13)
    print(subjects_filter)
    print('.' * 13)
    print(subjects_ordered)


    subjects = subjects_ordered.paginate(page, app.config['SUBJECTS_PER_PAGE'], False)
    # subjects = subjects_ordered.all()

    print('=' * 13)
    for s in subjects.items:
        print(s)

    # subjects_paginated = subjects_ordered.paginate(page, app.config['SUBJECTS_PER_PAGE'], False)
    # subjects = [f.MultiCheckboxField() for sp in subjects_paginated]
    next_url = url_for('search_results', search_word=search_word, page=subjects.next_num) if subjects.has_next else None
    prev_url = url_for('search_results', search_word=search_word, page=subjects.prev_num) if subjects.has_prev else None

    # print(search_bar['subject_form'].subject_keyword_1.raw_data)
    # print(search_bar['subject_form'].subject_keyword_2.raw_data)
    # print('^' * 15)
    # print(search_word)

    # print(request.args['results'])
    # results = request.args['results']
    # listlist = [CheckboxInput(label='bla', )]
    return render_template('search-results.html', title=f'Search Result for: {search_word}',
                           description="Tiresias: The Ancient Mediterranean Religions Source Database",
                           method='post',
                           results=subjects.items,
                           total=subjects.total,
                           search_bar=search_bar,
                           next_url=next_url,
                           prev_url=prev_url,
                           chkbx_class = BooleanField,
                           # chkbx_class = f.Chkbx,

                           # listlist=listlist
                           )

    # todo
    #  change projection to include entire entry instead of index alone
    #  add fuzzy (returns things *like* but not necessarily the same) / regex search on the query
    #  clean data before:
    #    split creation of tables function in db-migration into multiple function
    #    appropriate normalization


# ++++++++++++  Home page ++++++++++++
@app.route('/', methods=['GET', 'POST'])
def home():
    search_bar: Dict = utils.init_search_bar()
    search_word = search_bar['subject_form'].subject_keyword_1.data
    return render_template('index.html',
                           title='Tiresias',
                           index_title='The Ancient Mediterranean Religions Source Database',
                           description='Tiresias: The Ancient Mediterranean Religions Source Database',
                           search_bar=search_bar
                           )
    # if 'GET' == request.method:
    #     print('~' * 15, ' home() - GET ', '~' * 15)
    # print('~' * 15, ' home() - POST ', '~' * 15)
    # return redirect(url_for(search_results,search_word))


# ++++++++++++  list of books page ++++++++++++
@app.route('/book-indices')
def book_indices():
    return render_template('book-indices.html',
                           title="Books Included in the Tiresias Project Database",  # todo different title
                           description="Tiresias: The Ancient Mediterranean Religions Source Database", )


# ++++++++++++  list of "subjects" in the db page ++++++++++++
@app.route('/subject-list')
def subject_list():
    page = request.args.get('page', 1, type=int)
    subjects = m.TextSubject.query.paginate(page, app.config['SUBJECTS_PER_PAGE'], False)
    # there is not enough memory to do the next, but maybe consider the idea
    # subjects = TextSubject.query.order_by(
    #   TextSubject.subject.asc()).paginate(page, app.config['SUBJECTS_PER_PAGE'], False)
    next_url = url_for('subject_list', page=subjects.next_num) if subjects.has_next else None
    prev_url = url_for('subject_list', page=subjects.prev_num) if subjects.has_prev else None

    return render_template('subject-list.html',
                           title="Tiresias Subjects",  # todo different title
                           description="Tiresias: The Ancient Mediterranean Religions Source Database",
                           subjects=subjects,
                           total=subjects.total,
                           next_url=next_url,
                           prev_url=prev_url
                           )


# ++++++++++++  Error Handling ++++++++++++
@app.errorhandler(404)
def not_found(error):
    resp = make_response(render_template('page_not_found.html',
                                         title="Tiresias Project - Page not Found",
                                         description=str(error)), 404)
    print(error)
    return resp


# ++++++++++++  Login ++++++++++++
# @login_required https://flask-login.readthedocs.io/en/latest/ todo use this to protect from logged-off users
# @app.route('/insert-data')
# def insert_data():
#     print('congrats on the new addition')


# ++++++++++++  dbg pages ++++++++++++
@app.route('/check', methods=['GET', 'POST'])
def check_check():
    # subject_form = f.SearchSubject(request.form)
    subject_form = f.SimpleForm()
    # reference_form = SearchReference(request.form)
    # if subject_form.submit_subject.data and subject_form.validate_on_submit():
    #     print('Great Success')
    #     return redirect(url_for('success', title='subject_form'))
    # print('what happend')
    # print("subject_form.errors")
    # flash(subject_form.errors)

    if 'GET' == request.method:
        print('-' * 13, ' GET ', '-' * 13)

        return render_template('check.html', form1=subject_form)

    print('-' * 13, ' POST ', '-' * 13)
    if subject_form.validate_on_submit():
        print(subject_form.example.data)
        return render_template("check.html", form1=subject_form, data=subject_form.example.data)
    else:
        print("Validation Failed")
        print(subject_form.errors)
        return render_template('check.html', form1=subject_form, data=[])  # , form2=reference_form)


@app.template_filter("clean_date")
def clean_date(dt):
    return dt.strftime("%d %b %Y")


@app.route("/try_jinja")
def try_jinja():
    # Strings
    _str = "Julian"

    # Integers
    _int = 30

    # Lists
    _list = ["Python", "JavaScript", "Bash", "Ruby", "C", "Rust"]

    # Dictionaries
    _dict = {
        "Tony": 43,
        "Cody": 28,
        "Amy": 26,
        "Clarissa": 23,
        "Wendell": 39
    }

    # Tuples
    _tuple = ("Red", "Blue")

    # Booleans
    _bool = True

    # Classes
    class _class:
        def __init__(self, name, description, domain):
            self.name = name
            self.description = description
            self.domain = domain

        def pull(self):
            return f"Pulling repo '{self.name}'"

        def clone(self, repo):
            return f"Cloning into {repo}"

    _class_obj = _class(
        name="The Name",
        description="Some short description",
        domain="https://github.com/something-something.git"
    )

    # Functions
    def _function(x, qty=1):
        return x * qty

    from datetime import datetime
    date = datetime.utcnow()

    my_html = "<h1>This is some HTML</h1>"

    return render_template(
        "try_jinja.html", _str=_str, _int=_int, _list=_list,
        _dict=_dict, _tuple=_tuple, _bool=_bool, _class=_class,
        _class_obj=_class_obj, _function=_function, date=date,
        my_html=my_html
    )


@app.route("/try_bs", methods=['GET', 'POST'])
def try_bs():
    # headers = {"Content-Type": "app/kaka"}
    # return make_response(
    #     'Test worked!',
    #     200,
    #     headers
    # )
    from flask import flash
    flash('mamase mamasa mamakusa')

    return render_template('try_bs.html', title='TRY', range=range(25))


@app.route("/csv_to_mysql", methods=['GET', 'POST'])
def csv_to_mysql():
    csv_to_mysql()
    return 'OK'


@app.route("/success/<title>", methods=['GET', 'POST'])
def success(title):
    sform = f.SearchSubject()
    return '<h1>' + title + ' Great Success</h1>'
    # return render_template('try_bs.html', title='Great Success', sform=sform)
