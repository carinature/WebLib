import pymysql
import pandas as pd
import sys
from sqlalchemy import create_engine


host = 'moblid.mysql.pythonanywhere-services.com'
user = 'moblid'
password = 's4MYP9KSyYkZ6B6'

engine = create_engine("mysql+pymysql://{user}:{pw}@moblid.mysql.pythonanywhere-services.com/{db}"
                       .format(user="moblid",
                               pw="s4MYP9KSyYkZ6B6",
                               db="moblid$default"))

try:



    print('Connected to DB: {}'.format(host))
    print('Succuessfully loaded the table from csv1.')
except Exception as e:
    print('Error: {}'.format(str(e)))
    sys.exit(1)

