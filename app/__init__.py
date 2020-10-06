from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# from flask_wtf import CSRFProtect

db = SQLAlchemy()


def create_app():
    app = Flask(__name__, instance_relative_config=False)
    # instance_relative_config=True tells the app that configuration files are relative to the instance folder.
    # The instance folder is located outside the flaskr package and can hold local data that shouldn’t be committed
    # to version control, such as configuration secrets and the database file.
    # app.config.from_object('config.DevConfig')  # development configuration
    app.config.from_object('config.ProdConfig')  # production configuration

    db.init_app(app)

    # csrf = CSRFProtect(app)
    # csrf.init_app(app)

    with app.app_context():
        # todo - make sure this line wasn't deleted:
        #  from . import routes  # Import routes
        from . import routes  # Import routes
        # db.create_all()  # Create sql tables for our data models
        # from db_migration import csv_to_mysql
        # csv_to_mysql()
        return app
