from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
f = open(os.path.join(dir_path, 'user_data.db'), 'w')
f.close()

user_db_url = 'sqlite:///../user_data.db'
engine = create_engine(user_db_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close