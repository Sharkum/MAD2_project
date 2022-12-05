import json
import datetime , calendar , os, string,random
from distutils.log import Log
from sqlalchemy import extract,func
import numpy as np
import matplotlib.pyplot as plt
from flask import Flask,request,render_template,redirect, url_for,jsonify
from flask import current_app as app
from .models import *
import flask_login
from flask_login import login_required

# code to prevent the app from loading cached images/data and always load only the supplied data.
@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)
def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

@app.route('/', methods = ['GET'])
@login_required
def userpage():
    if request.method == 'GET' :
        curr_user = flask_login.current_user
        UserName = curr_user.username
        curr_lists = curr_user.lists.all()
        list_tup={}
        for l in curr_lists:
            cards = {"card-"+str(card.CardID):card.as_dict() for card in l.cards.all()}
            list_tup["list-"+str(l.ListID)]= {'listinfo':l.as_dict(),'cards':cards}
        
        return render_template('userpage.html',name= UserName, lists = json.dumps(list_tup))

@app.route('/addlist', methods=['POST'])
@login_required
def list_add():
    if request.method == 'POST':
        userid = flask_login.current_user.id
        list_name = request.form.get('list_name')
        list_desc = request.form.get('list_desc')
        new_list = Lists(List_name = list_name,\
                                Description = list_desc)
        db.session.add(new_list)
        db.session.commit()
        new_assn = Listusers(ListID = new_list.ListID,id = userid)
        db.session.add(new_assn)
        db.session.commit()
        return redirect('/')

@app.route('/<int:listid>/addcard', methods=['POST'])
@login_required
def add_card(listid):
    if request.method == 'POST':
        
        new_time = request.form.get('date_created').replace('T',' ')
        new_datetime = datetime.datetime.strptime(new_time, "%Y-%m-%d %H:%M")
        deadline = request.form.get('deadline').replace('T',' ')
        deadline = datetime.datetime.strptime(deadline, "%Y-%m-%d %H:%M")

        new_card = Cards( ListID = listid, \
                        Date_created = new_datetime.replace(second=0), \
                        Last_modified = datetime.datetime.now().replace(second = 0), \
                        Deadline = deadline.replace(second = 0),\
                        Date_completed = None,\
                        Title = request.form.get('Title'),\
                        Value = request.form.get('value'),\
                        Description =request.form.get('desc'))
        
        db.session.add(new_card)
        db.session.commit()
        card_assn = Cardlists( CardID = new_card.CardID,ListID=listid)
        db.session.add(card_assn)
        db.session.commit()

        return redirect('/')

@app.route('/<int:listid>/delete', methods=['POST'])
@login_required
def list_del(listid):
    if request.method == 'POST':
        curr_user = flask_login.current_user
        Lists.query.filter(Lists.ListID == listid).delete()
        Cards.query.filter(Cards.ListID == listid).delete()
        Listusers.query.filter(Listusers.ListID == listid).delete()
        Cardlists.query.filter(Cardlists.ListID == listid).delete()
        db.session.commit()
        return redirect('/')
      
@app.route('/summary', methods=['POST'])  
@login_required
def summarypage():
    if request.method == 'POST':
        curr_user = flask_login.current_user
        curr_lists = curr_user.lists.all()
        metrics={}
        for l in curr_lists:
            cards = l.cards.all()
            cnt = len(cards)
            mean = sum([card.Value for card in cards])/max(cnt,1)
            no_completed = sum([int(card.Date_completed != None) for card in cards])
            no_late = sum([int(card.Date_completed > card.Deadline if card.Date_completed else 0) for card in cards])
            metrics["list-"+str(l.ListID)]= {
                'name':l.List_name,
                'count':cnt,
                'mean': mean,
                'completed':no_completed,
                'late':no_late
            }
        print(metrics)
    return render_template('summary.html',name = curr_user.username,metrics=metrics)
        