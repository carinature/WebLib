from flask import request, render_template

# from utilities.models import *
from config import SQLALCHEMY_DATABASE_URI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Create engine
engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=False)

# Create the session
Session = sessionmaker(bind=engine)
session = Session()
# session = scoped_session(Session())

print('--------------------')
# for i in range(13):
#     entry = BookRef(text_value_col=f'{i}'+f'{i}'+f'{i}'+f'{i}')
#     session.add(entry)
#     print("entry")
#     print(entry)
#     session.commit()


# records = session.query(BookRef).all()
# create your own object instead to receive only the columns you want/need:
# for record in records:
#     print(record)

# records = session.query(BookRef).filter(BookRef.book_biblio_info > 140).all()
# print("bigger than ")
# for record in records:
#     print(record)

# records = session.query(BookRef).filter_by(book_biblio_info=3).all()
# print("equals =")
# for record in records:
#     print(record)
#
# records = session.query(BookRef).filter(BookRef.book_biblio_info == 3).all()
# print("equals ==")
# for record in records:
#     print(record)
#
# records = session.query(BookRef).filter(BookRef.book_biblio_info.like('1%')).all()
# print("like")
# for record in records:
#     print(record)

# todo
#   In addition to filter(), there are a few basic methods we should absolutely be familiar with.
#   Each of these corresponds to SQL keywords you're probably familiar with:
#   limit([INTEGER]): Limits the number of rows to a maximum of the number provided.
#   order_by([COLUMN]): Sorts results by the provided column.
#   offset([INTEGER]): Begins the query at row n.
#   "Group by" aggregation
#   records = session.query(func.count(Customer.first_name)).group_by(Customer.first_name).all()

# print('--------------------')
# records = session.query(BookRef).filter(BookRef.book_biblio_info.like('3%')).all()
# print("like")
# for record in records:
#     print(record)
#
# print('--------------------')
# records = session.query(BookRef).paginate.filter(BookRef.book_biblio_info.like('3%')).with_entities(BookRef.titleref).all()
# print("like")
# for record in records:
#     print(record)
# print(records)

from app.models import BookRef

print('--------------------')
records = BookRef.query.paginate(1, 3, False).items
print("like")
for record in records:
    print(record)
print(records)

from app.routes import app


# # @app.route('/', methods=['GET', 'POST'])
@app.route('/kaka', methods=['GET', 'POST'])
# @login_required
def kaka():
    # ...
    page = request.args.get('page', 1, type=int)
    bookrefs = BookRef.query.paginate(page, app.config['POSTS_PER_PAGE'], False)
    print('bookrefs')
    print(bookrefs)
    return render_template('book-indices.html', titles=bookrefs.items)

# @app.route('/explore')
# # @login_required
# def explore():
#     page = request.args.get('page', 1, type=int)
#     posts = Post.query.order_by(Post.timestamp.desc()).paginate(
#         page, app.config['POSTS_PER_PAGE'], False)
#     return render_template("index.html", title='Explore', posts=posts.items)
