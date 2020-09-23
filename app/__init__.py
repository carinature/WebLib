from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    # """Construct the core app."""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.DevConfig') # Using a development configuration
    # app.config.from_object('config.ProdConfig') # Using a production configuration
    # app.config.from_object('config.Config')

    db.init_app(app)

    with app.app_context():
        from . import routes  # Import routes
        # db.create_all()  # Create sql tables for our data models
        # from utilities.db_migration import csv_to_mysql
        # csv_to_mysql()
        return app
