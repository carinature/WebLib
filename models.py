from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, Text, String
from sqlalchemy.types import Integer, String, Text, DateTime, Float, Boolean, PickleType

from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{db_name}".format(
    username="root",
    password="123",
    hostname="localhost",
    db_name="tryout",
)

Base = declarative_base()


# class TeamModel(Base):
#     """Data model for teams."""
#     __tablename__ = "sqlalchemy_tutorial_teams"
#     # __table_args__ = {"schema": "example"} #for postgress
#
#     id = Column(Integer, primary_key=True, nullable=False)
#     name = Column(String(100), nullable=False)
#     city = Column(String(100), nullable=False)
#
#     def __repr__(self):
#         return '<Team model {}>'.format(self.id)
#
#
# class PlayerModel(Base):
#     """Data model for players."""
#     __tablename__ = "sqlalchemy_tutorial_players"
#     # __table_args__ = {"schema": "example"} #for postgress
#
#     id = Column(Integer, primary_key=True, nullable=False)
#
#     team_id = Column(Integer, ForeignKey('sqlalchemy_tutorial_teams.id'), nullable=False)  # todo bookmark
#     name = Column(String(100), nullable=False)
#     position = Column(String(100), nullable=False)
#
#     # Relationships #todo bookmark
#     team = relationship("TeamModel", backref="player")
#
#     def __repr__(self):
#         return '<Person model {}>'.format(self.id)

# corresponds to the titilesa.csv


# corresponds to the bookreferences2.csv
# class BookRef(Base):
#     __tablename__ = 'book_references'
#     src_scv = ['raw_data/bookreferences2.csv']
#     dtype_dic_csv2py = {'book_bibliographic_info': int, 'file': str, 'titleref': str, 'gcode': str}
#
#     # todo see if possible to name the fields differently from  their csv name
#     #   answer: names of columns here in the model class dont have to be the same as in the original file
#     # the fields marked as 'nullable(=True)' are those who doesn't necessarily have a value in the orig (moshes) csv
#     book_bibliographic_info = Column(Integer, primary_key=True, nullable=False)
#     file = Column(String(100), default='non',
#                   nullable=True)  # fixme find a better default val or handle empty field. try the option below
#     # besides what does it mean to have a column that both nullable and has a default value
#     # file = Column(String(100), default=None, nullable=True) todo try this one
#     titleref = Column(String(100), nullable=True)
#     gcode = Column(Text, nullable=True)
#
#     # gcode = Column(Text, nullable=True ,unique=True)
#
#     def __repr__(self):
#         return f'<BookRef model file: {self.file},  title ref: {self.titleref}, index: {self.book_bibliographic_info}>'
#
#     # def __init__(self, bib_info, file, titleref, gcode):
#     #     super().__init__(self)
#     #     self.book_bibliographic_info = bib_info
#     #     self.file = file
#     #     self.titleref = titleref
#     #     self.gcode = gcode


# corresponds to the bookreferences2.csv

# corresponds to the titlesa.csv
class Title(Base):  # todo make sure what each fields
    __tablename__ = 'titles_new'  # fixme
    src_scv = ['raw_data/titlesa.csv']

    dbg_index = Column(Integer, autoincrement=True,primary_key=True, )
    # the fields marked as 'nullable(=True)' are those who doesn't necessarily have a value in the orig (moshes) csv
    index1 = Column(Integer,primary_key=True,default='non')  # , nullable=False)
    author = Column(String(100))  # , nullable=False)
    centend = Column(Integer, default='non')  # , nullable=True)
    centstart = Column(Integer, default='non')  # , nullable=True)
    joined = Column(String(10), default='non')  # fixme this ) #seems to be alwayws null
    language = Column(String(100), default='non')  # , nullable=True)
    number = Column(Integer)  # , nullable=False)
    title = Column(String(100))  # , nullable=False)

    def __repr__(self):
        # return '<Person model {}>'.format(self.id)
        return f'<Title model title: {self.title},  author: {self.author}, index: {self.index}>'

# corresponds to the text_subjects2.csv
# class TextSubject(Base):
#     # todo fixme
#     #  file structure not fully understood
#     #  plus what happens when there are miultiple commas
#     #   or a subject that contains a comma within brackets(', ")
#     __tablename__ = "text_subjects_new"  # fixme
#     src_scv = ['raw_data/texts_subjects2.csv']
#
#     # next fields have to have the same names as the fields in the original table
#     dbg_index = Column(Integer, primary_key=True, autoincrement=True)
#     C = Column(Text)
#     subject = Column(String(120), nullable=False)
#     # subject = Column(Text, nullable=False, primary_key=True)
#
#     def __repr__(self):
#         return f'<TextSubject subject: {self.subject}, C: {self.C} >'


# # corresponds to the textsa1.csv textsa2.csv textsa19.csv textsa1.csv
# class TextText(Base):
#     __tablename__ = "text_texts"  # fixme
#     src_scv = ['raw_data/textsa1.csv', 'raw_data/textsa2.csv', 'raw_data/textsa19.csv']
#
#     subject = Column(String(100), nullable=False)
#     ref = Column(Float, primary_key=True, nullable=False)
#     page = Column(Integer, primary_key=True, nullable=False)
#     book_bibliographic_info = Column(Integer, primary_key=True, nullable=False)
#     number = Column(Integer, primary_key=True, nullable=False)
#     C = Column(Integer, primary_key=True, nullable=False)
#
#     def __repr__(self):
#         return f'<TextText model subject: {self.subject},  C: {self.C}, >'
