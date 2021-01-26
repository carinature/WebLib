from time import time

from itertools import groupby
from typing import List, Dict, Tuple

from flask import current_app as app, flash, g, session
from flask import render_template, make_response, redirect, url_for, request
from sqlalchemy import func
from sqlalchemy.orm import Query
from sqlalchemy.sql.functions import count
from wtforms import BooleanField, StringField, form
from wtforms.widgets import CheckboxInput

from db_migration import csv_to_mysql

from . import forms as f
from . import models as m
from . import utilities as utils

print('~' * 80)


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
    'books': '/book-indices',
    'subjects': '/subject-list',
}


# ++++++++++++  search results and filtering page ++++++++++++
# @app.route('/search-results/<string:search_word>/<int:page>', methods=['GET', 'POST'])
# @app.route('/search-results/<int:page>', methods=['GET', 'POST'])
# @app.route('/search-results/<string:search_word>', methods=['GET', 'POST'])
@app.route(links['search'], methods=['GET', 'POST'])
def search_results(search_word='', page=''):
    # todo put here the "waiting" bar/circle/notification (search "flashing/messages" in the flask doc)

    search_bar: Dict = utils.init_search_bar()
    subject_form = search_bar['subject_form']
    filter_form = search_bar['filter_form']

    if not subject_form.validate_on_submit():  # i.e. when method==GET
        return render_template('search_results.html',
                               title='Search',
                               # description="Tiresias: The Ancient Mediterranean Religions Source Database",
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

    # print('5' * 33)
    # print(txts_q_with_ent_filter_order)
    # print(txts_q_with_ent_filter.limit(30).all())

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
                           # title=f'Search Result for: {search_word}',
                           description="Tiresias: The Ancient Mediterranean Religions Source Database",
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
                           description='Tiresias: The Ancient Mediterranean Religions Source Database',
                           search_bar=search_bar,
                           email_form=email_form,
                           redirect_flag=True
                           )
    # if 'GET' == request.method:
    #     print('~' * 15, ' home() - GET ', '~' * 15)
    # print('~' * 15, ' home() - POST ', '~' * 15)
    # return redirect(url_for(search_results,search_word))


# ++++++++++++  list of books page ++++++++++++
@app.route(links['books'])
# @app.route('/book-indices')
def book_indices():
    return render_template('book_indices.html',
                           title="Books Included in the Tiresias Project Database",  # todo different title
                           description="Tiresias: The Ancient Mediterranean Religions Source Database", )


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
                               title="Tiresias Subjects",  # todo different title
                               description="Tiresias: The Ancient Mediterranean Religions Source Database",
                               subjects=subjects,
                               total=subjects.total,
                               next_url=next_url,
                               prev_url=prev_url,
                               search_bar=search_bar,
                               hide_filter=True,
                               # redirect_flag=False
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
                           title="Tiresias Subjects",  # todo different title
                           description="Tiresias: The Ancient Mediterranean Religions Source Database",
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
        _dict=_dict, _tuple=_tuple, _bool=_bool, _class=BooleanField,
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
    return render_template('try_bs.html', title='TRY', range=range(25), load_db_flag=False)


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
    # print("subject_form.errors")
    # flash(subject_form.errors)

    if 'GET' == request.method:
        # if not subject_form.validate_on_submit():
        print('-' * 13, ' GET ', '-' * 13)
        return render_template("check.html")  # , form1=subject_form, _list=subjects)#, data=subject_form.example.data)

    print('-' * 13, ' POST ', '-' * 13)

    print("request.values")
    print(request.values)
    print("request.form")
    print(request.form)
    print("getlist")
    print(request.form.getlist('item'))
    print("getlistgetlistgetlist")
    for item in request.form.getlist('item'):
        print(item)
    print("items")
    for item in request.form.items():
        print(item)
    printout = [request.values, request.form, request.form.getlist('item'), request.form.getlist('item'),
                request.form.items()]
    # print("request.data")
    # print(request.data)
    # print("request.args")
    # print(request.args)
    # results = request.args['results']

    return render_template("check.html",
                           printout=printout)  # , form1=subject_form, _list=subjects)#, data=subject_form.example.data)


# @app.route('/json')
# def json():
#     return render_template('json.html')

# background process happening without any refreshing
@app.route('/fetch_results')
def fetch_results():
    print("@@" * 33)

    return render_template('bar_srchbr.html', form1=f.SearchSubject())
    # return '<h1> A O K </h1>'


@app.route("/success/<title>", methods=['GET', 'POST'])
@app.route("/success")
def success(title=''):
    sform = f.SearchSubject()
    # return '<h1>' + title + ' Great Success</h1>'
    return render_template('bar_srchbr.html', title='Great Success', form1=sform)


@app.route('/falala')
def falalafunc():
    print('=-' * 33, ' falala')
    print("Adding your Email address")

    # csv_to_mysql()
    return '<h1> A O K </h1>'


@app.route('/flask_route_but_not_webpage')
def js_btn_to_python():
    print('##' * 33, ' from_js_btn_to_python function')
    print("It's happening... ")
    # csv_to_mysql()

    return '<h1> A O K </h1>'


@app.route("/csv_to_mysql_route", methods=['GET', 'POST'])
def load_db():
    from flask import flash
    flash("If you click on the button below You are about to ask the server to load raw scv files into the mysql DB. ")
    flash("It's gonna take a loooong time to finish (if lucky). ")
    flash("Are you sure you want to do that? ")
    return render_template('csv_to_mysql.html', load_db_flag=True)


@app.route("/csv_to_mysql_func")
def csv_to_mysql_func_btn():
    print("It's happening... ")
    t = time()
    csv_to_mysql()
    print("Time elapsed: " + str(time() - t) + " s.")
    return '<h1> A O K </h1>'


def flam_flam():
    print('flam_flam')


@app.route("/flam")
def flam_bla(place):
    print("-----")
    # print("place: ", place)
    flam_flam()
    return '<h1> A O K </h1>'
