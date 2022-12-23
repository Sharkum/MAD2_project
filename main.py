import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource,Api
from application.database import db
from application.workers import celery,ContextTask
from flask_security import Security, SQLAlchemySessionUserDatastore, SQLAlchemyUserDatastore
from application.models import User,Role
from application.config import *

current_dir = os.path.abspath(os.path.dirname(__file__))



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(current_dir, 'database.sqlite3')
app.config.from_object(LocalDevelopmentConfig)
db.init_app(app)
api = Api(app)
app.app_context().push()
celery.conf.update(
    broker_url = app.config["CELERY_BROKER_URL"],
    result_backend = app.config["CELERY_RESULT_BACKEND"]
)
celery.Task = ContextTask

user_datastore =  SQLAlchemySessionUserDatastore(db.session,User,Role)

security = Security(app,user_datastore)



from application.controllers import *

from application.api import UsersAPI,CardsAPI,ListsAPI

api.add_resource(UsersAPI,'/api/getuser')
api.add_resource(CardsAPI,'/api/<int:cardid>/exportcard','/api/updatecards','/api/<int:cardid>/delete')
api.add_resource(ListsAPI,'/api/<int:listid>/exportlist','/api/updatelists')

if __name__ == "__main__":
    app.run(debug = True)
