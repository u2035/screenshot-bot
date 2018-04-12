import sqlalchemy
from sqlalchemy import Column, Table, ForeignKey

from sqlalchemy import create_engine
from sqlalchemy import String, Integer, Boolean, PickleType, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
from sqlalchemy import Table, Column, String, MetaData
import datetime

DB_USERNAME = 'root'
DB_PASS = 'root'

db_url = 'mysql+pymysql://{0}:{1}@localhost:3306/u1021'.format(DB_USERNAME, DB_PASS)
# DONT FORGTET TO CREATE u1021 SCHEMA


db = sqlalchemy.create_engine(db_url)
meta = MetaData(db)
status = Table('uD', meta,
                       Column('telegram_id', String(100), unique=True, primary_key=True,),
                       Column('unti_code', String(100),),
                       Column('status', Integer),
                       Column('created_date', DateTime, default=datetime.datetime.utcnow)

    )




conn = db.engine.connect()
try:
    status.create()
except sqlalchemy.exc.InternalError:
    print('Base was already created')


def zcreate(**argv):
    insert_statement = status.insert().values(**argv)#telegram_id="1", status=1)
    conn.execute(insert_statement)

def zget(uid):
    select_statement = status.select(status.c.telegram_id == str(uid))
    result_set = conn.execute(select_statement)
    return result_set.fetchone()

def zupdate(uid, **argv):
    update_statement = status.update().where(status.c.telegram_id == str(uid)).values(**argv)
    conn.execute(update_statement)
