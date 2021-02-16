import collections
import os
from collections import defaultdict

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey, Table, MetaData, CheckConstraint
from sqlalchemy.ext.declarative import synonym_for
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import column_property, Query, validates, synonym
from sqlalchemy.types import Integer, String, Text, UnicodeText, DateTime, Float, Boolean, PickleType

from config import RAW_DATA_DIR

from . import db

Base: SQLAlchemy.__base__ = db.Model
# Base:SQLAlchemy.Query = db.Model
# Base:sqlalchemy.orm = db.Model
# Base:SQLAlchemy = db.Model

# Base = declarative_base()

# ---------- RelationShip Example ----------
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


SHORT_STRING_LEN = 20
LONG_STRING_LEN = 100

# the fields marked as 'nullable(=True)' are (mostly) those who don't have a value in the orig (moshes) csv

# corresponds to the book_references table
# holding information for the referencing books
# prime key 'bibinfo' is (will be) a foreign key in TextText
class BookRef(Base):
    __tablename__ = 'book_references'

    src_scv = [f'{RAW_DATA_DIR}/{textsfile}'
               for textsfile in os.listdir(RAW_DATA_DIR) if textsfile.startswith('bookreferences')]

    col_names = ['biblio', 'file', 'title', 'gcode']
    dtype_dic_py2sql = {int: Integer, str: Text}
    dtype_dic_csv2py = {'book bibliographic info': int,  # :int ???
                        'file': str,
                        'titleref': str,
                        'gcode': str}

    # prime key 'bibinfo' is (will be) a foreign key in TextText
    biblio = Column(Integer, primary_key=True, nullable=False)
    title = Column(String(LONG_STRING_LEN), nullable=False)
    file = Column(String(SHORT_STRING_LEN), nullable=False)
    gcode = Column(String(SHORT_STRING_LEN), nullable=True)

    # CheckConstraint("gcode in ('x','#VALUE!')"), #this only throws an exception and stops table build
    # ,unique=True)

    # def check_gcode(gcode: String):
    #     # return context.get_current_parameters()['gcode'] + 12
    #     if ('x' == gcode) or ('#VALUE!' == gcode):
    #         _gcode = None
    #     else:
    #         print(gcode)
    #         _gcode = gcode
    #     return _gcode

    # def mydefault(context):
    #     return context.get_current_parameters()['counter'] + 12

    # _gcode = Column(String(SHORT_STRING_LEN),
    #                 default=check_gcode,
    #                 nullable=True)

    # @synonym_for("gcode")
    # @property
    # # @hybrid_property
    # def _gcode(self):
    #     if 'x' == self.gcode:
    #         return None
    #     else:
    #         return self.gcode

    # ggcode = synonym("gcode", descriptor=_gcode)
    # @validates('gcode')
    # def bad_value_in_csv(self, key, value):
    #     if 'x' == value:
    #         return None
    #     else:
    #         return value

    # todo what does it mean to have a column that is both nullable and has a default value

    def __repr__(self):
        return \
            f'< (BookRef) - {self.title}, ' \
            f' file: {self.file}, ' \
            f' biblio: {self.biblio}>'


# corresponds to the titles table
# holding information for the referenced titles - the results of the search
# prime key 'number' is (will be) a foreign key in TextText
class Title(Base):  # todo handle cases of null in 'from/to century',
    __tablename__ = 'titles'  # fixme

    src_scv = [f'{RAW_DATA_DIR}/{textsfile}'
               for textsfile in os.listdir(RAW_DATA_DIR) if textsfile.startswith('title')]

    col_names = ['index_org', 'author', 'centend', 'centstart', 'joined', 'language', 'number', 'title']

    dtype_dic_csv2py = {'index1': str,
                        'author1': str,
                        'centend': str,  # fixme float,
                        'centstart': str,  # fixme float,
                        'joined': str,
                        'language': str,
                        'number': str,  # fixme int, #todo can you try a conversion function? kt_nan_to_int() ...?
                        'title1': str}
    dtype_dic_py2sql = {int: Integer, float: Float, str: Text}

    # dbg_index = Column(Integer, autoincrement=True, primary_key=True)
    index_org = Column(String(SHORT_STRING_LEN), primary_key=True, nullable=False)  # todo remove # , nullable=False)
    title = Column(String(500))  # fixme - shouldn't be that long - update in files
    author = Column(String(LONG_STRING_LEN))
    centend = Column(String(SHORT_STRING_LEN))  # Float, nullable=True, default=0)
    centstart = Column(String(SHORT_STRING_LEN))  # Float, nullable=True, default=0)
    joined = Column(String(250))  # fixme - shouldn't be that long - update in files
    language = Column(String(SHORT_STRING_LEN))
    number = Column(String(SHORT_STRING_LEN), primary_key=True)

    # fixme - number should be Integer - problem when file conains chars or empty field as number.
    #  also it should be the ONLY primary

    # CheckConstraint('centend <= centstart', name="ck_centend_before_centstart")

    # @staticmethod
    # def name():
    #     return 'Title bla bla'

    def __repr__(self):
        # todo rename column names
        return f'<Title model title: {self.title},  author: {self.author}, index: {self.index_org}>'


# corresponds to the text_subjects2.csv
class TextSubject(Base):
    # todo fixme
    #  file structure not fully understood
    #  plus what happens when there are miultiple commas
    #   or a subject that contains a comma within brackets(', ")
    __tablename__ = 'text_subjects'  # fixme

    col_names = ['subject', 'C']

    src_scv = [f'{RAW_DATA_DIR}/{textsfile}'
               for textsfile in os.listdir(RAW_DATA_DIR) if textsfile.startswith('texts_subjects')]

    dtype_dic_csv2py = {'subject': str,
                        'C': str}
    dtype_dic_py2sql = {int: Integer, str: Text}

    subject = Column(String(200), primary_key=True, nullable=False)
    dbg_index = Column(Integer, primary_key=True, autoincrement=True)  # todo remove
    C = Column(Text)  # longest C value is ~68,000 chars in line 24794/5 &~31268 ..
    Csum = Column(Integer)

    def __repr__(self):
        return f'<TextSubject subject: {self.subject}, #ref: {self.Csum} , C: {self.C}>'


# corresponds to the textsa1.csv textsa2.csv textsa19.csv textsa1.csv
class TextText(Base):
    __tablename__ = "texts"

    # src_scv = ['/home/fares/PycharmProjects/WebLib/raw_data/textsa1.csv']
    # src_scv = ['/home/fares/PycharmProjects/WebLib/raw_data/textsa2.csv']
    # src_scv = ['/home/fares/PycharmProjects/WebLib/raw_data/textsa19.csv']
    src_scv = [f'{RAW_DATA_DIR}/{textsfile}'  # fixme should work
               for textsfile in os.listdir(RAW_DATA_DIR) if textsfile.startswith('textsa')]

    col_names = ['subject', 'ref', 'page', 'biblio', 'number', 'C']

    dtype_dic_csv2py = {'subject': str,
                        'ref': str,
                        'page': str,
                        'book bibliographic info': str,  # :int ???
                        'number': str,
                        'C': str}  # {col:str for col in col_names}
    # dtype_dic_py2sql = {int: Integer, str: Text}
    index_dbg = Column(Integer, autoincrement=True, primary_key=True, nullable=False)

    subject = Column(String(120))
    ref = Column(String(100))
    page = Column(String(10))
    biblio = Column(String(10))
    number = Column(String(10))
    C = Column(String(10))

    def __repr__(self):
        return \
            f'<(TextText) ' \
            f'#{self.number}, ' \
            f'subject: {self.subject}, ' \
            f'ref: {self.ref}, ' \
            f'bib_info: {self.biblio} ' \
            f'pg.{self.page}, ' \
            f'C: {self.C}, ' \
            f'>'


from typing import List, Dict, Set


class Book:
    def __init__(self, bibinfo: int):
        self.bibinfo = int(float(bibinfo))  # todo bibinfo should be int in the DB, currentyly str
        self.pages: Set[int] = set()
        self.refs: List[int] = []
        q_book_ref: Query = BookRef.query
        q_book_ref_filter: Query = q_book_ref.filter(BookRef.biblio == self.bibinfo)
        self.title_full = q_book_ref_filter.value(BookRef.title)

    def __repr__(self):
        return \
            f'... The Referencing Book: ' \
            f'{self.title_full} ' \
            f'bib: {self.bibinfo} ' \
            f'pages: {self.pages}'


class ResultTitle:
    # print(' =============== ResultTitle ================')
    filtered_flag = False

    def __init__(self, num: str, filter_form: Dict):
        # def __init__(self, num: int, filter_form: f.FilterForm):
        # todo better to accept dict, instead of form?
        #  todo should accept num as int. change to DB
        from_century = filter_form['from_century']
        to_century = filter_form['to_century']
        language = filter_form['language']
        ancient_author = filter_form['ancient_author']
        ancient_title = filter_form['ancient_title']
        q_title_filter: Query = Title.query.filter(Title.number == num)
        # todo  if to_century < from_century:
        # todo remove the 'if' clause from the '*_century', when the html page would actually have a filter form
        if from_century:
            q_title_filter: Query = q_title_filter.filter(Title.centstart >= from_century)
        if to_century:
            q_title_filter: Query = q_title_filter.filter(Title.centend <= to_century)
        if language:
            q_title_filter: Query = q_title_filter.filter(Title.language == language)
        if ancient_author:
            q_title_filter: Query = q_title_filter.filter(Title.author == ancient_author)
        if ancient_title:
            q_title_filter: Query = q_title_filter.filter(Title.title == ancient_title)
        # if passed all filters
        if q_title_filter.first():
            self.filtered_flag = True
            self.num = num
            self.refs: Set = set()
            self.bibinfo: List[int] = []
            self.books: List[Book] = []
            self.books_dict: Dict[str, Book] = {}
            self.author = q_title_filter.value(Title.author)
            self.title = q_title_filter.value(Title.title)
            # print('.' * 50, self.title, 'by:', self.author)

    def add_bib(self, bibinfo: str):  # todo bibinfo: int
        # print(' ---------- add_bib --------- ')
        bibinfo = int(float(bibinfo))  # todo bibinfo should be int in the DB, currently str
        self.bibinfo.append(bibinfo)
        # self.books[bibinfo] = Book(bibinfo)
        self.books.append(Book(bibinfo))

    def add_page(self, page: str, bibinfo: str):  # todo bibinfo: int
        bibinfo = int(float(bibinfo))  # todo bibinfo should be int in the DB, currentyly str
        bibinfo = int(float(bibinfo))  # todo bibinfo should be int in the DB, currently str
        if not page.strip(' '):  # todo should be handled in DB
            page = ' Page-Unknown '
        else:
            page = int(float(page))  # todo page should be int in the DB, currentyly str
        # self.books[bibinfo].pages.add(page)

        # if page not in self.books[-1].pages:
        # print(' --------- add_page --------')
        self.books[-1].pages.add(page)

    def add_refs(self, ref: str, bibinfo: int):
        bibinfo = int(float(bibinfo))  # todo bibinfo should be int in the DB, currently str
        # self.books[bibinfo].refs.append(ref)
        # self.refs[bibinfo] = ref

        self.books[-1].refs.append(ref)
        if ref not in self.refs:
            print(' --- add_refs ---    ')
        self.refs.add(ref)

    def __repr__(self):
        s = '*' * 13
        # s += f' (The Result-Title): ' \
        s = f'' \
            f'#{self.num}, ' \
            f'{self.title} By: ' \
            f'{self.author}, ' \
            f'{self.bibinfo}, ' \
            f'{self.refs}\n'
        # for k, i in self.books.items():
        for i in self.books:
            s += f'\t\t{i}\n'
        return s

# from sqlalchemy_utils import create_view

# view: Table = create_view('my_view', TextText, Base.metadata)


# provides an ORM interface to the view
# class MyView(Base):
#     __table__ = 'my_view'
