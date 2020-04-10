import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# TODO: os -> url
DATABASE_URL = 'postgresql://journalize:12345678@localhost/journalize_db'

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
