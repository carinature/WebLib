from typing import List

from flask import flash
from flask import render_template, make_response, redirect, url_for, request

from .models import *

import random  # todo remove

from flask import current_app as app

@app.route("/kaka")
def kaka():
    headers = {"Content-Type": "app/kaka"}
    return make_response(
        'Test worked!',
        200,
        headers
    )


@app.route('/', methods=['GET', 'POST'])
def home():
    if 'GET' == request.method:
        print('INDEX - GET')
        return render_template('index.html',
                               title="Tiresias: The Ancient Mediterranean Religions Source Database",
                               description="Tiresias: The Ancient Mediterranean Religions Source Database"
                               )
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
            # resp.headers['X-Something'] = 'A value'
            pass  # todo handle "empty searches"

    # return redirect(url_for("search_results"))
    return redirect(url_for("search_results", search_word=search_word))
    # return redirect(url_for("search_results", results=results), code=307) #https://stackoverflow.com/questions/15473626/make-a-post-request-while-redirecting-in-flask #todo DO NOT DELTEE BEFORE YOU CHECKOUT
    # return redirect('/search_results', results)


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
        return render_template('search-results.html', title=f'Search Results for: {search_word}',
                               description="Tiresias: The Ancient Mediterranean Religions Source Database",
                               results=['pipi'], total=0)  # , results=results)

    flash('You\'re \'POST\' on!')
    print('post')
    # print(request.args['results'])
    # results = request.args['results']
    return render_template('search-results.html', title=f'Search Result for: {search_word}',
                           description="Tiresias: The Ancient Mediterranean Religions Source Database",
                           results=['pupu'], total=0)


# ++++++++++++  list of books page ++++++++++++
@app.route('/book-indices')
def book_indices():
    page = request.args.get('page', 1, type=int)
    ordered_titles = BookRef.query.order_by(BookRef.titleref.asc())
    paginated_titiles = ordered_titles.paginate(page, app.config['POSTS_PER_PAGE'], False)
    return render_template('book-indices.html',
                           title="Books Included in the Tiresias Project Database",  # todo different title
                           description="Tiresias: The Ancient Mediterranean Religions Source Database",
                           titles_list=paginated_titiles.items, total=paginated_titiles.total)


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
    return render_template('subject-list.html',
                           title="Tiresias Subjects",  # todo different title
                           description="Tiresias: The Ancient Mediterranean Religions Source Database",
                           subjects=subjects.items, total=subjects.total)
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


@app.errorhandler(404)
def not_found(error):
    resp = make_response(render_template('page_not_found.html', title="Tiresias Project - Page not Found",
                                         description=str(error)), 404)
    print(error)
    return resp

# @login_required https://flask-login.readthedocs.io/en/latest/ todo use this to protect from logged-off users
# @app.route('/insert-data')
# def insert_data():
#     print('congrats on the new addition')
