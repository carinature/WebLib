# A very simple Flask Hello World app for you to get started with...

from flask import Flask
from flask import render_template, make_response

app = Flask(__name__)


@app.route('/')
@app.route('/index.html')
def index():
    # return '<h1>You did IT!</h1><h1>You did IT!</h1><h1>You did IT!</h1>'
    return render_template('index.html')


@app.route('/book-indices.html')
def book_indices():
    return render_template('book-indices.html')


@app.route('/subject-list.html')
def subject_lis():
    return render_template('subject-list.html')


@app.route('/check.html')
def checkcheck():
    return render_template('check.html')


@app.errorhandler(404)
def not_found(error):
    resp = make_response(render_template('page_not_found.html'), 404)
    resp.headers['X-Something'] = 'A value'
    return resp


@app.route('/search-results.html')
def search_results():
    return render_template('search-results.html')

