from typing import List, Dict, Tuple
import logging, logging.config
from time import time, localtime

from flask import current_app as app, send_from_directory
from flask import render_template, make_response, redirect, url_for, request
from sqlalchemy import or_
from sqlalchemy.orm import Query
from flask_sqlalchemy import BaseQuery

from . import forms as f
from . import models as m
from . import utilities as utils

print('~' * 80)

categories: Dict[str, Dict] = {
    'high' : {
        'name'   : 'Highly Validated',
        'results': [  # {'title': 'title', 'author': 'Author', 'ref_num': 'ref_num', 'refs': 'refs'}
            ]
        },
    'valid': {
        'name'   : 'Validated',
        'results': [  # {'title': 'title', 'author': 'Author', 'ref_num': 'ref_num', 'refs': 'refs'}
            ]
        },
    'not'  : {
        'name'   : 'Unvalidated',
        'results': [  # {'title': 'title', 'author': 'Author', 'ref_num': 'ref_num', 'refs': 'refs'}
            ]
        }
    }
links = {
    'home'     : '/',
    'search'   : '/search-results',
    'books'    : '/book-indices',
    'subjects' : '/subject-list',
    'not_found': '/page-not-found',
    }


# ++++++++++++  search results and filtering page ++++++++++++
@app.route(links['search'], methods=['GET', 'POST'])
# @app.route('/search-results/<string:search_word>/<int:page>', methods=['GET', 'POST'])
def search_results(search_word='', page=''):
    t_time = time()  # for logging

    from flask_wtf import FlaskForm
    search_bar: Dict[str, FlaskForm] = utils.init_search_bar()
    subject_form: f.SearchSubject = search_bar['subject_form']
    filter_form: f.FilterForm = search_bar['filter_form'].return_as_dict()
    # print(filter_form.return_as_dict())

    if not subject_form.validate_on_submit():  # i.e. when method==GET
        return render_template('search_results.html',
                               title='Search',
                               description="Tiresias: The Ancient Mediterranean Religions Source Database. "
                                           "Default search page.",
                               search_bar=search_bar,
                               # categories=categories,
                               method='get'
                               )
    # filter_form = f.FilterForm().return_as_dict()
    from_century = filter_form['from_century']
    to_century = filter_form['to_century']
    language = filter_form['language']
    ancient_author = filter_form['ancient_author']
    ancient_title = filter_form['ancient_title']
    reference = filter_form['reference']

    # ............  return all matching results (subjects) by C column [list] ............
    txts_query: BaseQuery = m.TextText.query
    # filter by subject (and reference if ref_filter field in form is filled out)
    # search_word = 'left'
    search_word = subject_form.subject_keyword_1.data
    search = f'%{search_word}%'
    txts_q_filter: BaseQuery = txts_query.filter(m.TextText.subject.like(search))
    txts_q_filter = txts_q_filter.filter_by(ref=reference) if reference else txts_q_filter
    # filter by the title's category
    q_title_filter = txts_q_filter.join(m.Title)  # <-------------------------- .join(m.BookRef) slows significantly

    if from_century: q_title_filter: Query = q_title_filter.filter(
            or_(m.Title.centstart == None, m.Title.centstart >= from_century))
    if to_century: q_title_filter: Query = q_title_filter.filter(
            or_(m.Title.centend == None, m.Title.centend <= to_century))
    if language: q_title_filter: Query = q_title_filter.filter(or_(m.Title.lang == None, m.Title.lang == language))
    if ancient_author: q_title_filter: Query = q_title_filter.filter(m.Title.author == ancient_author)
    if ancient_title: q_title_filter: Query = q_title_filter.filter(m.Title.title == ancient_title)

    res_dict: Dict[int, m.ResultTitle] = {}
    highly_valid: List[m.ResultTitle] = []
    valid: List[m.ResultTitle] = []
    not_valid: List[m.ResultTitle] = []

    tt = time()  # for logging
    res_tit: m.TextText

    for res_tit in q_title_filter:
        res_title: m.ResultTitle = res_dict.setdefault(res_tit.number, m.ResultTitle(res_tit.title))
        res_title.add_bib(res_tit.book_ref).add_page(res_tit.page)
        res_title.add_ref(res_tit.ref).add_subject(res_tit.subject)

    print(f'res_dict: {time() - tt:.5}')

    for res in res_dict.values():
        if len(res.books_dict) > 1: highly_valid.append(res)
        elif len(res.refs) > 1: valid.append(res)
        else: not_valid.append(res)

    categories['high']['results'] = sorted(highly_valid, reverse=True)
    categories['valid']['results'] = sorted(valid, reverse=True)
    categories['not']['results'] = not_valid

    t_total = time() - t_time
    query_logger: logging.Logger = logging.getLogger('queryLogger')
    query_logger.info(f'\tQuery time: {t_total:<10.3f} #results: {len(res_dict):<10} search word: \'{search_word}\'')

    return render_template('search_results.html',
                           title=f'Search Result for: {search_word}',
                           description=f'Tiresias: The Ancient Mediterranean Religions Source Database. '
                                       f'This page shows results for {search_word}, sorted by validity.',
                           search_bar=search_bar,
                           categories=categories,
                           search_word=search_word,
                           results_num=len(res_dict),
                           query_time=t_total,
                           )


def nothing():
    pass


# ++++++++++++  Jinja2 Filter Functions ++++++++++++
@app.template_filter("clean_date")
def clean_date(dt):
    return dt.strftime("%d %b %Y")


@app.template_filter("value_or_zero")
def value_or_zero(val):
    return val if val else 0


@app.template_filter("value_or_empty")
def value_or_zero(val):
    return val if val else ''


# ++++++++++++  Home page ++++++++++++
@app.route(links['home'], methods=['GET', 'POST'])
def home():
    search_bar: Dict = utils.init_search_bar()
    email_form = f.SignupForm()
    # search_word = search_bar['subject_form'].subject_keyword_1.data
    return render_template('index.html',
                           title='Tiresias',
                           index_title='The Ancient Mediterranean Religions Source Database',
                           description='Tiresias: The Ancient Mediterranean Religions Source Database Home page.'
                                       'The Tiresias contains more than database allows'
                                       'Here is a short introduction to the site, search options, and conatact details.'
                                       'Also can be found a few database graphs describing ',
                           search_bar=search_bar,
                           email_form=email_form,
                           home_flag=True
                           )


# ++++++++++++  list of books page ++++++++++++
@app.route(links['books'])
# @app.route('/book-indices')
# todo create a table of the listed books and fix the description to show the correct number of books (dynamically)
def book_indices():
    return render_template('book_indices.html',
                           title="Tiresias: Books Included in the Project Database",  # todo different title
                           description="Tiresias: The Ancient Mediterranean Religions Source Database. "
                                       "The database references more than 200 title, which are listed in this page.", )


# ++++++++++++  list of Subjects in the db page ++++++++++++
@app.route(links['subjects'], methods=['GET', 'POST'])
def subject_list(search_word='', page=''):
    page = request.args.get('page', 1, type=int)
    search_bar: Dict = utils.init_search_bar()
    subject_form = search_bar['subject_form']
    filter_form = search_bar['filter_form']

    if not subject_form.validate_on_submit():  # i.e. when method==GET
        subjects = m.TextSubject.query.paginate(page, app.config['SUBJECTS_PER_PAGE'], False)
        # there is not enough memory to do the next, but maybe consider the idea
        # subjects = TextSubject.query.order_by(
        #   TextSubject.subject.asc()).paginate(page, app.config['SUBJECTS_PER_PAGE'], False)
        next_url = url_for('subject_list', page=subjects.next_num) if subjects.has_next else None
        prev_url = url_for('subject_list', page=subjects.prev_num) if subjects.has_prev else None

        return render_template('subject_list.html',
                               title="Tiresias Subjects Included in the Project Database",  # todo different title
                               description="Tiresias: The Ancient Mediterranean Religions Source Database."
                                           "The database includes over 50,000 subjects, listed in the page."
                                           "For a more topic specific list, use the search option",
                               subjects=subjects,
                               total=subjects.total,
                               next_url=next_url,
                               prev_url=prev_url,
                               search_bar=search_bar,
                               hide_filter=True,
                               # home_flag=False
                               )

    search_word = subject_form.subject_keyword_1.data
    search = '%{}%'.format(search_word)
    subjects_query: Query = m.TextSubject.query
    subjects_filter: Query = subjects_query.filter(m.TextSubject.subject.like(search))
    subjects_ordered: Query = subjects_filter.order_by(m.TextSubject.Csum.desc())
    subjects = subjects_ordered.paginate(page, app.config['SUBJECTS_PER_PAGE'], False)
    next_url = url_for('subject_list', page=subjects.next_num) if subjects.has_next else None
    prev_url = url_for('subject_list', page=subjects.prev_num) if subjects.has_prev else None
    return render_template('subject_list.html',
                           title=f'Tiresias Subjects Search Results for: {search_word}',  # todo different title
                           description="Tiresias: The Ancient Mediterranean Religions Source Database"
                                       "The database includes over 50,000 subjects, listed in the page.",
                           subjects=subjects,
                           total=subjects.total,
                           next_url=next_url,
                           prev_url=prev_url,
                           search_bar=search_bar,
                           hide_filter=True,
                           )


# ++++++++++++  Error Handling ++++++++++++
@app.errorhandler(404)
@app.route(links['not_found'], methods=['GET', 'POST'])
def not_found(error):
    resp = make_response(render_template('page_not_found.html',
                                         title="Tiresias Project - Page not Found",
                                         description=str(error)), 404)
    return resp


# ++++++++++++  Serving (Google's) Robots & Crawlers ++++++++++++
@app.route('/robots.txt')
@app.route('/sitemap.xml')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])


# ++++++++++++ ++++++++++++ ++++++++++++
# ++++++++++++ ++++++++++++ ++++++++++++
# ++++++++++++ ++++++++++++ ++++++++++++
# ++++++++++  DGB and Testing ++++++++++
# ++++++++++++ ++++++++++++ ++++++++++++
# ++++++++++++ ++++++++++++ ++++++++++++
# ++++++++++++ ++++++++++++ ++++++++++++
@app.route("/csv_to_mysql_route", methods=['GET', 'POST'])
def load_db():
    from flask import flash
    flash("If you click on the button below You are about to ask the server to load raw scv files into the mysql DB. ")
    flash("It's gonna take a loooong time to finish (if lucky). ")
    flash("Are you sure you want to do that? ")
    return render_template('dbg/csv_to_mysql.html', load_db_flag=True, avoid_robots=True)


@app.route("/csv_to_mysql_func")
# @app.route('/csv_to_mysql_func/<string:model>', methods=['GET', 'POST'])
def csv_to_mysql_func_btn(model='TextText'):
    print("It's happening... ")
    from time import time
    t = time()
    from db_migration import DBMigration
    DBMigration().load_full_db()
    # todo
    # DBMigration().load_single(m.TextText)
    # DBMigration().load_single(Base.__subclasses__()[f'm.{model}']) #fixme
    # DBMigration().load_src_file(m.TextText, './textsa2.csv')

    print("Time elapsed: " + str(time() - t) + " s.")
    return '<h1> A O K </h1>'
