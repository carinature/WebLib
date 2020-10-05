from flask import Flask
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def create_app():
    # print(' --- App Init --- ')
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.DevConfig')  # development configuration
    # app.config.from_object('config.ProdConfig')  # production configuration

    db.init_app(app)

    with app.app_context():
        # print(' - App CTX - ')
        from . import routes  # Import routes
        # db.create_all()  # Create sql tables for our data models
        from utilities.db_migration import csv_to_mysql
        # csv_to_mysql()
        return app
