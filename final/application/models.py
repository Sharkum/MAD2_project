from .database import db
from sqlalchemy.orm import declarative_base, relationship
from flask_security import UserMixin,RoleMixin
import datetime
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlite3 import Connection as SQLite3Connection


class Cards(db.Model):
    __tablename__ = 'Cards'
    CardID = db.Column(db.Integer, autoincrement= True, primary_key=True,nullable=False)
    ListID = db.Column(db.Integer,primary_key=True, nullable=False)
    Date_created = db.Column(db.TIMESTAMP, nullable=False)
    Last_modified = db.Column(db.TIMESTAMP, nullable=False)
    Deadline = db.Column(db.TIMESTAMP,  nullable=False)
    Date_completed = db.Column(db.TIMESTAMP)
    Title = db.Column(db.String,nullable=False)
    Value = db.Column(db.Integer, nullable = False)
    Description = db.Column(db.String, nullable = True)
    
    lists = db.relationship('Lists',secondary='Cardlists', backref=db.backref('cards',lazy='dynamic'))
    
    def as_dict(self):
        dic = {}
        for c in self.__table__.columns:
            attr = getattr(self,c.name)
            if isinstance(attr,datetime.datetime):
                attr = attr.strftime("%Y-%m-%dT%H:%M")
            dic[c.name]=attr
        return dic

class Cardlists(db.Model):
    __tablename__ = 'Cardlists'
    ListID = db.Column(db.Integer, db.ForeignKey('Lists.ListID'),primary_key=True, nullable=False)
    CardID = db.Column(db.Integer,db.ForeignKey('Cards.CardID'),nullable=False,primary_key=True)

class Lists(db.Model):
    __tablename__ = 'Lists'
    ListID = db.Column(db.Integer,primary_key=True, nullable=False,autoincrement= True)
    List_name = db.Column(db.String, nullable=False, primary_key=True)
    Description = db.Column(db.String)
    users = db.relationship('User',secondary='Listusers', backref=db.backref('lists',lazy='dynamic'))
    
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Listusers(db.Model):
    __tablename__ = 'Listusers'
    ListID = db.Column(db.Integer, db.ForeignKey('Lists.ListID'),primary_key=True, nullable=False)
    id = db.Column(db.Integer,db.ForeignKey('User.id'),nullable=False,primary_key=True)

class User(db.Model,UserMixin):
    __tablename__ = 'User'
    id = db.Column(db.Integer,nullable=False,unique=True, primary_key=True,autoincrement=True)
    username = db.Column(db.String)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    active = db.Column(db.Boolean())
    fs_uniquifier = db.Column(db.String,unique=True, nullable=False)
    roles= db.relationship('Role',secondary="role_users",backref=db.backref('users',lazy='dynamic'))
    
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
     
class role_users(db.Model):
    __tablename__ = 'role_users'
    role_id = db.Column(db.Integer, db.ForeignKey('Role.role_id'),primary_key=True, nullable=False)
    id = db.Column(db.Integer,db.ForeignKey('User.id'),nullable=False,primary_key=True)

class Role(db.Model,RoleMixin):
    __tablename__ = 'Role'
    role_id = db.Column(db.Integer,nullable=False,unique=True, primary_key=True)
    name = db.Column(db.String)
    Description = db.Column(db.String) 
    