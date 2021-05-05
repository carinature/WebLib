import os
import collections
from collections import defaultdict
from typing import List, Dict, Set, Tuple

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey, Table, MetaData, CheckConstraint, SmallInteger, inspect
from sqlalchemy.dialects.mysql import LONGTEXT
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


def get_prime_key(model: Base, model_row: Base = None) -> Tuple[List[str], str]:
    # prime_key_name = inspect(model).primary_key[0].name
    # prime_key_val = model_row.__dict__[prime_key_name] if model_row else None
    prime_key_name = [pk.name for pk in inspect(model).primary_key]
    prime_key_val = [model_row.__dict__[pk] if model_row else None for pk in prime_key_name]
    return prime_key_name, str(prime_key_val)


# the fields marked as 'nullable(=True)' are (mostly) those who don't have a value in the orig (moshes) csv

# corresponds to the book_references table
# holding information for the referencing books
# prime key 'bibinfo' is (will be) a foreign key in TextText
class BookRef(Base):
    __tablename__ = 'book_references'

    biblio = Column(Integer, primary_key=True, nullable=False)  # a foreign key in TextText
    title = Column(String(LONG_STRING_LEN), nullable=False)
    file = Column(String(SHORT_STRING_LEN), nullable=False)
    gcode = Column(String(SHORT_STRING_LEN), nullable=True)

    src_scv = [f'{RAW_DATA_DIR}/{textsfile}' for textsfile in os.listdir(RAW_DATA_DIR)
               if textsfile.startswith('bookreferences')]
    col_names = ['biblio', 'file', 'title', 'gcode']
    dtype_dic_py2sql = {int: Integer, str: Text}
    dtype_dic_csv2py = {
        'book bibliographic info': int,  # :int ???
        'file'                   : str,
        'titleref'               : str,
        'gcode'                  : str
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

    number = Column(Integer, primary_key=True, unique=True)  # a foreign key in TextText & RefQuote
    title = Column(String(5 * LONG_STRING_LEN), nullable=True)  # fixme - shouldn't be that long - update in files
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
        return f'< (Title) - {self.title},  ' \
               f'author: {self.author}, ' \
               f'number: {self.number}>'


# the fields marked as 'nullable(=True)' are (mostly) those who don't have a value in the orig (moshes) csv

# corresponds to the ref_quotes table and tlgs_with_text2.csv
# holding information for the referencing books
# prime key 'bibinfo' is (will be) a foreign key in TextText
class RefQuote(Base):
    __tablename__ = 'ref_quotes'

    number = Column(Integer,
                    ForeignKey(f'{Title.__tablename__}.{inspect(Title).primary_key[0].name}'),
                    primary_key=True,
                    nullable=False)
    ref = Column(String(SHORT_STRING_LEN),
                 # ForeignKey(f'{Title.__tablename__}.{inspect(Title).primary_key[0].name}'),
                 primary_key=True,
                 nullable=False)  # would be a foreign key in TextText?
    text = Column(Text, nullable=True)  # fixme change to Column(LONGTEXT, nullable=True) #
    texteng = Column(Text, nullable=True)
    # todo - the next two fields seem redundent (if there's a title's number anyway
    author = Column(String(2 * SHORT_STRING_LEN),
                    # ForeignKey(f'{Title.__tablename__}.{inspect(Title).c.author.name}'),
                    nullable=True)
    title = Column(String(4 * SHORT_STRING_LEN),
                   # ForeignKey(f'{Title.__tablename__}.{inspect(Title).c.title.name}'),
                   nullable=True)

    title_r = relationship('Title')

    src_scv = [f'{RAW_DATA_DIR}/{textsfile}' for textsfile in os.listdir(RAW_DATA_DIR)
               if textsfile.startswith('tlgs_with_text')]
    col_names = ['number', 'ref', 'text', 'texteng', 'author', 'title']
    dtype_dic_csv2py = {
        'number' : int,
        'ref'    : str,
        'text'   : str,
        'texteng': str,
        'author1': str,
        'title1' : str,
        }
    dtype_dic_py2sql = {int: Integer, str: Text}

    def __repr__(self):
        return f'< (RefQuote) - number: {self.number},  ref: {self.ref}>'


# corresponds to the text_subjects2.csv
class TextSubject(Base):
    # todo fixme
    #  file structure not fully understood
    #  plus what happens when there are miultiple commas
    #   or a subject that contains a comma within brackets(', ")
    __tablename__ = 'text_subjects'

    # fixme should subject be that long?
    subject = Column(String(2 * LONG_STRING_LEN, collation='utf8_bin'), primary_key=True,
                     nullable=False)  # , whitespace=
    C = Column(Text, nullable=False)  # longest C value is ~68,000 chars in line 24794/5 &~31268 ..
    Csum = Column(Integer)  # used for ref counts (e.g. in listings of subjects)

    src_scv = [f'{RAW_DATA_DIR}/{textsfile}' for textsfile in os.listdir(RAW_DATA_DIR) if
               textsfile.startswith('texts_subjects')]
    col_names = ['subject', 'C']
    dtype_dic_csv2py = {
        'subject': str,
        'C'      : str,
        }
    dtype_dic_py2sql = {
        int: Integer,
        str: Text
        }

    def __repr__(self):
        return f'< (TextSubject) - {self.subject}, ' \
               f'#ref: {self.Csum}, ' \
               f'C\'s List: {self.C}>'


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
    # ref_quote_tbl = relationship('RefQuote')

    # ref = Column(String(SHORT_STRING_LEN * 3),
    #              ForeignKey(f'{Title.__tablename__}.{inspect(Title).primary_key[0].name}'),
    #              nullable=True)
    # title_tbl = relationship('Title')
    # book_ref_tbl = relationship('BookRef')

    # todo
    # src_scv = ['/home/fares/PycharmProjects/WebLib/app/raw_data/textsa1.csv']
    # src_scv = ['app/raw_data/textsa1.csv', 'app/raw_data/textsa2.csv']# src_scv = ['/home/fares/PycharmProjects/WebLib/app/raw_data/textsa2.csv']
    # src_scv = ['/home/fares/PycharmProjects/WebLib/app/raw_data/textsa19.csv']
    src_scv = [f'{RAW_DATA_DIR}/{textsfile}'
               for textsfile in os.listdir(RAW_DATA_DIR) if textsfile.startswith('textsa')]
    col_names = ['subject', 'ref', 'page', 'biblio', 'number', 'C']
    dtype_dic_csv2py = {
        'subject'                : str,
        'ref'                    : str,
        'page'                   : float,
        'book bibliographic info': float,
        'number'                 : int,
        'C'                      : int
        }
    dtype_dic_py2sql = {int: Integer, str: String}

    # example = relationship("Chinese", backref="eng")

    def __repr__(self):
        return f'<(TextText) - ' \
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
        self.refs: Set[str] = set()  # todo maybe not needed - depends on the data shown in the site
        self.pages: Set[int] = set()  # todo maybe not needed - depends on the data shown in the site
        self.refs_per_page: Dict[int, List[str]] = {}  # refs_per_page={pages: List[refs]}
        self.title_full: BookRef = bibinfo

    def add_page(self, page: int = -1):
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

    def __init__(self, title: Title):
        self.author: str = title.author
        self.title: str = title.title
        self.num: int = title.number
        self.subjects: Set = set()
        self.refs: Set = set()
        self.books_dict: Dict[int, Book] = {}

    def add_bib(self, bibinfo: BookRef) -> Book:
        return self.books_dict.setdefault(bibinfo.biblio, Book(bibinfo))

    def add_ref(self, ref: str):
        self.refs.add(ref)
        return self

    def add_subject(self, subject: str):
        self.subjects.add(subject)
        return self

    def num_ref_books(self) -> int:
        return self.books_dict.__len__()

    def num_refs_total(self) -> int:
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
