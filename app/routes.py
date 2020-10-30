from datetime import time
from itertools import groupby
from typing import List, Dict, Tuple

from flask import current_app as app
from flask import render_template, make_response, redirect, url_for, request
from sqlalchemy import func
from sqlalchemy.orm import Query
from sqlalchemy.sql.functions import count
from wtforms import BooleanField, StringField
from wtforms.widgets import CheckboxInput

from db_migration import csv_to_mysql

from . import forms as f
from . import models as m
from . import utilities as utils

print('~' * 80)


# ++++++++++++  final (filtered) results page ++++++++++++
@app.route('/results', methods=['GET', 'POST'])
def final_results(search_word='', page=''):
    categories = [
        {'name': 'Highly Validated',
         'results': [
             {'title': 'title',
              'author': 'Author',
              'ref_num': 'ref_num',
              'refs': 'refs'
              }
         ]
         },
        {'name': 'Validated',
         'results': [
             {'title': 'title',
              'author': 'Author',
              'ref_num': 'ref_num',
              'refs': 'refs'
              }
         ]
         },
        {'name': 'Unvalidated',
         'results': [
             {'title': 'title',
              'author': 'Author',
              'ref_num': 'ref_num',
              'refs': 'refs'
              }
         ]
         }
    ]
    search = '%{}%'.format('woman')
    # search = '%{}%'.format('divination')

    # todo this shoult be replaced by results from the previous page

    # ---------------------------------------------------------------------
    # -------- search subject in TextSubject, return C (list) ------------
    # -------------------------------------------------------------------
    # print('@' * 20)
    # table: m.Base = m.TextSubject
    # subject_col = m.TextSubject.subject
    # C_col = m.TextSubject.C
    # Csum_col = m.TextSubject.Csum
    # txt_subj_query: Query = m.TextSubject.query
    # # ............  return C (list)
    # # q_with_ent: Query = txt_subj_query.with_entities(subject_col, count())
    # q_with_ent: Query = txt_subj_query
    # q_with_ent_filter: Query = q_with_ent.filter(subject_col.like(search))
    # q_with_ent_filter_group: Query = q_with_ent_filter
    # # q_with_ent_filter_group: Query = q_with_ent_filter.group_by(subject_col)
    # q_with_ent_filter_group_order: Query = q_with_ent_filter_group.order_by(Csum_col.desc())
    # # print('\ntable:\n', table)
    # # print('\nsubject_col:\n', subject_col)
    # # print('\nC_col:\n', C_col)
    # # print('\ntxt_subj_query:\n', txt_subj_query)
    # # print('\nq_with_ent:\n', q_with_ent)
    # # print('\nq_with_ent_filter:\n', q_with_ent_filter)
    # # print('\nq_with_ent_filter_group:\n', q_with_ent_filter_group)
    # # print('\nq_with_ent_filter_group_order:\n', q_with_ent_filter_group_order)
    #
    # subjects = q_with_ent_filter_group_order.all()
    # subjects_clists = []
    # for subject in subjects:
    #     temp_clist = str(subject.C).split(',')
    #     clist: List[str] = []  # splitting the C list into single Cs
    #     for i in range(len(temp_clist)):
    #         c = temp_clist[i]
    #         if '-' in c:
    #             cc = c.split('-')
    #             for i in range(int(cc[0]), int(cc[1]) + 1):
    #                 clist.append(i)
    #         else:
    #             clist.append(int(c))
    #     # print(clist)
    #     subjects_clists.append(clist)
    # # print(subjects_clists)
    # # if subject.Csum == len(clist):
    # #     print('#'*20)
    # #     print(temp_clist)
    # #     print(clist)
    # #     print(subject.Csum)
    #
    # # for c in clist:

    # ---------------------------------------------------------------
    # ---------------  search subject in TextText -------------------
    # ---------------------------------------------------------------
    txts_table = m.TextText
    txts_subject_col = txts_table.subject
    txts_C_col = txts_table.C
    num_col = txts_table.number
    ref_col = txts_table.ref
    bib_info_col = txts_table.book_biblio_info
    page_col = txts_table.page

    # ............  return C (list)
    texts_query: Query = txts_table.query
    # txts_q_with_ent: Query = texts_query.with_entities(txts_subject_col, count(txts_subject_col),
    # txts_q_with_ent: Query = texts_query.with_entities(num_col, txts_subject_col, ref_col, count(bib_info_col), page_col)  # count())
    txts_q_with_ent: Query = texts_query.with_entities(
        num_col, ref_col,
        txts_subject_col,
        bib_info_col,
        page_col,
        txts_C_col)  # count()) fixme remove C_col in production
    txts_q_with_ent_filter: Query = txts_q_with_ent.filter(txts_subject_col.like(search))
    # txts_q_with_ent_filter_group: Query = txts_q_with_ent_filter.group_by(txts_num_col, txts_subject_col)
    # txts_q_with_ent_filter_group_order: Query = txts_q_with_ent_filter_group.order_by(num_col, bib_info_col)
    # needs to be ordered for the itertools.groupby() later on,
    #   since it collects together CONTIGUOUS items with the same key.
    # todo consider doing the order by bib_info_col after groupby(by num_col)
    txts_q_with_ent_filter_order: Query = txts_q_with_ent_filter.order_by(num_col)  # , bib_info_col)
    numbers_dict: Dict = {}
    res_dict: Dict = {}

    groups_by_number = groupby(
        txts_q_with_ent_filter_order,
        key=lambda txts_table: (txts_table.number))  # , txts_table.book_biblio_info))

    for title_number, texts_tuples_group in groups_by_number:
        # resdict[k]=[txts_table for txts_table in g]
        numbers_dict[title_number]: Dict = {}
        print('@' * 33, title_number)

        res = m.ResultByNum(title_number)
        res_dict[title_number] = res
        print('@' * 13, res)

        # TODO note that after the next line (sorted()) - texts_tuples_group NO LONGER EXISTS
        #   maybe it's better to use order_by of sql (if slower)
        texts_tuples_group_ordered = sorted(texts_tuples_group, key=lambda x: x[3])
        group_by_number_n_bibinfo = groupby(
            texts_tuples_group_ordered,  #
            key=lambda txts_table: txts_table[3])  # , txts_table.book_biblio_info))

        # for k, g in groups_by_number:
        for bibinfo, texts_tuples_sub_group in group_by_number_n_bibinfo:
            print('o' * 13, bibinfo, texts_tuples_sub_group)
            print('o' * 13, res)
            # j = 0
            numbers_dict[title_number][bibinfo]: List[txts_table] = []
            print('*' * 13, bibinfo)
            res.add_bib(bibinfo)
            print('*' * 13, res)
            # 8255
            for gg in texts_tuples_sub_group:
                txt_entry = m.TextText(number=gg[0],
                                       ref=gg[1],
                                       subject=gg[2],
                                       book_biblio_info=gg[3],
                                       page=gg[4],
                                       C=gg[5])
                numbers_dict[title_number][bibinfo].append(txt_entry)
                res.add_refs(ref=gg[1],  bibinfo=gg[3])
                res.add_page(page=gg[4], bibinfo=gg[3])
                # res.add_refs(ref=gg[1], bibinfo=int(float(gg[3])))
                # print('\t\t\t', numbers_dict[title_number][bibinfo][j])
                # j+=1

        print('_' * 13, res)
            # print(numbers_dict[title_number][bibinfo])

            # for gg in resdict[k]:
            # print('\t\t', j, '. ', gg)
            # j += 1
        # print(numbers_dict[title_number])

    # print([gg for gg in g])
    # resdict2[k] = list(thelist)
    # print('{}: {}'.format(k, '\n\t\t'.join( thelist)))
    # print('{}: {}'.format(k, '\n\t\t'.join(txts_table.subject for txts_table in g)))
    # print('-' * 20)
    # print(k, g)
    # print('.' * 20)
    # print(k, resdict[k])

    # for k, g in groupby(session.query(Stuff).order_by(Stuff.column1, Stuff.column2), key=lambda stuff: stuff.column1):
    #     print('{}: {}'.format(k, ','.join(stuff.column2 for stuff in g)))

    # return str(scalar + '              ' + txts_q_with_ent_filter_group_order + '           ' + scalar)

    # print('\ntxts_subject_col:\n', txts_subject_col)
    # print('\ntxts_C_col:\n', txts_C_col)
    # print('\ntxts_subject_col:\n', txts_subject_col)
    # print('\ntexts_query:\n', texts_query)
    # print('\ntxts_q_with_ent_filter:\n', txts_q_with_ent_filter)
    # print('\ntxts_q_with_ent_filter_group:\n', txts_q_with_ent_filter_group)
    # print('\ntxts_q_with_ent_filter_group_order:\n', txts_q_with_ent_filter_group_order)
    #
    #
    # results = txts_q_with_ent_filter_group_order.all()
    #
    # # result_clists = subjects_clists
    # # res_dict: Dict = {}
    # # for i in range(len(results)):
    # #     res_dict[results[i].subject] = result_clists[i]
    # #     # for c in result_clists[i]:
    #
    #

    # print('\t\t\t', numbers_dict[title_number][bibinfo][j])

    # for num, dic in numbers_dict.items():
    #     # q_title: Query = m.Title.query
    #     # q_title_filter: Query = q_title.filter(m.Title.number == num)
    #     # title = q_title_filter.value(m.Title.title)
    #     # author = q_title_filter.value(m.Title.author)
    #     # print('=' * 16, num, ' - ', title, ' -- ', author)
    #     # res = m.ResultByNum(num)
    #     # print(res)
    #     for bibinfo, biblist in dic.items():
    #         # q_book_ref: Query = m.BookRef.query
    #         # q_book_ref_filter: Query = q_book_ref.filter(m.BookRef.book_biblio_info == int(float(bibinfo)))
    #         # titleref = q_book_ref_filter.value(m.BookRef.titleref)
    #         # page = biblist.page
    #         # print('-' * 16, bibinfo, ' - ', titleref, 'page')
    #         print('-' * 16, bibinfo)
    #         for book in biblist:
    #             print('\t', book)

    # lst = []
    # for s in len(texts_tuples_group.sort(key=lambda x: x[3])):
    #     lst[s] = texts_tuples_group[s]
    # sorted(lst, key=lambda x: x[3])
    # print(lst)
    #
    # print('lst'*5)
    # print(lst)
    # for k, g in lst:
    #     print(k)
    #     print('----------')
    #     print(g)
    #     print('.........')

    # return str(txts_q_with_ent_filter_order)
    return render_template('full-results.html',
                           # title='Final Results',
                           description="Tiresias: The Ancient Mediterranean Religions Source Database",
                           categories=categories,
                           results=numbers_dict,
                           # result_clists=result_clists,
                           # res_dict = res_dict
                           )


# ++++++++++++  search results and filtering page ++++++++++++
# @app.route('/search-results/<string:search_word>/<int:page>', methods=['GET', 'POST'])
# @app.route('/search-results/<int:page>', methods=['GET', 'POST'])
@app.route('/search-results/<string:search_word>', methods=['GET', 'POST'])
@app.route('/search-results', methods=['GET', 'POST'])
def search_results(search_word='', page=''):
    print('.' * 13)
    print(page)

    # todo put here the "waiting" bar/circle/notification (search "flashing/messages" in the flask doc)
    search_bar: Dict = utils.init_search_bar()
    subject_form = search_bar['subject_form']
    filter_form = search_bar['filter_form']

    if not subject_form.validate_on_submit():
        return render_template('search-results.html',
                               title='',
                               # description="Tiresias: The Ancient Mediterranean Religions Source Database",
                               results=[],
                               total=0,
                               search_bar=search_bar
                               )

    # if 'GET' == request.method:
    # if not subject_form.validate_on_submit():
    #     print('-' * 13, ' GET ', '-' * 13)
    #     if not search_word:
    #         print('=' * 13)
    #         print('not search_word')
    #     print('^' * 13, ' not validated on submit ', '^' * 13)
    #     print('^' * 13, search_word, '^' * 13)
    #     print('^' * 13, page, '^' * 13)
    #     redirect(url_for('not_found'))

    print('-' * 13, ' POST ', '-' * 13)
    search_word = subject_form.subject_keyword_1.data
    # print(search_word)
    # print(search_bar['subject_form'].subject_keyword_1.raw_data)

    # search = f'%{search_word}%'
    search = '%{}%'.format(search_word)
    page = request.args.get('page', 1, type=int)
    subjects_query: Query = m.TextSubject.query
    subjects_filter: Query = subjects_query.filter(m.TextSubject.subject.like(search))
    subjects_ordered: Query = subjects_filter.order_by(m.TextSubject.Csum.desc())
    print('.' * 13)
    # print(request.args['results'])
    # results = request.args['results']

    # subjects = subjects_ordered.paginate(page, app.config['ITEMS_PER_PAGE'], False)
    # next_url = url_for('search_results', search_word=search_word, page=subjects.next_num) if subjects.has_next else None
    # prev_url = url_for('search_results', search_word=search_word, page=subjects.prev_num) if subjects.has_prev else None

    subjects = subjects_ordered.all()
    return render_template('search-results.html', title=f'Search Result for: {search_word}',
                           # description="Tiresias: The Ancient Mediterranean Religions Source Database",
                           method='post',
                           results=subjects,
                           total=len(subjects),
                           # results=subjects.items,
                           # total=len(subjects_filter.all()),
                           search_bar=search_bar,
                           # next_url=next_url,
                           # prev_url=prev_url,
                           search_word=search_word
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
@app.route('/page-not-found')
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


@app.template_filter("clean_date")
def clean_date(dt):
    return dt.strftime("%d %b %Y")


@app.template_filter("value_or_zero")
def value_or_zero(val):
    return val if val else 0


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
