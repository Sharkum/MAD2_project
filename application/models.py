from sqlalchemy import ForeignKey
from .database import db
from sqlalchemy.orm import declarative_base, relationship
from flask_security import UserMixin

class Cards(db.Model):
    __tablename__ = 'Cards'
    CardID = db.Column(db.Integer, autoincrement= True, primary_key=True)
    UserName = db.Column(db.String, ForeignKey('User.UserName'), nullable=False)
    List_name = db.Column(db.String, nullable=False)
    Date_created = db.Column(db.TIMESTAMP, nullable=False)
    Last_modified = db.Column(db.TIMESTAMP, nullable=False)
    Deadline = db.Column(db.TIMESTAMP,  nullable=False)
    Date_completed = db.Column(db.TIMESTAMP)
    Value = db.Column(db.Integer, nullable = False)
    Description = db.Column(db.String, nullable = True)

class Lists(db.Model):
    __tablename__ = 'Lists'
    UserName = db.Column(db.String, nullable=False, primary_key=True)
    List_name = db.Column(db.String, nullable=False, primary_key=True)
    Description = db.Column(db.String)
    Active = db.Column(db.Integer, nullable=False)

class User(db.Model):
    __tablename__ = 'User'
    UserName = db.Column(db.String, nullable=False, unique=True, primary_key=True)
    Password = db.Column(db.String, nullable=False)
    fs_uniquifier = db.Column(db.String,unique=True, nullable=False)
