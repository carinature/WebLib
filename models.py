from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, Text, String
from sqlalchemy.types import Integer, String, Text, DateTime, Float, Boolean, PickleType

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class UserModel(Base):
    """Data model example."""
    __tablename__ = "example_table"
    # __table_args__ = {"schema": "example"} # for postrgres

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    join_date = Column(DateTime, nullable=True)
    vip = Column(Boolean, nullable=True)
    number = Column(Float, nullable=True)
    data = Column(PickleType, nullable=True)

    def __repr__(self):
        return f'<UserModel model id: {self.id},  name: {self.name}, >'


class Entry(Base):
    __tablename__ = 'check'

    # next fields have to have the same names as the fields in the original table
    int_value_col = Column(Integer, primary_key=True, unique=True, AUTO_INCREMENT=True)
    # fixme line above gives the following: "SAWarning: Can't validate argument 'AUTO_INCREMENT'; can't locate any
    #  SQLAlchemy dialect named 'AUTO' % (k, dialect_name)"
    text_value_col = Column(String(80), nullable=False)

    # email = Column(String(120), unique=True, nullable=False)
    # joined = Column(Datetime, unique=False, nullable=False)

    def __repr__(self):
        return f'<Entry {self.text_value_col}>'


SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{db_name}".format(
    username="root",
    password="123",
    hostname="localhost",
    db_name="tryout",
)


class TeamModel(Base):
    """Data model for teams."""
    __tablename__ = "sqlalchemy_tutorial_teams"
    # __table_args__ = {"schema": "example"} #for postgress

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)

    def __repr__(self):
        return '<Team model {}>'.format(self.id)


class PlayerModel(Base):
    """Data model for players."""
    __tablename__ = "sqlalchemy_tutorial_players"
    # __table_args__ = {"schema": "example"} #for postgress

    id = Column(Integer, primary_key=True, nullable=False)

    team_id = Column(Integer, ForeignKey('sqlalchemy_tutorial_teams.id'), nullable=False)  # todo bookmark
    name = Column(String(100), nullable=False)
    position = Column(String(100), nullable=False)

    # Relationships #todo bookmark
    team = relationship("TeamModel", backref="player")

    def __repr__(self):
        return '<Person model {}>'.format(self.id)


class Title(Base):  # todo see if possible to name the fields differently from  their csv name
    __tablename__ = 'titles_new'

    # indexa    bigint null,
    # the fields marked as 'nullable(=True)' are those who doesn't necessarily have a value in the orig (moshes) csv
    index = Column(Float, primary_key=True, nullable=False)  # value of the 'index' column in the original source csv
    author1 = Column(Text, nullable=False)
    centend = Column(Text, nullable=True)
    centstart = Column(Text, nullable=True)
    joined = Column(Text, nullable=True)
    language = Column(Text, nullable=True)
    number = Column(Text, nullable=False)
    title1 = Column(Text, nullable=False)

    def __repr__(self):
        # return '<Person model {}>'.format(self.id)
        return f'<Title model title: {self.title1},  author: {self.author1}, index: {self.index}>'
