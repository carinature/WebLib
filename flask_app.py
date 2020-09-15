from typing import List

from flask import Flask, jsonify, flash
from flask import render_template, make_response, redirect, url_for, request
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Query  # mainly for autocomplete

from utilities.models import *
from config import *
# from config import *
import random  # todo remove

from sqlalchemy.orm import Query


# engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=False, pool_recycle=3600)


@app.route('/', methods=['GET', 'POST'])
def home():
    if 'GET' == request.method:
        print('INDEX - GET')
        return render_template('index.html')
    fields = [
        "search-subject",
        "second-keyword",
        "search-author",
        "search-work",
        "search-reference"
    ]

    for i in range(len(fields)):
        if fields[i] in request.form:
            print()
            # print(request.form.get(fields[i]))

    # todo
    #  - DONE - collect fields
    #  - DONE - depending on which fields/form filled - choose a search function
    #  next page should receive the results of the function as params
    #  like so:         return render_template('search_results', comments=ExampleEntry.query.all())
    #  but first try like this         redirect(url_for("search_results", comments=ExampleEntry.query.all()))

    # todo
    #  create a class for the forms?
    #  you MUST make sure to be safe from SQL injection and other X

    # todo
    #  in the search-results do
    #    change get to render with params
    #    change html to create/fill new data ("you searched for...", "total #results..")
    #    consider running the functions in "search-result" and NOT "home"
    #    make some sort "waiting" bar/circle/notification (search "flashing/messages" in the flask doc)

    # todo
    #  change projection to include entire entry instead of index alone
    #  add fuzzy (returns things *like* but not necessarily the same) / regex search on the query
    #  clean data before:
    #    split creation of tables function in db-migration into multiple function
    #    appropriate normalization

    print(request.form.to_dict())
    search_word = request.form[fields[0]] if (fields[0] in request.form) else None
    search_reference = request.form[fields[2]] if (fields[2] in request.form) else None
    new_result: List[TextSubject] = []

    # db.Session.query(TextSubject).filter().
    # TextSubject.query.
    if search_word:  # the search by Subject button was clicked
        if search_word == "":
            pass  # todo handle "empty searches"
        results = TextSubject.query.filter(TextSubject.subject.like(search_word)).paginate(1, 1, False).items
        for result in results:
            new_result.append(result)
            print('result.subject: ', result.subject, '\nres: ', result, '\nnew_result: ', new_result)

    else:  # the search by Reference button was clicked
        if search_reference == "":
            pass  # todo handle "empty searches"

    return redirect(url_for("search_results", results=results))
    # return redirect(url_for("search_results", results=results), code=307) #https://stackoverflow.com/questions/15473626/make-a-post-request-while-redirecting-in-flask #todo DO NOT DELTEE BEFORE YOU CHECKOUT
    # return redirect('/search_results', results)


@app.errorhandler(404)
def not_found(error):
    resp = make_response(render_template('page_not_found.html'), 404)
    resp.headers['X-Something'] = 'A value'
    print(error)
    return resp

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
# ++++++++++++  search results and filtering page ++++++++++++
@app.route('/search-results', methods=['GET', 'POST'])
def search_results():
    flash('You doing great GRRRLLLL')
    if 'GET' == request.method:
        # print(request.args)
        # print(request.values)
        # print(request)
        flash('You \'GET\' this')
        print('get')
        print(request.args['results'])
        results = request.args['results']
        return render_template('search-results.html', results=[results])
    flash('You\'re \'POST\' on!')
    print('post')
    print(request.args['results'])
    results = request.args['results']
    return render_template('search-results.html')


# ++++++++++++  list of books page ++++++++++++
@app.route('/book-indices')
def book_indices():
    page = request.args.get('page', 1, type=int)
    ordered_titles = BookRef.query.order_by(BookRef.titleref.asc())
    paginated_titiles = ordered_titles.paginate(page, app.config['POSTS_PER_PAGE'], False)
    return render_template('book-indices.html', titles=paginated_titiles.items, total=paginated_titiles.total)


# ++++++++++++  list of "subjects" in tje db page ++++++++++++
@app.route('/subject-list')
def subject_list():
    class SubjectEnum(TextSubject):
        newc = TextSubject.C
        # __tablename__ = 'text_subjects'  # fixme
        # dbg_index = Column(Integer)
        # subject = Column(String(200))
        # C = Column(Text)

        # kaka = newc.__getitem__(1)
        # # pipi = kaka + kaka
        # # newc = pipi
        # newc = kaka
        # def __init__(self):
        #     super.__init__(self)
        #     # newc = TextSubject.C
        #     # self.newc = str(newc) + str(newc)
        #     self.C = self.newc + self.newc

    page = request.args.get('page', 1, type=int)
    subjects = SubjectEnum.query.paginate(page, app.config['POSTS_PER_PAGE'], False)
    return render_template('subject-list.html', subjects=subjects.items, total=subjects.total)
    # return render_template(url_for('subject_list')+'.html')


# ++++++++++++  dbg page ++++++++++++
@app.route('/check', methods=['GET', 'POST'])
def check_check():
    if request.method == 'GET':
        return render_template('check.html', bookrefs=BookRef.query.all())
    print(request.form.get("contents"))
    print(request.form.get("contents2"))
    if "contents2" in request.form:
        field_contents = request.form["contents2"] + " (from 2nd field)"
    else:
        field_contents = request.form["contents"] + " (from 1st field)"
    bookref = BookRef(titleref=field_contents, book_biblio_info=str(random.randint(3, 9)))
    # db.session.add(bookref)
    # db.session.commit()
    return redirect('/check', bookref)
