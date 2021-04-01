from flask import current_app as app, flash, g, session
from flask import render_template, make_response, redirect, url_for, request

from time import time

from sqlalchemy import or_
from wtforms import BooleanField

from . import forms as f
from . import models as m
from flask_sqlalchemy import BaseQuery
from sqlalchemy.orm import Query
from typing import List, Dict, Tuple

links = {
    'home'       : '/',
    'search'     : '/search-results',
    'test_search': '/test-search-results',
    'books'      : '/book-indices',
    'subjects'   : '/subject-list',
    }

# ++++++++++++  search results and filtering page ++++++++++++
@app.route('/test-search-results', methods=['GET', 'POST'])
def search_test():
    print('#'*34)
    from time import time
    t_total = time()  # for logging
    filter_form = f.FilterForm().return_as_dict()

    # search = '%{}%'.format('freedwoman')
    search = '%{}%'.format('divin')
    # search = '%{}%'.format('women')
    from_century = filter_form['from_century']
    to_century = filter_form['to_century']
    # language = 'Latin'
    language = filter_form['language']
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

#
# # ++++++++++++  search results and filtering page ++++++++++++
# @app.route('/test-search-results', methods=['GET', 'POST'])
# def search_test():
#     print('#'*34)
#     from time import time
#     t_total = time()  # for logging
#
#     from flask_wtf import FlaskForm
#     search_bar: Dict[str, FlaskForm] = utils.init_search_bar()
#     subject_form: f.SearchSubject = search_bar['subject_form']
#     filter_form: f.FilterForm = search_bar['filter_form']
#     print(filter_form.return_as_dict())
#
#     if not subject_form.validate_on_submit():  # i.e. when method==GET
#         return render_template('search_results.html',
#                                title='Search',
#                                description="Tiresias: The Ancient Mediterranean Religions Source Database. "
#                                            "Default search page.",
#                                search_bar=search_bar,
#                                method='get'
#                                )
#
#     search_word = subject_form.subject_keyword_1.data
#     search = '%{}%'.format(search_word)
#     # search = '%{}%'.format('freedwoman')
#     # search = '%{}%'.format('divin')
#     # search = '%{}%'.format('women')
#     filter_form = f.FilterForm().return_as_dict()
#     from_century = filter_form['from_century']
#     to_century = filter_form['to_century']
#     # language = 'Latin'
#     language = filter_form['language']
#     ancient_author = filter_form['ancient_author']
#     ancient_title = filter_form['ancient_title']
#     reference = filter_form['reference']
#
#     # ............  return all matching results (subjects) by C column [list] ............
#     txts_query: BaseQuery = m.TextText.query
#     # filter by subject (and reference if ref_filter field in form is filled out)
#     txts_q_filter: BaseQuery = txts_query.filter(m.TextText.subject.like(search))
#     txts_q_filter = txts_q_filter.filter_by(ref=reference) if reference else txts_q_filter
#
#     # filtered_sub_query: Query = txts_q_filter.subquery()
#
#     # # group by title and then by bib_info (referencing book) and count refs (C's)
#     # sub_q_title_and_bibinfo_with_count = txts_query.with_entities(
#     #     # filtered_sub_query.c.number,
#     #     filtered_sub_query.c.number,
#     #     filtered_sub_query.c.biblio,
#     #     count().label('count_c')
#     # )
#     # groups_by_title_bibinfo = sub_q_title_and_bibinfo_with_count.group_by(
#     #     filtered_sub_query.c.number,
#     #     filtered_sub_query.c.biblio)
#     # grouped_sub_query: Query = groups_by_title_bibinfo.subquery()
#     # # filter by subject and count ref-books
#     # sub_q_title_bibcount = txts_query.with_entities(
#     #     grouped_sub_query.c.number,
#     #     count().label('count_bib')
#     # )
#     # groups_by_title = sub_q_title_bibcount.group_by(grouped_sub_query.c.number)
#     # highly_valid, valid, not_valid = List[m.ResultTitle], List[m.ResultTitle], List[m.ResultTitle]
#     # bib_more_than_1, bib_only_1 = {}, {}
#     # print(txts_q_filter)
#
#     # x: m.TextText
#     # for x in txts_q_filter:
#     #     print(type(x))
#     #     print(x)
#     #     title_key = x.number
#     #     res_title: m.ResultTitle = res_dict.setdefault(title_key, m.ResultTitle(title_key, filter_form))
#
#     # df: pd.DataFrame = pd.read_sql(txts_q_filter.statement, txts_q_filter.session.bind)
#     # print(df.tail())
#     #
#     # groups_by_title_num: pd.DataFrame.groupby.DataFrameGroupBy = df.groupby(
#     #     by=['number'],  # ,'biblio'],  # Notice that a tuple is interpreted as a (single) key.
#     #     # level=0,
#     #     # as_index=False,  # is effectively “SQL-style” grouped output.
#     #     # sort=True,
#     # )
#     # lists_by_title_num = groups_by_title_num.apply(list)
#     #
#     # title_key: str
#     # titles_group: pd.DataFrame
#     # for title_key, titles_group in groups_by_title_num:
#     #     # print(type(titles_group))
#     #     groups_by_title_and_bib: pd.DataFrame.groupby.DataFrameGroupBy = titles_group.groupby(
#     #         by=['biblio'])
#     #     res_title: m.ResultTitle = res_dict.setdefault(title_key, m.ResultTitle(title_key, filter_form))
#     #     if not res_title.filtered_flag:
#     #         continue
#     #     bib_count = len(titles_group['biblio'].unique())
#     #     # print(bib_count)
#     #     if 2> bib_count:
#     #         continue
#     #     bib_info: str
#     #     bib_info_group: pd.DataFrame
#     #     for bib_info, bib_info_group in groups_by_title_and_bib:
#     #         # print('-------\n', bib_info)
#     #         # print('-------\n', bib_info_group)
#     #         res_bib = res_title.books_dict.setdefault(bib_info, res_title.add_bib(bib_info))
#     #         # res_title.add_bib(bib_info)
#     #     highly_valid.append(res_title)
#
#     # print('sr' * 33)
#     # for sr, gr in res_dict.items():
#     #     print(sr)
#     #     print(gr)
#
#     # highly_valid.append(bib_more_than_1)
#     # valid.append(bib_only_1)
#
#     q_title_filter = txts_q_filter.join(m.Title)
#
#     if from_century:
#         q_title_filter: Query = q_title_filter.filter(m.Title.centstart >= from_century)
#     if to_century:
#         q_title_filter: Query = q_title_filter.filter(m.Title.centend <= to_century)
#     if language:
#         q_title_filter: Query = q_title_filter.filter(m.Title.lang == language)
#     if ancient_author:
#         q_title_filter: Query = q_title_filter.filter(m.Title.author == ancient_author)
#     if ancient_title:
#         q_title_filter: Query = q_title_filter.filter(m.Title.title == ancient_title)
#
#     res_dict: Dict[int, m.ResultTitle] = {}
#     highly_valid: List[m.ResultTitle] = []
#     valid: List[m.ResultTitle] = []
#     not_valid: List[m.ResultTitle] = []
#
#     res_tit: m.TextText
#     for res_tit in q_title_filter:
#         res_title: m.ResultTitle = res_dict.setdefault(
#                 res_tit.number,
#                 m.ResultTitle(res_tit.number,
#                               res_tit.title.title,
#                               res_tit.title.author))
#
#         res_title.add_bib(res_tit.book_ref)
#
#     highly_valid = sorted(res_dict.values(), key=m.ResultTitle.num_ref_books, reverse=True)
#     # print(res_dict)
#
#     for k, res in res_dict.items():
#         # print(k)
#         # print(res)
#         if len(res.books_dict) > 1:
#             highly_valid.append(res)  # categories[0]['results'].append(res)
#         elif len(res.refs) > 1:
#             # elif len(res.pages) > 1:
#             valid.append(res)
#         else:
#             not_valid.append(res)
#
#     print('=' * 12 + ' Total Time elapsed: ' + str(time() - t_total) + ' s.')
#
#
#     categories[0]['results'] = sorted(highly_valid, key=lambda result: len(result.books_dict), reverse=True)
#     categories[1]['results'] = sorted(valid, key=lambda result: len(result.refs), reverse=True)
#     categories[2]['results'] = not_valid
#
#     # 6276 for number and 15 & 31 for bub-info  || 8255 and 31.0 & 64.0
#     # return render_template('dbg/test_search.html',
#     #                        motototo=['Nothing', 'worth', 'having', 'comes', 'easy'],
#     #                        # list1=highly_valid,
#     #                        # list2=valid,
#     #                        list1=highly_valid,
#     #                        dict2=res_dict,
#     #                        )
#
#     return render_template('search_results.html',
#                            title=f'Search Result for: {search_word}',
#                            description=f'Tiresias: The Ancient Mediterranean Religions Source Database. '
#                                        f'This page shows results for {search_word}, sorted by validity.',
#                            search_bar=search_bar,
#                            categories=categories,
#                            search_word=search_word,
#                            results_num=len(highly_valid) + len(valid) + len(not_valid),
#                            )

@app.route('/submitmail', methods=['GET', 'POST'])
def submit_mail():
    print('-.' * 33, ' submitmail function')
    # print('It's happening... ')

    return '<h1> A O K </h1>'
    # return render_template('dbg/bar_srchbr.html', avoid_robots=True, form1=f.SignupForm())


# ++++++++++++  DGB and Testing ++++++++++++
@app.route('/try_jinja')
def try_jinja():
    # Strings
    _str = 'Julian'

    # Integers
    _int = 30

    # Lists
    _list = ['Python', 'JavaScript', 'Bash', 'Ruby', 'C', 'Rust']

    # Dictionaries
    _dict = {
        'Tony': 43,
        'Cody': 28,
        'Amy': 26,
        'Clarissa': 23,
        'Wendell': 39
    }

    # Tuples
    _tuple = ('Red', 'Blue')

    # Booleans
    _bool = True

    # Classes
    class _class:
        def __init__(self, name, description, domain):
            self.name = name
            self.description = description
            self.domain = domain

        def pull(self):
            return f'Pulling repo "{self.name}"'

        def clone(self, repo):
            return f'Cloning into {repo}'

    _class_obj = _class(
        name='The Name',
        description='Some short description',
        domain='https://github.com/something-something.git'
    )

    # Functions
    def _function(x, qty=1):
        return x * qty

    from datetime import datetime
    date = datetime.utcnow()

    my_html = '<h1>This is some HTML</h1>'

    return render_template(
        'dbg/try_jinja.html', avoid_robots=True, _str=_str, _int=_int, _list=_list,
        _dict=_dict, _tuple=_tuple, _bool=_bool, _class=BooleanField,
        _class_obj=_class_obj, _function=_function, date=date,
        my_html=my_html
    )


@app.route('/try_bs', methods=['GET', 'POST'])
def try_bs():
    # headers = {'Content-Type': 'app/kaka'}
    # return make_response(
    #     'Test worked!',
    #     200,
    #     headers
    # )
    from flask import flash
    flash('mamase mamasa mamakusa')
    return render_template('dbg/try_bs.html', avoid_robots=True, title='TRY', range=range(25), load_db_flag=False)


# ++++++++++++  Login ++++++++++++
# @login_required https://flask-login.readthedocs.io/en/latest/ todo use this to protect from logged-off users
# @app.route('/insert-data')
# def insert_data():
#     print('congrats on the new addition')


# ++++++++++++  dbg pages ++++++++++++
@app.route('/check', methods=['GET', 'POST'])
def check_check():
    # subject_form = f.PurchaseForm(fdict)
    # reference_form = SearchReference(request.form)
    # if subject_form.submit_subject.data and subject_form.validate_on_submit():
    #     print('Great Success')
    #     return redirect(url_for('success', title='subject_form'))
    # print('what happend')
    # print('subject_form.errors')
    # flash(subject_form.errors)

    if 'GET' == request.method:
        # if not subject_form.validate_on_submit():
        print('-' * 13, ' GET ', '-' * 13)
        return render_template(
            'dbg/check.html',
            avoid_robots=True)  # , form1=subject_form, _list=subjects)#, data=subject_form.example.data)

    print('-' * 13, ' POST ', '-' * 13)

    print('request.values')
    print(request.values)
    print('request.form')
    print(request.form)
    print('getlist')
    print(request.form.getlist('item'))
    print('getlistgetlistgetlist')
    for item in request.form.getlist('item'):
        print(item)
    print('items')
    for item in request.form.items():
        print(item)
    printout = [request.values, request.form, request.form.getlist('item'), request.form.getlist('item'),
                request.form.items()]
    # print('request.data')
    # print(request.data)
    # print('request.args')
    # print(request.args)
    # results = request.args['results']

    return render_template('dbg/check.html', avoid_robots=True,
                           printout=printout)  # , form1=subject_form, _list=subjects)#, data=subject_form.example.data)


# @app.route('/json')
# def json():
#     return render_template('json.html', avoid_robots=True)

# background process happening without any refreshing
@app.route('/bar_srchbr')
def bar_srchbr():
    print('@@' * 33)

    # return render_template('dbg/bar_srchbr.html', avoid_robots=True, form1=f.SearchSubject())
    return '<h1> A O K </h1>'


@app.route('/success/<title>', methods=['GET', 'POST'])
@app.route('/success')
def success(title=''):
    sform = f.SearchSubject()
    # return '<h1>' + title + ' Great Success</h1>'
    return render_template('dbg/bar_srchbr.html', avoid_robots=True, title='Great Success', form1=sform)


@app.route('/falala')
def falalafunc():
    print('=-' * 33, ' falala')
    print('Adding your Email address')

    # csv_to_mysql()
    return '<h1> A O K </h1>'


@app.route('/flask_route_but_not_webpage')
def js_btn_to_python():
    print('##' * 33, ' from_js_btn_to_python function')
    print('It\'s happening... ')
    # csv_to_mysql()

    return '<h1> A O K </h1>'


@app.route('/flam_flam')
def flam_flam():
    print('flam_flam')
    # 6276 has 2 bib-infos   . another option for 'woman' is 8255. also 2 bib-infos
    from . import models as m
    resTitle = m.Title.query.filter_by(number='6276').all()
    resRef = m.BookRef.query.filter(or_(
        m.BookRef.biblio == '15',
        m.BookRef.biblio == '31')).all()
    resTextText = m.TextText.query.filter(or_(
        m.TextText.subject == 'Proverbs, ideal woman',
        m.TextText.subject == 'Martha apocryphal as anointing woman')).all()
    print(resTitle)
    print(resTitle.__repr__())
    for r in resRef:
        print('  ---  ref  --- ', r.__repr__())
        print(r)
    print(resRef)
    # for r in resTextText:
    #     print('  ---  texttext  --- ', r.__repr__())
    # return (resRef) #exception
    return (resRef.__repr__())


