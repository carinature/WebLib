
from flask_app import db

# Get SQLAlchemy to create the database tables.
# This is a one-off operation – once weve created the databases structure, its done.
db.create_all()
