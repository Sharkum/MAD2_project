from flask import make_response, request,session
import pandas as pd
from flask_restful import Resource, Api, marshal_with, fields
from .database import db 
from .models import *
from .tasks import export_csv
from werkzeug.exceptions import HTTPException
import json
from flask_login import current_user
from flask_security import auth_token_required
from .controllers import cache


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
        return json.dumps(cache.get('userid'))

class CardsAPI(Resource):
    @auth_token_required
    def get(self,cardid):
        card = Cards.query.filter(Cards.CardID == cardid).first()
        cards = [card.as_dict()]
        export_csv.delay(cards,"downloads/cards/card-"+str(cardid)+"_"+card.Last_modified.strftime("%Y-%m-%d_%H:%M")+".csv")
        return
        
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
                    datecomp = datetime.datetime.strptime(card['Date_completed'], "%Y-%m-%dT%H:%M")
                    
                updatedcard = {
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
    def get(self,listid):
        cards = Lists.query.filter(Lists.ListID == listid).first().cards.all()
        cards = [card.as_dict() for card in cards]
        export_csv.delay(cards,"downloads/lists/list-"+str(listid)+".csv")
        return
    
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
