from typing import List, Dict, Tuple, Set
import logging, logging.config
from time import time, localtime
import pandas as pd

from flask import current_app as app, send_from_directory
from flask import render_template, make_response, redirect, url_for, request
from sqlalchemy import or_
from sqlalchemy.orm import Query
from flask_sqlalchemy import BaseQuery

from . import forms as f
from . import models as m
from . import utilities as utils

print('~' * 80)

links = {  # todo move to utils?
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
    reference_form: f.SearchReference = search_bar['reference_form']
    search_word: str = subject_form.subject_keyword_1.data

    # go to a clean `Search Results` page
    if not subject_form.validate_on_submit() and not reference_form.validate_on_submit():  # i.e. when method==GET
        return render_template('search_results.html',
                               title='Search',
                               description="Tiresias: The Ancient Mediterranean Religions Source Database. "
                                           "Default search page.",
                               search_bar=search_bar,
                               # categories=categories,
                               method='get'
                               )
    # search query submitted for search by subject
    query_logger: logging.Logger = logging.getLogger('queryLogger')
    if 'submit_subject' in request.form:
        categories: Dict[str, Dict] = search_by_subject(subject_form, filter_form)
        t_total = time() - t_time
        res_size = sum([len(cat["results"]) for cat in categories.values()])
        print(res_size)
        query_logger.info(f'\tQuery time: {t_total:<10.3f} '
                          f'#results: {res_size :<10} '
                          f'search word: \'{search_word}\'')
        return render_template('search_results.html',
                               index_title=f'Search Result for: {search_word}',
                               description=f'Tiresias: The Ancient Mediterranean Religions Source Database. '
                                           f'This page shows results for {search_word}, sorted by validity.',
                               search_by='by_subject',
                               search_bar=search_bar,
                               search_word=search_word,
                               categories=categories,
                               results_num=res_size,
                               query_time=t_total,
                               )

    # search query submitted for search by reference
    else:
        author: str = reference_form["search_author"].data
        work: str = reference_form["search_work"].data
        reference: str = reference_form["search_reference"].data
        chkbox: str = reference_form["fetch_books"].data
        print(f'chkbox - {chkbox}')

        refs_list, subjects_list = search_ref(author, work, reference, chkbox)

        t_total = time() - t_time
        query_logger.info(f'\tQuery time: {t_total:<10.3f} '
                          f'#results: quotes - {len(refs_list)-1 :<6} & refs&subjects - {len(subjects_list)-1 :<6} '
                          f'query (auth,work,ref): {[author, work, reference]}'
        )

        return render_template('search_ref_results.html',
                               index_title=f'Search Result for:'
                                           f' {author}'
                                           f' {work}'
                                           f' {reference}',
                               description=f'Tiresias: The Ancient Mediterranean Religions Source Database. '
                                           f'This page shows results for '
                                           f'{author}'
                                           f'{work}'
                                           f'{reference}.',
                               search_by='by_reference',
                               search_bar=search_bar,
                               search_word=' '.join([author, work, reference]),
                               refs_list=refs_list,
                               subjects_list=subjects_list,
                               query_time=t_total,
                               )


def search_ref(author: str,
               work: str,
               reference: str,
               chkbox:bool)\
        -> [List[List[str]], List[List[str]]]:
    title_tbl: m.Base = m.Title
    title_query: Query = title_tbl.query
    txt_tbl: m.Base = m.TextText
    txt_query: Query = txt_tbl.query
    ref_quote_tbl: m.Base = m.RefQuote
    ref_quote_q: Query = ref_quote_tbl.query
    if author:
        search_author: str = f'%{author}%'
        title_query = title_query.filter(title_tbl.author.like(search_author))
        ref_quote_q = ref_quote_q.filter(ref_quote_tbl.author.like(search_author))
    if work:
        search_work: str = f'%{work}%'
        title_query = title_query.filter(title_tbl.title.like(search_work))
        ref_quote_q = ref_quote_q.filter(ref_quote_tbl.title.like(search_work))
    if reference:
        search_reference: str = f'%{reference}%'
        txt_query = txt_query.filter(txt_tbl.ref.like(search_reference))
        ref_quote_q = ref_quote_q.filter(ref_quote_tbl.ref.like(search_reference))
    refs_list: List[List[str, str, str]] = [['Reference', 'Original Text', 'Translation to English']] + [
        [f'{r.author}, {r.title}, {r.ref}',
         r.text if None != r.text else 'Quote Unavailabe',
         r.texteng if None != r.texteng else 'Quote Unavailabe']
        for r in ref_quote_q if r.ref or r.text or r.texteng]
    subjects_list: List[List[str, str]] = [['Book bibliographic info', 'Subject']]
    if chkbox:
        txt_query = txt_query.join(title_query)
        subjects_dict: Dict[str, List[Set[str], Set[str]]] = {}
        for r in txt_query:
            pg_str = str(r.page)
            res: List[Set[str], Set[str]] = subjects_dict.setdefault(r.book_ref.title, [{pg_str}, set()])
            res[0].add(pg_str)
            res[1].add(r.subject)
            # glink = 'https://books.google.co.il/books?id=' + book.title_full.gcode
            # +'&lpg=PP1&pg=PA' + page | string + '#v=onepage&q&f=false'
        subjects_list += [
            [f'{title} pages: {", ".join(s[0])}', ', '.join(s[1])]
            for title, s, in subjects_dict.items()]
    return refs_list, subjects_list


def search_by_subject(subject_form: f.SearchSubject,
                      filter_form: f.FilterForm)\
        -> Dict[str, Dict]:
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
    # q_title_filter = txts_q_filter.join(m.Title)  # <-------------------------- .join(m.BookRef) slows significantly
    q_title_filter: BaseQuery = m.Title.query  # <-------------------------- .join(m.BookRef) slows significantly
    if -21 != from_century:
        q_title_filter: Query = q_title_filter.filter(or_(m.Title.centstart is None, m.Title.centstart >= from_century))
    if 21 != to_century:
        q_title_filter: Query = q_title_filter.filter(or_(m.Title.centend is None, m.Title.centend <= to_century))
    if language:
        q_title_filter: Query = q_title_filter.filter(or_(m.Title.lang is None, m.Title.lang == language))
    if ancient_author:
        q_title_filter: Query = q_title_filter.filter(m.Title.author == ancient_author)
    if ancient_title:
        q_title_filter: Query = q_title_filter.filter(m.Title.title == ancient_title)
    title_q_filter = txts_q_filter.join(q_title_filter)  # <-------------------------- .join(m.BookRef) slows significantly

    res_dict: Dict[int, m.ResultTitle] = {}
    highly_valid: List[m.ResultTitle] = []
    valid: List[m.ResultTitle] = []
    not_valid: List[m.ResultTitle] = []
    tt = time()  # for logging
    res_tit: m.TextText
    for res_tit in title_q_filter:
        res_title: m.ResultTitle = res_dict.setdefault(res_tit.number, m.ResultTitle(res_tit.title))
        res_title.add_bib(res_tit.book_ref).add_page(res_tit.page)
        res_title.add_ref(res_tit.ref).add_subject(res_tit.subject)
    # print(f'res_dict: {time() - tt:.5}')
    for res in res_dict.values():
        if len(res.books_dict) > 1: highly_valid.append(res)
        elif len(res.refs) > 1: valid.append(res)
        else: not_valid.append(res)

    categories: Dict[str, Dict] = {
        'high' : {
            'name'   : 'Highly Validated',
            'results': sorted(highly_valid, reverse=True)
            },
        'valid': {
            'name'   : 'Validated',
            'results': sorted(valid, reverse=True)
            },
        'not'  : {
            'name'   : 'Unvalidated',
            'results': not_valid
            }
        }
    return categories


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
                           title="Tiresias",  # todo different title
                           index_title="Books Included in the Project Database",  # todo different title
                           description="Tiresias: The Ancient Mediterranean Religions Source Database. "
                                       "The database references more than 200 title, which are listed in this page.", )


# ++++++++++++  list of Subjects in the db page ++++++++++++
@app.route(links['subjects'], methods=['GET', 'POST'])
def subject_list(search_word='', page=''):
    page = request.args.get('page', 1, type=int)
    search_bar: Dict = utils.init_search_bar()
    subject_form = search_bar['subject_form']
    # filter_form = search_bar['filter_form']

    if not subject_form.validate_on_submit():  # i.e. when method==GET
        subjects = m.TextSubject.query.paginate(page, app.config['SUBJECTS_PER_PAGE'], False)
        # there is not enough memory to do the next, but maybe consider the idea
        # subjects = TextSubject.query.order_by(
        #   TextSubject.subject.asc()).paginate(page, app.config['SUBJECTS_PER_PAGE'], False)
        next_url = url_for('subject_list', page=subjects.next_num) if subjects.has_next else None
        prev_url = url_for('subject_list', page=subjects.prev_num) if subjects.has_prev else None

        return render_template('subject_list.html',
                               title="Tiresias",
                               index_title="Subjects Included in the Project Database",  # todo different title
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
    search = f'%{search_word}%'
    subjects_query: Query = m.TextSubject.query
    subjects_filter: Query = subjects_query.filter(m.TextSubject.subject.like(search))
    subjects_ordered: Query = subjects_filter.order_by(m.TextSubject.Csum.desc())
    subjects = subjects_ordered.paginate(page, app.config['SUBJECTS_PER_PAGE'], False)
    next_url = url_for('subject_list', page=subjects.next_num) if subjects.has_next else None
    prev_url = url_for('subject_list', page=subjects.prev_num) if subjects.has_prev else None
    return render_template('subject_list.html',
                           title=f'Tiresias Subjects',
                           index_title=f'Search Results for: {search_word}',  # todo different title
                           description="Tiresias: The Ancient Mediterranean Religions Source Database"
                                       "The database includes over 50,000 subjects, listed in the page.",
                           subjects=subjects,
                           total=subjects.total,
                           next_url=next_url,
                           prev_url=prev_url,
                           search_bar=search_bar,
                           hide_filter=True,
                           )


# ++++++++++++  Serving Requests from JS ++++++++++++
@app.route('/fetchrefs')
def fetch_refs_for_title(title_num: str = '') -> str:
    ref_nums = ['\'' + r.strip('{ }\'') for r in request.args['refs'].split(',')]  # fixme should be r.strip('{ }\'')
    res = m.RefQuote.query.filter(m.RefQuote.number == request.args['title_num']).filter(m.RefQuote.ref.in_(ref_nums))
    refs_list: List[Tuple] = [tuple([r.ref.strip('\''), r.text, r.texteng]) for r in res if r.ref or r.text or r.texteng]
    ref_html = pd.DataFrame(refs_list).to_html(header=False, index=False, table_id=f'reftbl{title_num}', border=0,
                                               classes='table table-hover', na_rep='Quote unavailable')
    print(f' - fetchrefs - fetchrefs - fetchrefs - ')
    print(f' - {res.count()} -  {len(refs_list)} - ')
    return f'<h4 class="padding-1"> Source Quotes Referenced: </h4> {ref_html}' if refs_list \
        else f'No Quotes Available for References: <div class="padding">{request.args["refs"]}</div>'


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
    flash(
            "If you click on the button below You are about to ask the server to load raw scv files into the mysql DB. ")
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
