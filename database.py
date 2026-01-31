from sqlalchemy import create_engine, Column, String, Integer, DateTime, ForeignKey
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


DATABASE_URL = "postgresql://admin:password@localhost:5432/urlshortener"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class URLModel(Base):
    __tablename__ = "urls"
    
    code = Column(String, primary_key=True, index=True)
    url = Column(String, nullable=False)
    clicks = Column(Integer, default=0)
    created_time = Column(DateTime, default=datetime.now)
    expires_time = Column(DateTime, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'))

class UserModel(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_time = Column(DateTime, default=datetime.now)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()