from database import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from database import engine

class Posts(Base):
    """Post model for DataBase"""
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    tag = Column(String)
    owner_id = Column(Integer, ForeignKey('users.id'))

class Users(Base):
    """User model for DataBase"""
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    password = Column(String)


# Base.metadata.create_all(bind=engine)                           # create tables
