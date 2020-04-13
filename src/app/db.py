import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

LOCAL_DATABASE_URL = 'postgresql://journalize:12345678@localhost/journalize_db'
DATABASE_URL = os.getenv('DATABASE_URL', LOCAL_DATABASE_URL)
engine = create_engine(DATABASE_URL)
Base = declarative_base()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
