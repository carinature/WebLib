from flask import current_app as app, flash, g, session
from flask import render_template, make_response, redirect, url_for, request

from time import time

from sqlalchemy import or_
from wtforms import BooleanField


# from . import forms as f


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


