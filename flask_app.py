# A very simple Flask Hello World app for you to get started with...

from flask import Flask
from flask import render_template, make_response, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy

import random   # todo remove


app = Flask(__name__)

# Also, just to help in case you’ve made a typo in the code somewhere, add this line just after the line that says
# app = Flask(__name__)
app.config["DEBUG"] = True  # todo fixme remove this in production!!!


# SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{db_name}".format(
#     username="karinature",
#     password="dsmiUw2sn",
#     hostname="karinature.mysql.pythonanywhere-services.com",
#     db_name="karinature$tryout",
# )
SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{db_name}".format(
    username="root",
    password="123",
    hostname="localhost",
    db_name="tryout",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# example table module todo move to a different file (aux/migration/once_off)
class ExampleEntry(db.Model):
    __tablename__ = "check"

    # id = db.Column(db.Integer, primary_key=True)
    # content = db.Column(db.String(4096))
    int_value_col = db.Column(db.Integer, primary_key=True)
    text_value_col = db.Column(db.String(4096))


# ++++++++++++  dbg page ++++++++++++
@app.route('/check', methods=['GET', 'POST'])
def check_check():
    if request.method == 'GET':
        return render_template('check.html', comments=ExampleEntry.query.all())
    comment = ExampleEntry(text_value_col=request.form["contents"], int_value_col=random.randint(3, 9))
    db.session.add(comment)
    db.session.commit()
    return redirect('/check')


@app.route('/search-results')
def search_results():
    return render_template('search-results.html')


@app.route('/book-indices')
def book_indices():
    return render_template('book-indices.html')


@app.route('/subject-list')
# @app.route('/subject-list.html')
def subject_list():
    return render_template('subject-list.html')
    # return render_template(url_for('subject_list')+'.html')


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.errorhandler(404)
def not_found(error):
    resp = make_response(render_template('page_not_found.html'), 404)
    resp.headers['X-Something'] = 'A value'
    print(error)
    return resp
