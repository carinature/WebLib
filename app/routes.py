from datetime import time
from typing import List, Dict

from flask import current_app as app
from flask import render_template, make_response, redirect, url_for, request
from sqlalchemy.orm import Query

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

    if 'GET' == request.method:
        print('-' * 13, ' GET ', '-' * 13)
        return render_template('search-results.html',
                               title=f'Search Results for: {search_word}',
                               description="Tiresias: The Ancient Mediterranean Religions Source Database",
                               results=['THIS', 'SHOULD', 'BE', 'SOMETHING', 'ELSE'],
                               total=0,
                               search_bar=search_bar
                               )

    print('-'*13, ' POST ', '-'*13)
    if search_bar['subject_form'].validate_on_submit():
        print('subject_form valid')
    if search_bar['subject_form'].validate():
            print('subject_form validate')

    if not search_word:
        search_word = search_bar['subject_form'].subject_keyword_1.data

    search = "%{}%".format(search_word)
    page = request.args.get('page', 1, type=int)
    subjectsQuery: Query = m.TextSubject.query

    subjects = subjectsQuery.filter(m.TextSubject.subject.like(search))
    subjectsPage = subjects.paginate(page, app.config['SUBJECTS_PER_PAGE'], False)

    # print(search_bar['subject_form'].subject_keyword_1.raw_data)
    # print(search_bar['subject_form'].subject_keyword_2.raw_data)
    # print('^' * 15)
    # print(search_word)

    # print(request.args['results'])
    # results = request.args['results']

    return render_template('search-results.html', title=f'Search Result for: {search_word}',
                           description="Tiresias: The Ancient Mediterranean Religions Source Database",
                           results=subjectsPage,
                           total=subjectsPage.total,
                           search_bar=search_bar
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
    subject_form = f.SearchSubject(request.form)
    # reference_form = SearchReference(request.form)
    # if subject_form.submit_subject.data and subject_form.validate_on_submit():
    #     print('Great Success')
    #     return redirect(url_for('success', title='subject_form'))
    # if reference_form.submit_reference.data and reference_form.validate_on_submit():
    #     print('Great Success')
    #     return redirect(url_for('success', title='reference_form'))
    #     # return render_template('try_bs.html', title='Great Success', subject_form=subject_form)
    # print('what happend')
    # print("subject_form.errors")
    # print(subject_form.errors)
    # flash(subject_form.errors)
    # page = request.args.get('page', 1, type=int)
    # table = TextSubject.query.paginate(page, app.config['ITEMS_PER_PAGE'], False).items
    # return render_template('try_bs.html',mydata=table, form1=subject_form)  # , form2=reference_form)
    return render_template('try_bs.html', form1=subject_form)  # , form2=reference_form)


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


@app.route("/pipi", methods=['GET', 'POST'])
def pipi():
    csv_to_mysql()
    return 'OK'
    # return render_template('try_bs.html', form1=subject_form)  # , form2=reference_form)


@app.route("/success/<title>", methods=['GET', 'POST'])
def success(title):
    sform = f.SearchSubject()
    return '<h1>' + title + ' Great Success</h1>'
    # return render_template('try_bs.html', title='Great Success', sform=sform)
