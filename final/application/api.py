from flask import make_response, request
from flask_restful import Resource, Api, marshal_with, fields
from .database import db 
from .models import *
from werkzeug.exceptions import HTTPException
import json
from flask_login import current_user
from flask_security import auth_token_required


class DefaultError(HTTPException):
    def __init__(self, status_code, desc):
        self.response = make_response('', status_code)
        self.description = "<p>"+desc+"</p>"

class Success(HTTPException):
    def __init__(self, status_code, msg):
        self.response = make_response(msg, status_code)

class BError(HTTPException):
    def __init__(self, status_code, errorcode, errormsg):
        message = {
  "error_code": errorcode,
  "error_message": errormsg
}
        self.response = make_response(json.dumps(message), status_code)

cardinfo = {
    "CardID" : fields.Integer,
    "ListID" : fields.Integer,
    "Date_created" : fields.DateTime,
    "Last_modified" : fields.DateTime,
    "Deadline": fields.DateTime,
    "Date_completed":fields.DateTime,
    "Value":fields.Integer,
    "Description":fields.String
}
listinfo = {
    "ListID": fields.Integer,
    "List_name": fields.String,
    "Description": fields.String
}

class UsersAPI(Resource):
    def get(self):
        try:
            curr_user = current_user.first()
        except:
            raise DefaultError(status_code=500, desc='Internal Server Error ')
        if curr_user:
            user_lists = Listusers.query.filter(Listusers.id == curr_user.id).lists.all()
            if user_lists:
                return {"Lists": [a.as_dic() for a in user_lists]} 
            else:
                raise DefaultError(status_code=404, desc="No Lists found for the given user\n")
        else:
            raise DefaultError(status_code=404, desc="User doesn't exist.\n")

class CardsAPI(Resource):
    @auth_token_required
    def post(self):
        try:
            curr_user = current_user
            details = json.loads(request.get_data())
        except:
            raise DefaultError(status_code=400, desc='Bad Request')
        result = []
        for card in details.values():
            try:
                cardid = card['CardID']
                datecomp=None
                if card['Date_completed'] != None:
                    datecomp = datetime.datetime.strptime(card['Date_completed'].split('.')[0][:-3], "%Y-%m-%dT%H:%M")
                    
                updatedcard = {
                    "ListID": card['ListID'],
                    "Date_created":datetime.datetime.strptime(card['Date_created'], "%Y-%m-%dT%H:%M"),
                    "Last_modified":datetime.datetime.strptime(card['Last_modified'], "%Y-%m-%dT%H:%M"),
                    "Deadline":datetime.datetime.strptime(card['Deadline'], "%Y-%m-%dT%H:%M"),
                    "Date_completed":datecomp,
                    "Title":card['Title'],
                    "Value":card['Value'],
                    "Description":card['Description'],
                }
                dbcard = Cards.query.filter(Cards.CardID == cardid).update(updatedcard)
                assn = Cardlists.query.filter(Cardlists.CardID == cardid).update({'ListID':card['ListID']})
                db.session.commit()
                result.append(cardid)
            except:
                raise DefaultError(status_code=500, desc="Internal Server Error")
        return json.dumps(result)
    
    @auth_token_required
    def delete(self,cardid):
        try:
            Cards.query.filter(Cards.CardID == cardid).delete()
            Cardlists.query.filter(Cardlists.CardID == cardid).delete()
            db.session.commit()
        except:
            raise DefaultError(status_code=500, desc="Internal Server Error")
        
        return json.dumps(str(cardid)+" deleted successfuly")
    
class ListsAPI(Resource):
    @auth_token_required
    def post(self):
        try:
            curr_user = current_user
            details = json.loads(request.get_data())
        except:
            raise DefaultError(status_code=400, desc='Bad Request')
        result = []
        for list in details.values():
            try:
                listid = list['ListID']
                    
                updatedlist = {
                    "List_name": list['List_name']
                }
                dbcard = Lists.query.filter(Lists.ListID == listid).update(updatedlist)
                db.session.commit()
                result.append(listid)
            except:
                raise DefaultError(status_code=500, desc="Internal Server Error")
        return json.dumps(result)