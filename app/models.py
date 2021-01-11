import collections
import os
from collections import defaultdict

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey, Table, MetaData
from sqlalchemy.orm import column_property, Query
from sqlalchemy.types import Integer, String, Text, UnicodeText, DateTime, Float, Boolean, PickleType

from config import RAW_DATA_DIR

from . import db
from . import forms as f

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


# corresponds to the bookrefernces.csv
class BookRef(Base):
    __tablename__ = 'book_references'

    src_scv = [f'{RAW_DATA_DIR}/{textsfile}'
               for textsfile in os.listdir(RAW_DATA_DIR) if textsfile.startswith('bookreferences')]

    col_names = ['book_biblio_info', 'file', 'titleref', 'gcode']
    dtype_dic_py2sql = {int: Integer, str: Text}
    dtype_dic_csv2py = {'book bibliographic info': str,  # :int ???
                        'file': str,
                        'titleref': str,
                        'gcode': str}

    # the fields marked as 'nullable(=True)' are those who doesn't necessarily have a value in the orig (moshes) csv
    dbg_index = Column(Integer, autoincrement=True, primary_key=True, )
    book_biblio_info = Column(String(10), primary_key=True, nullable=False, default='non')
    file = Column(String(100), default='non', nullable=True)
    titleref = Column(String(100), nullable=True)
    gcode = Column(Text, nullable=True)  # ,unique=True)

    # fixme find a better default val or handle empty field. try the option below
    # file = Column(String(100), default=None, nullable=True) todo try this one
    # todo what does it mean to have a column that is both nullable and has a default value

    def __repr__(self):
        return \
            f'< (BookRef) - file: {self.file}, ' \
            f' title ref: {self.titleref}, ' \
            f' book_biblio_info: {self.book_biblio_info}>'


# corresponds to the titlesa.csv
class Title(Base):  # todo handle cases of null in 'from/to century',
    __tablename__ = 'titles'  # fixme

    src_scv = [f'{RAW_DATA_DIR}/{textsfile}'
               for textsfile in os.listdir(RAW_DATA_DIR) if textsfile.startswith('title')]

    col_names = ['index_org', 'author', 'centend', 'centstart', 'joined', 'language', 'number', 'title']

    dtype_dic_csv2py = {'index1': str,
                        'author1': str,
                        'centend': str,
                        'centstart': str,
                        'joined': str,
                        'language': str,
                        'number': str,
                        'title1': str}
    # dtype_dic_py2sql = {int: Integer, str: Text}

    dbg_index = Column(Integer, autoincrement=True, primary_key=True)
    # the fields marked as 'nullable(=True)' are those who doesn't necessarily have a value in the orig (moshes) csv
    index_org = Column(String(10), primary_key=True, nullable=False, default='non')  # , nullable=False)
    title = Column(String(500))
    author = Column(String(100))
    centend = Column(String(100))
    centstart = Column(String(100))
    joined = Column(String(200))  # fixme this seems to be always null
    language = Column(String(100))
    number = Column(String(100))

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

    dbg_index = Column(Integer, primary_key=True, autoincrement=True)
    subject = Column(String(200), nullable=False)
    C = Column(Text)  # longest C value is ~68,000 chars in line 24794/5 &~31268 .. fixme consider creating sub tables
    Csum = Column(
        Integer)  # longest C value is ~68,000 chars in line 24794/5 &~31268 .. fixme consider creating sub tables

    def __repr__(self):
        return f'<TextSubject subject: {self.subject}, C: {self.C} >'


# corresponds to the textsa1.csv textsa2.csv textsa19.csv textsa1.csv
class TextText(Base):
    __tablename__ = "texts"

    # src_scv = ['/home/fares/PycharmProjects/WebLib/raw_data/textsa1.csv']
    # src_scv = ['/home/fares/PycharmProjects/WebLib/raw_data/textsa2.csv']
    # src_scv = ['/home/fares/PycharmProjects/WebLib/raw_data/textsa19.csv']
    src_scv = [f'{RAW_DATA_DIR}/{textsfile}'  # fixme should work
               for textsfile in os.listdir(RAW_DATA_DIR) if textsfile.startswith('textsa')]

    col_names = ['subject', 'ref', 'page', 'book_biblio_info', 'number', 'C']

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
    book_biblio_info = Column(String(10))
    number = Column(String(10))
    C = Column(String(10))

    def __repr__(self):
        return \
            f'<(TextText) ' \
            f'#{self.number}, ' \
            f'subject: {self.subject}, ' \
            f'ref: {self.ref}, ' \
            f'bib_info: {self.book_biblio_info} ' \
            f'pg.{self.page}, ' \
            f'C: {self.C}, ' \
            f'>'


from typing import List, Dict, Set


class Book:
    def __init__(self, bibinfo: int):
        self.pages: Set[int] = set()
        self.refs: List[int] = []
        q_book_ref: Query = BookRef.query
        q_book_ref_filter: Query = q_book_ref.filter(BookRef.book_biblio_info == bibinfo)
        self.title_full = q_book_ref_filter.value(BookRef.titleref)
        self.bibinfo = int(float(bibinfo))  # todo bibinfo should be int in the DB, currentyly str

    def __repr__(self):
        return \
            f'... The Referencing Book: ' \
            f'{self.bibinfo} ' \
            f'{self.title_full} ' \
            f'pages: {self.pages}'


class ResultTitle:
    def __init__(self, num: int, filter_form: f.FilterForm):
        # def __init__(self, num: int, filter_form: f.FilterForm):
        self.num = num
        # self.refs: Dict = {}
        self.refs: Set = set()
        self.bibinfo: List[int] = []
        self.books: List[Book] = []
        # self.books: Dict[int, Book] = collections.defaultdict(Book)
        q_title: Query = Title.query
        q_title_filter: Query = q_title.filter(Title.number == num)
        self.author = q_title_filter.value(Title.author)
        self.title = q_title_filter.value(Title.title)
        print('.' * 13, self.title, 'by:', self.author)
        self.filtered_flag = False
        from_century = int(filter_form.from_century.data) if filter_form.from_century.data else -21
        to_century = int(filter_form.to_century.data) if filter_form.to_century.data else 21
        language = filter_form.language.data
        ancient_author = filter_form.ancient_author.data
        ref = filter_form.ancient_author.data
        if to_century > from_century:
            if from_century:
                q_title_filter: Query = q_title_filter.filter(Title.centstart >= from_century)
            if to_century:
                q_title_filter: Query = q_title_filter.filter(Title.centend <= to_century)
        if language:
            q_title_filter: Query = q_title_filter.filter(Title.language == language)
        if ancient_author:
            q_title_filter: Query = q_title_filter.filter(Title.author == ancient_author)
        # if ref: fixme
        #     q_title_filter: Query = q_title_filter.filter(Title. == filter_form.from_century.data)  # fixme check this in routes!

        # # fixme check this in routes or sooner in the code - at the top of this function!
        # q_title_filter_title: Query = q_title_filter_author.filter(
        #     Title.title == filter_form.ancient_title.data) if filter_form.ancient_author.data \
        #         else q_title_filter_author

        if q_title_filter.first():
            self.filtered_flag = True
        # self.filtered_flag = True
        # fixme - the above yields 87 results and only 15 results without the 2nd 'flag=true' line
        #   even though in both cases the filters are empty in the form.
        #   this is probably the result of mishandling null in the 'to_century" field
        #   (currently 'Any' value is -100, so if NULL in the field the query to_century<-100 is always FALSE)

    def add_bib(self, bibinfo: int):
        bibinfo = int(float(bibinfo))  # todo bibinfo should be int in the DB, currently str
        self.bibinfo.append(bibinfo)
        # self.books[bibinfo] = Book(bibinfo)
        self.books.append(Book(bibinfo))

    def add_refs(self, ref: str, bibinfo: int):
        bibinfo = int(float(bibinfo))  # todo bibinfo should be int in the DB, currently str
        # self.books[bibinfo].refs.append(ref)
        self.books[-1].refs.append(ref)
        # self.refs[bibinfo] = ref
        self.refs.add(ref)

    def add_page(self, page: str, bibinfo: int):
        bibinfo = int(float(bibinfo))  # todo bibinfo should be int in the DB, currentyly str
        if not page.strip(' '):  # todo should be handled in DB
            page = ' Page-Unknown '
        else:
            page = int(float(page))  # todo page should be int in the DB, currentyly str
        # self.books[bibinfo].pages.add(page)
        self.books[-1].pages.add(page)

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
