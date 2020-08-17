# A very simple Flask Hello World app for you to get started with...

from flask import Flask
from flask import render_template, make_response, redirect, url_for, request

app = Flask(__name__)

# Also, just to help in case you’ve made a typo in the code somewhere, add this line just after the line that says
# app = Flask(__name__) todo fixme remove this in production!!!
app.config["DEBUG"] = True


@app.errorhandler(404)
def not_found(error):
    resp = make_response(render_template('page_not_found.html'), 404)
    resp.headers['X-Something'] = 'A value'
    return resp


# ++++++++++++  dbg page ++++++++++++
comments = ["sdlkfjsksldjfksldjflkdsjf"]


@app.route('/check', methods=['GET', 'POST'])
# @app.route('/check.html', methods=['GET', 'POST'])
def checkcheck():
    if request.method == 'GET':
        return render_template('check.html', comments=comments)
    comments.append(request.form["contents"])
    return redirect('/check')


@app.route('/search-results')
# @app.route('/search-results.html')
def search_results():
    return render_template('search-results.html')


@app.route('/book-indices')
# @app.route('/book-indices.html')
def book_indices():
    return render_template('book-indices.html')


@app.route('/subject-list')
# @app.route('/subject-list.html')
def subject_list():
    return render_template('subject-list.html')
    # return render_template(url_for(subject-list))


@app.route('/')
@app.route('/index')
@app.route('/index.html')
def index():
    # return '<h1>You did IT!</h1><h1>You did IT!</h1><h1>You did IT!</h1>'
    return render_template('index.html')

# @app.route('/index1.html')
# def redirect_index():
#     return redirect(url_for('subject_list'))
#     # return redirect('/index.html')
