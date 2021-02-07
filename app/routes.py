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
    {'name': 'Highly Validated',
     'id': 'high',
     'results': [  # {'title': 'title', 'author': 'Author', 'ref_num': 'ref_num', 'refs': 'refs'}
     ]
     },
    {'name': 'Validated',
     'id': 'valid',
     'results': [  # {'title': 'title', 'author': 'Author', 'ref_num': 'ref_num', 'refs': 'refs'}
     ]
     },
    {'name': 'Unvalidated',
     'id': 'not',
     'results': [  # {'title': 'title', 'author': 'Author', 'ref_num': 'ref_num', 'refs': 'refs'}
     ]
     }
]
links = {
    'home': '/',
    'search': '/search-results',
    'test_search': '/test-search-results',
    'books': '/book-indices',
    'subjects': '/subject-list',
}


# ++++++++++++  search results and filtering page ++++++++++++
@app.route(links['test_search'], methods=['GET', 'POST'])
# @app.route('/search-results/<string:search_word>/<int:page>', methods=['GET', 'POST'])
def search_test(search_word='', page=''):
    search = '%{}%'.format('divin')

    txts_table = m.TextText
    # ............  return all matching results (subjects) by C column [list] ............
    txts_query: BaseQuery = txts_table.query

    # filter by subject
    txts_q_filter: BaseQuery = txts_query.filter(txts_table.subject.like(search))
    # txts_q_filter: BaseQuery = txts_q_filter.filter(txts_table.subject.like(search))
    filtered_sub_query: Query = txts_q_filter.subquery()

    # # group by title and then by bib_info (referencing book) and count refs (C's)
    # sub_q_title_and_bibinfo_with_count = txts_query.with_entities(
    #     # filtered_sub_query.c.number,
    #     filtered_sub_query.c.number,
    #     filtered_sub_query.c.book_biblio_info,
    #     count().label('count_c')
    # )
    # groups_by_title_bibinfo = sub_q_title_and_bibinfo_with_count.group_by(
    #     filtered_sub_query.c.number,
    #     filtered_sub_query.c.book_biblio_info)
    # grouped_sub_query: Query = groups_by_title_bibinfo.subquery()
    #
    # # filter by subject and count ref-books
    # sub_q_title_bibcount = txts_query.with_entities(
    #     grouped_sub_query.c.number,
    #     count().label('count_bib')
    # )
    # groups_by_title = sub_q_title_bibcount.group_by(grouped_sub_query.c.number)

    bib_dict: Dict[int, List] = {}

    numbers_dict: Dict = {}
    res_dict: Dict = {}
    highly_valid, valid, not_valid = [], [], []
    bib_more_than_1, bib_only_1 = {}, {}

    print(txts_q_filter)
    df: pd.DataFrame = pd.read_sql(txts_q_filter.statement, txts_q_filter.session.bind)
    print(df.tail())
    dfgroups: pd.DataFrame.groupby.DataFrameGroupBy = df.groupby(
        # by=['number', 'book_biblio_info'],  # Notice that a tuple is interpreted as a (single) key.
        by=['number'],  # Notice that a tuple is interpreted as a (single) key.
        as_index=False,  # is effectively “SQL-style” grouped output.
        sort=True, )
    tit: str
    dfg: pd.DataFrame
    for tit, dfg in dfgroups:
        print('-------\n', tit)
        # dfg.sort(key = lambda x: x[3] ) #todo change x[3] to x.bib_info...
        print('-------\n', type(dfg))
        fin = dfg.groupby(
            by=['book_biblio_info'],
            as_index=False,  # is effectively “SQL-style” grouped output.
        )
        for sg in fin:
            print('-------\n', sg)

    # print('sr' * 33)
    # for sr in groups_by_title:
    #     print(sr)

    # print('res' * 33)
    # for res in filtered_results:
    #     bib_count = res.count_bib
    #     title_number = res.number
    #     if bib_count >= 2:  # todo maybe consider using HAVING instead of an 'if'
    #         print('-' * 30, title_number, '-' * 30, bib_count)
    #         full_res = txts_q_filter.filter(filtered_sub_query.c.number == title_number).all()
    #         bib_more_than_1[title_number] = full_res
    #         # print(full_res)
    #
    #     else:
    #         bib_only_1[title_number] = bib_count

    highly_valid.append(bib_more_than_1)
    valid.append(bib_only_1)
    # print('highly_valid '*5)
    # print(highly_valid)
    # print('bib_only_1 ' * 5)
    # print(bib_only_1)

    # for res in groups_by_title_bibinfo:
    #     print(res)
    #     res_num = res.number  # res[0]
    #     bib_info = res.book_biblio_info  # res[1]
    #     # cc = res.C  # res[2]
    #     bib_dict[res_num] = res_num
    #     # group by title, and then by bib
    #     print(res.number, res_num)
    #     print()
    #     # cc: BaseQuery = txts_query.filter(num_col==res_num).all()
    #     # cc: BaseQuery = txts_query.filter_by(number=res_num).all() # this gives tooo many results - wrong ones
    #     print('cc' * 9)
    #     # print(len(cc))
    #     # print(cc)
    #     print(bib_info)
    #     print('ee' * 9)
    #
    #     # title = m.Title.get(res_num)
    #     # bib_info = m.Title.get(res[1])

    # 6276 of number and 15 & 31 for bub-info
    return render_template('dbg/test_search.html',
                           motototo=['Nothing', 'worth', 'having', 'comes', 'easy'],
                           list1=highly_valid,
                           list2=valid,
                           )


# ++++++++++++  search results and filtering page ++++++++++++
@app.route(links['search'], methods=['GET', 'POST'])
# @app.route('/search-results/<string:search_word>/<int:page>', methods=['GET', 'POST'])
# @app.route('/search-results/<int:page>', methods=['GET', 'POST'])
# @app.route('/search-results/<string:search_word>', methods=['GET', 'POST'])
def search_results(search_word='', page=''):
    # todo put here the "waiting" bar/circle/notification (search "flashing/messages" in the flask doc)

    search_bar: Dict = utils.init_search_bar()
    subject_form = search_bar['subject_form']
    filter_form = search_bar['filter_form']

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
    bib_info_col, ref_col, page_col = txts_table.book_biblio_info, txts_table.ref, txts_table.page
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
        key=lambda txts_table: (txts_table.number))  # , txts_table.book_biblio_info))

    # print('$'*20, )
    # for ke, ge in groups_by_number:
    #     print('#' * 13, ke)
    #     print('^' * 13, list(ge))

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
            key=lambda txts_table: txts_table[3])  # , txts_table.book_biblio_info))

        # add every ref-ing title to the current result (title) object
        for bibinfo, texts_tuples_sub_group in group_by_number_n_bibinfo:
            numbers_dict[title_number][bibinfo]: List[txts_table] = []
            res.add_bib(bibinfo)  # 8255
            for gg in texts_tuples_sub_group:
                txt_entry = m.TextText(number=gg[0],
                                       ref=gg[1],
                                       subject=gg[2],
                                       book_biblio_info=gg[3],
                                       page=gg[4],
                                       C=gg[5])
                numbers_dict[title_number][bibinfo].append(txt_entry)
                res.add_page(page=gg[4], bibinfo=gg[3])
                res.add_refs(ref=gg[1], bibinfo=gg[3])

        res_dict[title_number] = res
        if len(res.books) > 1:
            highly_valid.append(res)  # categories[0]['results'].append(res)
        elif len(res.refs) > 1:
            # elif len(res.pages) > 1:
            valid.append(res)
        else:
            not_valid.append(res)

    categories[0]['results'] = sorted(highly_valid, key=lambda result: len(result.books), reverse=True)
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
