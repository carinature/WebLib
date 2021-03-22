import os
import collections
from collections import defaultdict
from typing import List, Dict, Set

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey, Table, MetaData, CheckConstraint, SmallInteger, inspect
from sqlalchemy.orm import column_property, Query, validates, synonym, relationship
from sqlalchemy.types import Integer, String, Text, UnicodeText, DateTime, Float, Boolean, PickleType
from sqlalchemy.ext.declarative import synonym_for
from sqlalchemy.ext.hybrid import hybrid_property

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

    biblio = Column(Integer, primary_key=True, nullable=False)  # (will be) a foreign key in TextText
    title = Column(String(LONG_STRING_LEN), nullable=False)
    file = Column(String(SHORT_STRING_LEN), nullable=False)
    gcode = Column(String(SHORT_STRING_LEN), nullable=True)

    src_scv = [f'{RAW_DATA_DIR}/{textsfile}' for textsfile in os.listdir(RAW_DATA_DIR) if
               textsfile.startswith('bookreferences')]
    col_names = ['biblio', 'file', 'title', 'gcode']
    dtype_dic_py2sql = {int: Integer, str: Text}
    dtype_dic_csv2py = {
        'book bibliographic info': int,  # :int ???
        'file'                   : str, 'titleref': str, 'gcode': str
        }

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

    # todo what happens when a column is both nullable and has a default value

    def __repr__(self):
        return f'< (BookRef) - {self.title}, ' \
               f' file: {self.file}, ' \
               f' biblio: {self.biblio}>'


# corresponds to the titles table
# holding information for the referenced titles - the results of the search
# prime key 'number' is (will be) a foreign key in TextText
class Title(Base):
    __tablename__ = 'titles'

    number = Column(Integer, primary_key=True, unique=True)  # (will be) a foreign key in TextText
    title = Column(String(500), nullable=True)  # fixme - shouldn't be that long - update in files
    author = Column(String(LONG_STRING_LEN), nullable=True)
    centstart = Column(SmallInteger, nullable=True)  # , default=+21)# , server_default='+21')
    centend = Column(SmallInteger, nullable=True)  # , default=-21)# , server_default='+21')
    lang = Column(String(SHORT_STRING_LEN), nullable=True)
    # `index_org` & `joined` columns are omitted since they don't appear to be used

    src_scv = [f'{RAW_DATA_DIR}/{textsfile}' for textsfile in os.listdir(RAW_DATA_DIR) if textsfile.startswith('title')]
    col_names = ['index_org', 'author', 'centend', 'centstart', 'joined', 'lang', 'number', 'title']
    dtype_dic_csv2py = {
        'index1'   : str,
        'author1'  : str,
        # `int` is usable only for not-NaN cols: The lack of NaN rep in int cols is a pandas "gotcha".
        # 'centend': int,   todo
        # 'centstart': int, todo
        'centend'  : str,
        'centstart': str,
        'joined'   : str,
        'language' : str,
        'number'   : int,
        'title1'   : str
        }
    dtype_dic_py2sql = {int: Integer, float: Float, str: Text}

    # CheckConstraint('centend <= centstart', name="ck_centend_before_centstart")

    # @staticmethod
    # def name():
    #     return 'Title bla bla'

    def __repr__(self):
        # todo rename column names
        return f'<Title model title: {self.title},  author: {self.author}, index: {{self.index_org}}>'


# corresponds to the text_subjects2.csv
class TextSubject(Base):
    # todo fixme
    #  file structure not fully understood
    #  plus what happens when there are miultiple commas
    #   or a subject that contains a comma within brackets(', ")
    __tablename__ = 'text_subjects'

    # fixme should subject be that long?
    subject = Column(String(LONG_STRING_LEN * 2, collation='utf8_bin'), primary_key=True,
                     nullable=False)  # , whitespace=
    C = Column(Text, nullable=False)  # longest C value is ~68,000 chars in line 24794/5 &~31268 ..
    Csum = Column(Integer)  # used for ref counts (e.g. in listings of subjects)

    src_scv = [f'{RAW_DATA_DIR}/{textsfile}' for textsfile in os.listdir(RAW_DATA_DIR) if
               textsfile.startswith('texts_subjects')]
    col_names = ['subject', 'C']
    dtype_dic_csv2py = {
        'subject': str,
        'C'      : str
        }
    dtype_dic_py2sql = {
        int: Integer,
        str: Text
        }

    def __repr__(self):
        return f'<TextSubject subject: {self.subject}, #ref: {self.Csum} , C: {self.C}>'


# corresponds to the textsa1.csv textsa2.csv textsa19.csv textsa1.csv
class TextText(Base):
    __tablename__ = "texts"

    # index_dbg = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    C = Column(Integer, primary_key=True, nullable=False, autoincrement=False)
    subject = Column(String(LONG_STRING_LEN), nullable=False)  # ForeignKey('text_subjects.subject'),
    number = Column(Integer, ForeignKey(f'{Title.__tablename__}.{inspect(Title).primary_key[0].name}'), nullable=False)
    biblio = Column(Integer, ForeignKey(f'{BookRef.__tablename__}.{inspect(BookRef).primary_key[0].name}'),
                    nullable=False)
    page = Column(Integer, nullable=True)  # could be null(empty) - KT 20210221.
    # could be null(empty) - KT 20210221 - todo figure out what this means (for 'page' also)
    ref = Column(String(SHORT_STRING_LEN * 3), nullable=True)
    title = relationship('Title')
    book_ref = relationship('BookRef')

    # src_scv = ['/home/fares/PycharmProjects/WebLib/app/raw_data/textsa1.csv']
    src_scv = ['/home/fares/PycharmProjects/WebLib/app/raw_data/textsa2.csv']
    # src_scv = ['/home/fares/PycharmProjects/WebLib/app/raw_data/textsa19.csv']
    # src_scv = [f'{RAW_DATA_DIR}/{textsfile}'
    #            for textsfile in os.listdir(RAW_DATA_DIR) if textsfile.startswith('textsa')]
    col_names = ['subject', 'ref', 'page', 'biblio', 'number', 'C']
    dtype_dic_csv2py = {
        'subject'                : str,
        'ref'                    : str,
        'page'                   : float,
        'book bibliographic info': float,
        'number'                 : int,
        'C'                      : int
        }
    dtype_dic_py2sql = {
        int: Integer,
        str: String
        }

    # example = relationship("Chinese", backref="eng")

    def __repr__(self):
        return f'<(TextText) ' \
               f'C: {self.C}, ' \
               f'subject: {self.subject}, ' \
               f'#{self.number}, ' \
               f'bib_info: {self.biblio} ' \
               f'ref: {self.ref}, ' \
               f'pg.{self.page}, ' \
               f'>'


class Book:
    def __init__(self, bibinfo: BookRef):
        self.biblio: int = bibinfo.biblio
        self.refs: List[str] = []  # list of all refs todo maybe not nedded - depends on the data shown in the site
        self.pages: Set[int] = set()  # list of all refs todo maybe not nedded - depends on the data shown in the site
        self.refs_per_page: Dict[int, List[str]] = {}  # refs_per_page={pages: List[refs]}
        self.title_full: BookRef = bibinfo

    def add_page(self, page: int = -1):  # todo add ref?
        self.pages.add(page)
        return self

    def __repr__(self):
        # f'\n\t The Referencing Book: ' \
        return f'' \
               f'{self.title_full} ' \
               f'bib: {self.biblio} ' \
               f'refs per page: {self.refs_per_page}'

    def __len__(self):
        counter = 0
        # for pg, ref_list in self.refs_per_page.items():
        for ref_list in self.refs_per_page.values():
            counter += ref_list.__len__()
        return counter
        # return self.refs.__len__()

    def __lt__(self, other) -> bool:
        return self.__len__() < other.__len__()

    def __eq__(self, other) -> bool:
        return self.__len__() == other.__len__()


class ResultTitle:
    # print(' =============== ResultTitle ================')
    filtered_flag = False

    def __init__(self, num: int, title: str, author: str):  # fixme you don't really need the num
        self.num = num
        self.refs: Set = set()
        self.books_dict: Dict[int, Book] = {}
        self.author = author
        self.title = title

    def add_bib(self, bibinfo: BookRef) -> Book:
        self.books_dict[bibinfo.biblio] = self.books_dict.setdefault(bibinfo.biblio, Book(bibinfo))
        return self.books_dict[bibinfo.biblio]

    def add_refs(self, ref: str):
        self.refs.add(ref)

    def num_ref_books(self):
        return self.books_dict.__len__()

    def num_refs_total(self):
        return self.books_dict.__len__()

    def __repr__(self):
        s = '*' * 13
        # s += f' (The Result-Title): ' \
        s = f'' \
            f'#{self.num}, ' \
            f'{self.title} By: ' \
            f'{self.author}, ' \
            f'{self.books_dict}, ' \
            f'{self.refs}\n' \
            f'\nThe  ( ---{self.books_dict.__len__()}--- )  ref books: \n'
        # for k, i in self.books.items():
        for i in self.books_dict.items():
            s += f'\t\t{i}\n'
        return s

    def __len__(self) -> int:
        return self.books_dict.__len__()

    def __lt__(self, other) -> bool:
        return self.__len__() < other.__len__()

    def __eq__(self, other) -> bool:
        return self.__len__() == other.__len__()

