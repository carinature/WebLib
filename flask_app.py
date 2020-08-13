# A very simple Flask Hello World app for you to get started with...

from flask import Flask
from flask import render_template

app = Flask(__name__)


@app.route('/')
@app.route('/index.html')
def hello_world():
    # return '<h1>You did IT!</h1><h1>You did IT!</h1><h1>You did IT!</h1>'
    return render_template('index.html')
