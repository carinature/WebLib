from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    # print(' --- App Init --- ')
    app = Flask(__name__, instance_relative_config=False)
    # instance_relative_config=True tells the app that configuration files are relative to the instance folder.
    # The instance folder is located outside the flaskr package and can hold local data that shouldn’t be committed
    # to version control, such as configuration secrets and the database file.
    app.config.from_object('config.DevConfig')  # development configuration
    # app.config.from_object('config.ProdConfig')  # production configuration

    db.init_app(app)

    with app.app_context():
        # print(' - App CTX - ')
        # db.create_all()  # Create sql tables for our data models
        # csv_to_mysql()
        return app
