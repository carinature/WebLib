from flask import Flask, jsonify
from flask import render_template, make_response, redirect, url_for, request
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Query  # mainly for autocomplete

from utilities.models import *
from properties import *
import random  # todo remove

app = Flask(__name__)
# Also, just to help in case you’ve made a typo in the code somewhere, add this line just after the line that says
# app = Flask(__name__)
app.config["DEBUG"] = True  # todo fixme remove this in production!!!

app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)  # the type is SQLAlchemy.orm ?


# engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=False, pool_recycle=3600)


@app.route('/', methods=['GET', 'POST'])
# @app.route('/#', methods=['GET', 'POST'])
# @app.route('/index', methods=['GET', 'POST'])
# @app.route('/index#', methods=['GET', 'POST'])
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

    if search_word:  # the search by Subject button was clicked
        if search_word == "":
            pass  # todo handle "empty searches"
        results = db.session.query(TextSubject).filter_by(subject=search_word)

        # texts_subjects2 = texts_subjects1[
        #     texts_subjects1["subject"].str.contains('\\b' + search_word + '\\b', case=False, na=False)]
        # # texts_subjects3 = texts_subjects1[
        #     # texts_subjects1["subject"].str.contains('\\b' + search_word + 's\\b', case=False, na=False)]
        # texts_subjects1 = pd.concat([texts_subjects2, texts_subjects3])
        # subjects = texts_subjects1['subject'].values.tolist()
        # # texts_subjects1["C"] = texts_subjects1["C"].apply(hyphenate)
        # cs = texts_subjects1['C'].values.tolist()
        # ccs = [item for sublist in cs for item in sublist]
        # lccs = len(ccs)
        # pd.set_option('display.max_colwidth', -1)
        # if option == "and":
        #     # d2 = "'%" + get_d_from_form + "%'"
        #     # sql_for_df_sub_d = "SELECT * FROM texts_subjects WHERE subject like " + d2
        #     d_texts_subjects = pd.read_sql_query(sql_for_df_sub_d, db)
        #     d_subjects = d_texts_subjects['subject'].values.tolist()
        #     d_texts_subjects["C"] = d_texts_subjects["C"].apply(hyphenate)
        #     ds = d_texts_subjects['C'].values.tolist()
        #     dds = [item for sublist in ds for item in sublist]

        print(results.all())

    else:  # the search by Reference button was clicked
        if search_reference == "":
            pass  # todo handle "empty searches"

    return redirect(url_for("search_results"), )


@app.errorhandler(404)
def not_found(error):
    resp = make_response(render_template('page_not_found.html'), 404)
    resp.headers['X-Something'] = 'A value'
    print(error)
    return resp


# ++++++++++++  search results and filtering page ++++++++++++
@app.route('/search-results', methods=['GET', 'POST'])
def search_results():
    return render_template('search-results.html')


# ++++++++++++  list of books page ++++++++++++
@app.route('/book-indices')
def book_indices():
    # results = Query(Title).all().options()

    # table = Title.query.all()
    # return render_template('book-indices.html', titles=table)
    # q = db.session.query().
    return render_template('book-indices.html', titles=["title", "title1", "title2", "title3", "title4"])


# ++++++++++++  list of "subjects" in tje db page ++++++++++++
@app.route('/subject-list')
def subject_list():
    return render_template('subject-list.html')
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
    db.session.add(bookref)
    db.session.commit()
    return redirect('/check')
