from typing import List, Dict, Tuple

import pandas as pd
from itertools import groupby

from flask import current_app as app, flash, g, session, send_from_directory
from flask import render_template, make_response, redirect, url_for, request
from flask_sqlalchemy import BaseQuery
from sqlalchemy.orm import Query
from sqlalchemy.sql.functions import count

from .models import Base
from . import forms as f
from . import models as m
from . import utilities as utils

print('~' * 80)

from sqlalchemy import orm


def get_flag():
    if 'flag' not in g:
        g.flag = False
    return g.flag


@app.teardown_appcontext
def teardown_db(exception):
    flag = g.pop('flag', None)
    if flag is not None:
        flag = False


categories = [
    {
        'name'   : 'Highly Validated',
        'id'     : 'high',
        'results': [  # {'title': 'title', 'author': 'Author', 'ref_num': 'ref_num', 'refs': 'refs'}
            ]
        },
    {
        'name'   : 'Validated',
        'id'     : 'valid',
        'results': [  # {'title': 'title', 'author': 'Author', 'ref_num': 'ref_num', 'refs': 'refs'}
            ]
        },
    {
        'name'   : 'Unvalidated',
        'id'     : 'not',
        'results': [  # {'title': 'title', 'author': 'Author', 'ref_num': 'ref_num', 'refs': 'refs'}
            ]
        }
    ]
links = {
    'home'       : '/',
    'search'     : '/search-results',
    'test_search': '/test-search-results',
    'books'      : '/book-indices',
    'subjects'   : '/subject-list',
    }


# ++++++++++++  search results and filtering page ++++++++++++
@app.route(links['test_search'], methods=['GET', 'POST'])
# @app.route('/search-results/<string:search_word>/<int:page>', methods=['GET', 'POST'])
def search_test(search_word='', page=''):
    from time import time
    t_total = time()  # for logging

    # search = '%{}%'.format('freedwoman')
    search = '%{}%'.format('divin')
    # search = '%{}%'.format('women')
    filter_form = f.FilterForm().return_as_dict()
    from_century = filter_form['from_century']
    to_century = filter_form['to_century']
    language = 'Latin'
    # language = filter_form['language']
    ancient_author = filter_form['ancient_author']
    ancient_title = filter_form['ancient_title']
    reference = filter_form['reference']

    # ............  return all matching results (subjects) by C column [list] ............
    txts_query: BaseQuery = m.TextText.query
    # filter by subject (and reference if ref_filter field in form is filled out)
    txts_q_filter: BaseQuery = txts_query.filter(m.TextText.subject.like(search))
    txts_q_filter = txts_q_filter.filter_by(ref=reference) if reference else txts_q_filter

    # filtered_sub_query: Query = txts_q_filter.subquery()

    # # group by title and then by bib_info (referencing book) and count refs (C's)
    # sub_q_title_and_bibinfo_with_count = txts_query.with_entities(
    #     # filtered_sub_query.c.number,
    #     filtered_sub_query.c.number,
    #     filtered_sub_query.c.biblio,
    #     count().label('count_c')
    # )
    # groups_by_title_bibinfo = sub_q_title_and_bibinfo_with_count.group_by(
    #     filtered_sub_query.c.number,
    #     filtered_sub_query.c.biblio)
    # grouped_sub_query: Query = groups_by_title_bibinfo.subquery()
    # # filter by subject and count ref-books
    # sub_q_title_bibcount = txts_query.with_entities(
    #     grouped_sub_query.c.number,
    #     count().label('count_bib')
    # )
    # groups_by_title = sub_q_title_bibcount.group_by(grouped_sub_query.c.number)
    # highly_valid, valid, not_valid = List[m.ResultTitle], List[m.ResultTitle], List[m.ResultTitle]
    # bib_more_than_1, bib_only_1 = {}, {}
    # print(txts_q_filter)

    # x: m.TextText
    # for x in txts_q_filter:
    #     print(type(x))
    #     print(x)
    #     title_key = x.number
    #     res_title: m.ResultTitle = res_dict.setdefault(title_key, m.ResultTitle(title_key, filter_form))

    # df: pd.DataFrame = pd.read_sql(txts_q_filter.statement, txts_q_filter.session.bind)
    # print(df.tail())
    #
    # groups_by_title_num: pd.DataFrame.groupby.DataFrameGroupBy = df.groupby(
    #     by=['number'],  # ,'biblio'],  # Notice that a tuple is interpreted as a (single) key.
    #     # level=0,
    #     # as_index=False,  # is effectively “SQL-style” grouped output.
    #     # sort=True,
    # )
    # lists_by_title_num = groups_by_title_num.apply(list)
    #
    # title_key: str
    # titles_group: pd.DataFrame
    # for title_key, titles_group in groups_by_title_num:
    #     # print(type(titles_group))
    #     groups_by_title_and_bib: pd.DataFrame.groupby.DataFrameGroupBy = titles_group.groupby(
    #         by=['biblio'])
    #     res_title: m.ResultTitle = res_dict.setdefault(title_key, m.ResultTitle(title_key, filter_form))
    #     if not res_title.filtered_flag:
    #         continue
    #     bib_count = len(titles_group['biblio'].unique())
    #     # print(bib_count)
    #     if 2> bib_count:
    #         continue
    #     bib_info: str
    #     bib_info_group: pd.DataFrame
    #     for bib_info, bib_info_group in groups_by_title_and_bib:
    #         # print('-------\n', bib_info)
    #         # print('-------\n', bib_info_group)
    #         res_bib = res_title.books_dict.setdefault(bib_info, res_title.add_bib(bib_info))
    #         # res_title.add_bib(bib_info)
    #     highly_valid.append(res_title)

    # print('sr' * 33)
    # for sr, gr in res_dict.items():
    #     print(sr)
    #     print(gr)

    # highly_valid.append(bib_more_than_1)
    # valid.append(bib_only_1)

    q_title_filter = txts_q_filter.join(m.Title)

    if from_century:
        q_title_filter: Query = q_title_filter.filter(m.Title.centstart >= from_century)
    if to_century:
        q_title_filter: Query = q_title_filter.filter(m.Title.centend <= to_century)
    if language:
        q_title_filter: Query = q_title_filter.filter(m.Title.lang == language)
    if ancient_author:
        q_title_filter: Query = q_title_filter.filter(m.Title.author == ancient_author)
    if ancient_title:
        q_title_filter: Query = q_title_filter.filter(m.Title.title == ancient_title)

    res_dict: Dict[str, m.ResultTitle] = {}
    highly_valid: List[m.ResultTitle] = []

    res_tit: m.TextText
    for res_tit in q_title_filter:
        res_title: m.ResultTitle = res_dict.setdefault(
                res_tit.number,
                m.ResultTitle(res_tit.number,
                              res_tit.title.title,
                              res_tit.title.author))

        res_title.add_bib(res_tit.book_ref)

    highly_valid = sorted(res_dict.values(), key=m.ResultTitle.num_ref_books, reverse=True)

    print('=' * 12 + ' Total Time elapsed: ' + str(time() - t_total) + ' s.')

    # 6276 for number and 15 & 31 for bub-info  || 8255 and 31.0 & 64.0
    return render_template('dbg/test_search.html',
                           motototo=['Nothing', 'worth', 'having', 'comes', 'easy'],
                           # list1=highly_valid,
                           # list2=valid,
                           list1=highly_valid,
                           dict2=res_dict,
                           )


# ++++++++++++  search results and filtering page ++++++++++++
@app.route(links['search'], methods=['GET', 'POST'])
# @app.route('/search-results/<string:search_word>/<int:page>', methods=['GET', 'POST'])
# @app.route('/search-results/<int:page>', methods=['GET', 'POST'])
# @app.route('/search-results/<string:search_word>', methods=['GET', 'POST'])
def search_results(search_word='', page=''):
    # todo put here the "waiting" bar/circle/notification (search "flashing/messages" in the flask doc)

    search_bar: Dict = utils.init_search_bar()
    subject_form: f.SearchSubject = search_bar['subject_form']
    filter_form: f.FilterForm = search_bar['filter_form']
    print(filter_form.return_as_dict())

    if not subject_form.validate_on_submit():  # i.e. when method==GET
        return render_template('search_results.html',
                               title='Search',
                               description="Tiresias: The Ancient Mediterranean Religions Source Database. "
                                           "Default search page.",
                               search_bar=search_bar,
                               method='get'
                               )

    # print('-' * 13, ' POST ', '-' * 13)
    # print(' - request.form - ')
    # print(request.form)
    # print(' - subject_form - ')
    # print(subject_form)
    print(' - filter_form - ')
    print(filter_form)
    # print(filter_form.from_century)
    # print(filter_form.from_century.data)
    # print(type(filter_form.from_century))
    # print(type(filter_form.from_century.data))

    # print(f'Starting data Value : {subject_form.submit_subject.data}')
    # print(f'Ending data Value :     {filter_form.fetch_results.data}')

    search_word = subject_form.subject_keyword_1.data
    search = '%{}%'.format(search_word)
    # search = '%{}%'.format('women')
    # page = request.args.get('page', 1, type=int)
    session['formdata'] = request.form
    session['search_word'] = search_word

    txts_table = m.TextText
    sbj_col, c_col, num_col = txts_table.subject, txts_table.C, txts_table.number
    bib_info_col, ref_col, page_col = txts_table.biblio, txts_table.ref, txts_table.page
    # ............  return all matching results (subjects) by C column [list] ............
    texts_query: Query = txts_table.query
    print(texts_query)
    # txts_q_with_ent: Query = texts_query.with_entities(sbj_col, count(sbj_col),
    # txts_q_with_ent: Query = texts_query.with_entities(num_col, sbj_col, ref_col, count(bib_info_col), page_col)  # count())
    #     # txts_q_with_ent: Query = texts_query.with_entities(txts_subject_col, count(txts_subject_col),
    txts_q_with_ent: Query = texts_query.with_entities(
            num_col, ref_col,
            sbj_col,
            bib_info_col,
            page_col,
            c_col)  # count()) fixme remove C_col in production
    txts_q_with_ent_filter: Query = txts_q_with_ent.filter(sbj_col.like(search))
    if filter_form.reference.data:
        txts_q_with_ent_filter: Query = txts_q_with_ent_filter.filter(ref_col.like(str(filter_form.reference)))
    # txts_q_with_ent_filter_group: Query = txts_q_with_ent_filter.group_by(txts_num_col, sbj_col)
    # txts_q_with_ent_filter_group_order: Query = txts_q_with_ent_filter_group.order_by(num_col, bib_info_col)
    # needs to be ordered for the itertools.groupby() later on,
    #   since it collects together CONTIGUOUS items with the same key.
    # todo consider doing the order by bib_info_col after groupby(by num_col)
    txts_q_with_ent_filter_order: Query = txts_q_with_ent_filter.order_by(num_col)  # , bib_info_col)
    numbers_dict: Dict = {}
    res_dict: Dict = {}
    highly_valid, valid, not_valid = [], [], []

    # ............  group the results by (referenced) title ('number' column) [dict?] ............
    groups_by_number = groupby(
            txts_q_with_ent_filter_order,
            key=lambda txts_table: (txts_table.number))  # , txts_table.biblio))

    # print('$'*20, )
    # for ke, ge in groups_by_number:
    #     print('#' * 13, ke)
    #     print('^' * 13, list(ge))
    filter_form = f.FilterForm().return_as_dict()

    # ............  filter and add the references (ref-ing titles) [dict of result objects ] ............
    for title_number, texts_tuples_group in groups_by_number:
        # resdict[k]=[txts_table for txts_table in g]
        # print('=' * 100, 'title_number: ', title_number)
        numbers_dict[title_number]: Dict = {}
        # ... create title object. filtering is done during object init
        res = m.ResultTitle(title_number, filter_form)
        # if the result doesn't pass the filters, continue to the next result.
        # can only know that after creating the result/title obj when checking in the Titles table.
        # if this title doesn't pass the filtering continue to the next result (it won't be added to the final list)
        # print('(-)' * 13, res)
        if not res.filtered_flag:  # fixme - too primitive?
            continue

        # TODO note that after the next line (sorted()) - texts_tuples_group NO LONGER EXISTS
        #   maybe it's better to use order_by of sql (if slower)
        # ... sub grouping the results by the ref-ing titles
        texts_tuples_group_ordered = sorted(texts_tuples_group, key=lambda x: x[3])
        group_by_number_n_bibinfo = groupby(
                texts_tuples_group_ordered,
                key=lambda txts_table: txts_table[3])  # , txts_table.biblio))

        # add every ref-ing title to the current result (title) object
        for bibinfo, texts_tuples_sub_group in group_by_number_n_bibinfo:
            numbers_dict[title_number][bibinfo]: List[txts_table] = []
            res.add_bib(bibinfo)  # 8255
            for gg in texts_tuples_sub_group:
                txt_entry = m.TextText(number=gg[0],
                                       ref=gg[1],
                                       subject=gg[2],
                                       biblio=gg[3],
                                       page=gg[4],
                                       C=gg[5])
                numbers_dict[title_number][bibinfo].append(txt_entry)
                res.add_page(page=gg[4], bibinfo=gg[3])
                res.add_refs(ref=gg[1], bibinfo=gg[3])

        res_dict[title_number] = res
        if len(res.books_dict) > 1:
            highly_valid.append(res)  # categories[0]['results'].append(res)
        elif len(res.refs) > 1:
            # elif len(res.pages) > 1:
            valid.append(res)
        else:
            not_valid.append(res)

    categories[0]['results'] = sorted(highly_valid, key=lambda result: len(result.books_dict), reverse=True)
    categories[1]['results'] = sorted(valid, key=lambda result: len(result.refs), reverse=True)
    categories[2]['results'] = not_valid

    return render_template('search_results.html',
                           title=f'Search Result for: {search_word}',
                           description=f'Tiresias: The Ancient Mediterranean Religions Source Database. '
                                       f'This page shows results for {search_word}, sorted by validity.',
                           search_bar=search_bar,
                           categories=categories,
                           search_word=search_word,
                           results_num=len(highly_valid) + len(valid) + len(not_valid),
                           )

    # todo
    #  add fuzzy (returns things *like* but not necessarily the same) / regex search on the query
    #  clean data before:
    #    split creation of tables function in db-migration into multiple function
    #    appropriate normalization

    # for k, g in groupby(session.query(Stuff).order_by(Stuff.column1, Stuff.column2), key=lambda stuff: stuff.column1):
    #     print('{}: {}'.format(k, ','.join(stuff.column2 for stuff in g)))


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
# @app.route('/subject-list', methods=['GET', 'POST'])
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
@app.route('/page-not-found')
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
def csv_to_mysql_func_btn():
    print("It's happening... ")
    from time import time
    t = time()
    from db_migration import csv_to_mysql
    csv_to_mysql()
    print("Time elapsed: " + str(time() - t) + " s.")
    return '<h1> A O K </h1>'
