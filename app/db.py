import os
from databases import Database
from sqlalchemy import (create_engine, ForeignKey, MetaData, Table, Column, Integer, String, DateTime, ARRAY)
from sqlalchemy.sql import func


DATABASE_URL = 'postgresql://journalize:12345678@localhost/journalize_db'
engine = create_engine(DATABASE_URL)
metadata = MetaData()


types_table = Table(
    'types',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('title', String(32), unique=True, nullable=False),
    Column('description', String(254)),
    Column('created_date', DateTime, default=func.now(), nullable=False),
    Column('updated_date', DateTime, default=func.now(), nullable=False)
)


devices_table = Table(
    'devices',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('type', Integer, default=0),
    Column('title', String(64)),
    Column('description', String(254)),
    Column('created_date', DateTime, default=func.now(), nullable=False),
    Column('updated_date', DateTime, default=func.now(), nullable=False)
)


journal_table = Table(
    'journal',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('device_id', Integer, nullable=False),
    Column('key', String(), nullable=False),
    Column('value', String(), nullable=False),
    Column('dt', DateTime, default=func.now(), nullable=False)
)

database = Database(DATABASE_URL)
