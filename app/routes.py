from datetime import time
from typing import List

from flask import current_app as app
from flask import flash
from flask import render_template, make_response, redirect, url_for, request

from db_migration import csv_to_mysql
from .forms import *
from .models import *

print('~' * 113)


# ++++++++++++  search results and filtering page ++++++++++++
@app.route('/search-results/<string:search_word>', methods=['GET', 'POST'])
@app.route('/search-results', methods=['GET', 'POST'])
def search_results(search_word=''):
    flash('You doing great GRRRLLLL')

    # search_word = search_word if search_word else request.args['search_word']
    print(search_word)
    if 'GET' == request.method:
        # print(request.args)
        # print(request.values)
        # print(request)
        # flash('You \'GET\' this')
        # print('get')
        # print(request.args['results'])
        # results = request.args['results']
        # return render_template('search-results.html', results=results)

        subject_form = SearchSubject(request.form)
        reference_form = SearchReference(request.form)
        filter_form = FilterForm(request.form)

        return render_template('search-results.html', title=f'Search Results for: {search_word}',
                               description="Tiresias: The Ancient Mediterranean Religions Source Database",
                               results=['res1', 'res2', 'res3', 'res4'], total=0,
                               form1=subject_form, form2=reference_form, form3=filter_form,
                               )  # , results=results)

    flash('You\'re \'POST\' on!')
    print('post')
    # print(request.args['results'])
    # results = request.args['results']
    return render_template('search-results.html', title=f'Search Result for: {search_word}',
                           description="Tiresias: The Ancient Mediterranean Religions Source Database",
                           results=['pupu'], total=0)

    # todo
    #  in the search-results do
    #    consider running the functions in "search-result" and NOT "home"
    #    make some sort "waiting" bar/circle/notification (search "flashing/messages" in the flask doc)
    #  change projection to include entire entry instead of index alone
    #  add fuzzy (returns things *like* but not necessarily the same) / regex search on the query
    #  clean data before:
    #    split creation of tables function in db-migration into multiple function
    #    appropriate normalization


# ++++++++++++  Home page ++++++++++++
@app.route('/', methods=['GET', 'POST'])
def home():
    if 'GET' == request.method:
        print('INDEX - GET')
        subject_form = SearchSubject(request.form)
        reference_form = SearchReference(request.form)
        filter_form = FilterForm(request.form)
        radio = SearchTypeChoice(request.form)
        return render_template('index.html',
                               title="Tiresias: The Ancient Mediterranean Religions Source Database",
                               description="Tiresias: The Ancient Mediterranean Religions Source Database",
                               form1=subject_form, form2=reference_form, form3=filter_form, radio=radio
                               )

    form_fields = [
        "search-subject",
        "second-keyword",
        "search-author",
        "search-work",
        "search-reference"
    ]

    # for i in range(len(fields)):
    #     if fields[i] in request.form:
    #         print()
    # print(request.form.get(fields[i]))

    print(request.form.to_dict())
    search_word = request.form[form_fields[0]] if (form_fields[0] in request.form) else None
    # second_keyword = request.form[fields[2]] if (fields[2] in request.form) else None
    # search_author = request.form[fields[2]] if (fields[2] in request.form) else None
    # search_work = request.form[fields[2]] if (fields[2] in request.form) else None
    search_reference = request.form[form_fields[2]] if (form_fields[2] in request.form) else None
    new_result: List[TextSubject] = []

    if search_word:  # the search by Subject button was clicked
        if search_word == "":
            pass  # todo handle "empty searches"
        results = TextSubject.query.filter(TextSubject.subject.like(search_word)).paginate(1, 1, False).items
        for result in results:
            new_result.append(result)
            print('result.subject: ', result.subject, '\nres: ', result, '\nnew_result: ', new_result)
    elif search_reference:
        pass
    else:  # the search by Reference button was clicked
        # if search_reference == "":
        # resp.headers['X-Something'] = 'A value'
        pass  # todo handle "empty searches"

    # return redirect(url_for("search_results"))
    return redirect(url_for("search_results", search_word=search_word))
    # return redirect(url_for("search_results", results=results), code=307) #https://stackoverflow.com/questions/15473626/make-a-post-request-while-redirecting-in-flask #todo DO NOT DELTEE BEFORE YOU CHECKOUT
    # return redirect('/search_results', results)


# ++++++++++++  list of books page ++++++++++++
@app.route('/book-indices')
def book_indices():
    print('whaaaaaaa..?')
    return render_template('book-indices.html',
                           title="Books Included in the Tiresias Project Database",  # todo different title
                           description="Tiresias: The Ancient Mediterranean Religions Source Database", )


# ++++++++++++  list of "subjects" in the db page ++++++++++++
@app.route('/subject-list')
def subject_list():
    t = time()

    page = request.args.get('page', 1, type=int)
    subjects = TextSubject.query.paginate(page, app.config['SUBJECTS_POSTS_PER_PAGE'], False)
    # there is not enough memory to do the next, but maybe consider the idea
    # subjects = TextSubject.query.order_by(
    #   TextSubject.subject.asc()).paginate(page, app.config['SUBJECTS_POSTS_PER_PAGE'], False)
    next_url = url_for('subject_list', page=subjects.next_num) if subjects.has_next else None
    prev_url = url_for('subject_list', page=subjects.prev_num) if subjects.has_prev else None

    return render_template('subject-list.html',
                           title="Tiresias Subjects",  # todo different title
                           description="Tiresias: The Ancient Mediterranean Religions Source Database",
                           subjects=subjects, total=subjects.total,
                           next_url=next_url,
                           prev_url=prev_url
                           )


# ++++++++++++  dbg pages ++++++++++++
@app.route('/check', methods=['GET', 'POST'])
def check_check():
    subject_form = SearchSubject(request.form)
    # reference_form = SearchReference(request.form)
    # if subject_form.submit_subject.data and subject_form.validate_on_submit():
    #     print('Great Success')
    #     return redirect(url_for('success', title='subject_form'))
    # if reference_form.submit_reference.data and reference_form.validate_on_submit():
    #     print('Great Success')
    #     return redirect(url_for('success', title='reference_form'))
    #     # return render_template('kaka.html', title='Great Success', subject_form=subject_form)
    # print('what happend')
    # print("subject_form.errors")
    # print(subject_form.errors)
    # flash(subject_form.errors)
    # page = request.args.get('page', 1, type=int)
    # table = TextSubject.query.paginate(page, app.config['POSTS_PER_PAGE'], False).items
    # return render_template('kaka.html',mydata=table, form1=subject_form)  # , form2=reference_form)
    return render_template('kaka.html', form1=subject_form)  # , form2=reference_form)


@app.route("/kaka", methods=['GET', 'POST'])
def kaka():
    # headers = {"Content-Type": "app/kaka"}
    # return make_response(
    #     'Test worked!',
    #     200,
    #     headers
    # )

    return render_template('kaka.html')


@app.route("/pipi", methods=['GET', 'POST'])
def pipi():
    csv_to_mysql()
    return 'OK'
    # return render_template('kaka.html', form1=subject_form)  # , form2=reference_form)


@app.route("/success/<title>", methods=['GET', 'POST'])
def success(title):
    sform = SearchSubject()
    return '<h1>' + title + ' Great Success</h1>'
    # return render_template('kaka.html', title='Great Success', sform=sform)


# ++++++++++++  Error Handling ++++++++++++
@app.errorhandler(404)
def not_found(error):
    resp = make_response(render_template('page_not_found.html',
                                         title="Tiresias Project - Page not Found",
                                         description=str(error)), 404)
    print(error)
    return resp

# @login_required https://flask-login.readthedocs.io/en/latest/ todo use this to protect from logged-off users
# @app.route('/insert-data')
# def insert_data():
#     print('congrats on the new addition')
