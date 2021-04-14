from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

import logging.config

# from flask_wtf import CSRFProtect

db = SQLAlchemy()
bootstrap = Bootstrap()


def create_app():
    app = Flask(__name__, instance_relative_config=False)
    # instance_relative_config=True tells the app that configuration files are relative to the instance folder.
    # The instance folder is located outside the flaskr package and can hold local data that shouldn’t be committed
    # to version control, such as configuration secrets and the database file.

    # app.config.from_object('config.DevConfig')  # development configuration, configured for local sql docker
    app.config.from_object('config.ProdConfig')  # production configuration, configured for pythonanywhere

    db.init_app(app)
    bootstrap.init_app(app)

    # csrf = CSRFProtect(app)
    # csrf.init_app(app)

    # # logging #todo put in `with app.app_context()`  ?
    # logging.config.fileConfig('logging.conf', defaults={'logfilename': 'db_migration.log'})

    with app.app_context():
        from . import routes  # Import routes  # todo - make sure this line wasn't deleted:
        from . import test_routes  # fixme remove in production
        # db.create_all()  # Create sql tables for our data models
        # from db_migration import DBMigration
        # DBMigration().load_full_db()
        return app
