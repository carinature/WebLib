
from flask_app import db

# Get SQLAlchemy to create the database tables.
# This is a one-off operation - once we've created the database's structure, it's done.
db.create_all()
