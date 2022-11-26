from .database import db
from sqlalchemy.orm import declarative_base, relationship
from flask_security import UserMixin,RoleMixin

class Cards(db.Model):
    __tablename__ = 'Cards'
    CardID = db.Column(db.Integer, autoincrement= True, primary_key=True)
    ListID = db.Column(db.Integer,primary_key=True, nullable=False,autoincrement= True)
    Date_created = db.Column(db.TIMESTAMP, nullable=False)
    Last_modified = db.Column(db.TIMESTAMP, nullable=False)
    Deadline = db.Column(db.TIMESTAMP,  nullable=False)
    Date_completed = db.Column(db.TIMESTAMP)
    Value = db.Column(db.Integer, nullable = False)
    Description = db.Column(db.String, nullable = True)
    users = db.relationship('User',secondary='Listusers')
    
class Cardlists(db.Model):
    __tablename__ = 'Cardlists'
    ListID = db.Column(db.Integer, db.Foreignkey('Lists.ListID'),primary_key=True, nullable=False)
    CardID = db.Column(db.Integer,db.Foreignkey('Cards.CardID'),nullable=False,primary_key=True,autoincrement=True)

class Lists(db.Model):
    __tablename__ = 'Lists'
    ListID = db.Column(db.Integer,primary_key=True, nullable=False,autoincrement= True)
    List_name = db.Column(db.String, nullable=False, primary_key=True)
    Description = db.Column(db.String)
    users = db.relationship('User',secondary='Listusers')

class Listusers(db.Model):
    __tablename__ = 'Listusers'
    ListID = db.Column(db.Integer, db.Foreignkey('Lists.ListID'),primary_key=True, nullable=False)
    id = db.Column(db.Integer,db.Foreignkey('User.id'),nullable=False,primary_key=True,autoincrement=True)

class User(db.Model,UserMixin):
    __tablename__ = 'User'
    id = db.Column(db.Integer,nullable=False,unique=True, primary_key=True,autoincrement=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    active = db.Column(db.Boolean())
    fs_uniquifier = db.Column(db.String,unique=True, nullable=False)
    roles= db.relationship('Role',secondary="Role",backref=db.backref('users',lazy='dynamic'))
    
class Role(db.Model,RoleMixin):
    __tablename__ = 'Role'
    id = db.Column(db.Integer,nullable=False,unique=True, primary_key=True)
    UserName = db.Column(db.String, unique=True)