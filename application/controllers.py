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
        print(list_tup)
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

@app.route('/<int:listid>/edit', methods=['GET', 'POST'])
def list_edit(listid):
    
    if request.method == 'POST':
        curr_user = flask_login.current_user
        list_info = curr_user.lists.filter(Lists.ListID == listid).first()
        new_tname = request.form.get('list_name')
        new_desc = request.form.get('list_desc')
        list_info.List_name = new_tname
        list_info.Description = new_desc
        db.session.commit()

        return redirect('/')

@app.route('/<int:listid>/addcard', methods=['POST'])
def add_card(listid):
    if request.method == 'POST':
        
        new_time = request.form.get('date_created').replace('T',' ')
        new_datetime = datetime.datetime.strptime(new_time, "%Y-%m-%d %H:%M")
        deadline = request.form.get('deadline').replace('T',' ')
        deadline = datetime.datetime.strptime(deadline, "%Y-%m-%d %H:%M")

        new_card = Cards( ListID = listid, \
                        Date_created = deadline.replace(second=0), \
                        Last_modified = datetime.datetime.now().replace(second = 0), \
                        Deadline = new_datetime.replace(second = 0),\
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


# @app.route('/<string:UserName>/<string:Tracker_name>/delete', methods = ['GET'])
# def tracker_delete(UserName, Tracker_name):
#     if request.method == 'GET':
#         tracker_info = Lists.query.filter(Lists.Tracker_name == Tracker_name).filter(Lists.UserName == UserName).delete()
#         log_info = Logs.query.filter(Logs.Tracker_name == Tracker_name).filter(Logs.UserName == UserName).delete()
#         db.session.commit()

#         return redirect('/'+ UserName+ '/trackers')

# # Shows logs associated with a given user and tracker.
# @app.route('/<string:UserName>/<string:Tracker_name>/logs', methods=['GET', 'POST'])
# def logs_page(UserName, Tracker_name):
#     if request.method == 'GET':

#         logs_queried = Logs.query.filter(Logs.UserName == UserName).filter(Logs.Tracker_name == Tracker_name).all()
#         logs_list = []
#         for i in logs_queried:
#             log_dic = i.__dict__
#             log_dic['Last_modified'] = log_dic['Last_modified'][:16]
#             log_dic['Date_created'] = log_dic['Date_created'][:16]
#             logs_list.append([log_dic['Date_created'], log_dic['Value'], log_dic['Description'], log_dic['Last_modified'], log_dic['LogID']])
        
#         return render_template('logs.html', logs_list= logs_list, name = UserName, tracker_name = Tracker_name)
    
    
#     if request.method == 'POST':
        
#         logs_queried = Logs.query.filter(Logs.UserName == UserName).filter(Logs.Tracker_name == Tracker_name)
#         selected_period = int(request.form.get('period'))

#         present_time = datetime.datetime.now()
#         logs_thisyear = logs_queried.filter(extract('year',Logs.Date_created) == present_time.year)
#         logs_thismonth = logs_thisyear.filter(extract('month',Logs.Date_created) == present_time.month)
#         logs_thisweek = logs_thismonth.filter(extract('week',func.date(Logs.Date_created))== present_time.isocalendar().week)
#         logs_today = logs_thisweek.filter(extract('day',Logs.Date_created) == present_time.day)

#         logs_periodwise = [logs_today,logs_thisweek,logs_thismonth]
#         logs_list = []
#         logs_intime = logs_periodwise[selected_period].all()
        
#         def new(x,y,days):
#             newy = [[] for i in range(days)]
#             for i in range(x.shape[0]):
#                 newy[x[i]].append(int(y[i])) 
#             for i in range(len(newy)):
#                 if newy[i]:
#                     newy[i] = sum(newy[i])/len(newy[i])
#                 else:
#                     newy[i]=0
#             y = np.array(newy)
#             return y

#         def saveplot(y,original_ticks, new_ticks, xlabel):
#             fig = plt.figure()
#             _ = plt.plot(range(1,len(y)+1),y)
#             plt.xticks(original_ticks, new_ticks)
#             plt.ylabel('Average of values by '+ xlabel)
#             plt.xlabel(xlabel)
#             plt.savefig('static/trendline.jpg')
#             return 
        
#         x,y = [],[]
#         for i in logs_intime:
#             log_dic = i.__dict__
#             x.append(datetime.datetime.strptime(i.Date_created[:16],"%Y-%m-%d %H:%M"))
#             y.append(i.Value)
#             log_dic['Last_modified'] = log_dic['Last_modified'][:16]
#             log_dic['Date_created'] = log_dic['Date_created'][:16]
#             logs_list.append([log_dic['Date_created'], log_dic['Value'], log_dic['Description'], log_dic['Last_modified'], log_dic['LogID']])

#         x = np.array(x)
#         y = np.array(y)
        
#         if selected_period == 0:
#             midnight = present_time.replace(hour=0, minute=0, second=0, microsecond=0)
#             if x.shape[0]:
#                 x = np.apply_along_axis(lambda z:z[0].seconds//3600-1,axis=1,arr=(x-midnight).reshape(-1,1))
#                 y = new(x,y,24)
#                 saveplot(y,range(1,25,2),range(1,25,2), "Hours")
#             else:
#                 saveplot([0 for i in range(1,25)],range(0,24,2),range(1,25,2),"Hours")
        
#         if selected_period == 1:
#             if x.shape[0]:
#                 weekstart = present_time - datetime.timedelta(days=present_time.weekday())
#                 x = np.apply_along_axis(lambda z :z[0].days+1,axis=1, arr = (x-weekstart).reshape(-1,1))
#                 y = new(x,y,7)
#                 saveplot(y, range(1,8), ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],"Weekday")
#             else:
#                 saveplot([0 for i in range(1,8)], range(1,8), [ 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],"Weekday")
        
#         if selected_period ==2:
#             if x.shape[0]:
#                 x = np.apply_along_axis(lambda z:z[0].day-1,axis=1,arr=(x).reshape(-1,1))
#                 days_in_month = calendar.monthrange(present_time.year, present_time.month)[1]
#                 y = new(x,y,days_in_month)
#                 saveplot(y, range(1,days_in_month,2), range(1,days_in_month,2),"Day of this month")
#             else:
#                 saveplot([0 for i in range(days_in_month)], range(1,days_in_month,2), range(1,days_in_month,2),"Day of this month")
        
#         return render_template('logs.html', logs_list=logs_list, name = UserName, tracker_name = Tracker_name)



# @app.route('/<string:UserName>/<string:Tracker_name>/logs/<int:LogID>/delete', methods=['GET'])
# def log_delete(UserName,Tracker_name, LogID):
#     if request.method == 'GET' :
#         Log_entry = Logs.query.filter(Logs.LogID == LogID)
#         if Log_entry.first() != []:
#             deleted = Log_entry.delete()
#             db.session.commit()
#             tracker_info = Lists.query.filter(Lists.Tracker_name == Tracker_name).filter(Lists.UserName == UserName).first()
#             tracker_info.Active -= 1
#             db.session.add(tracker_info)
#             db.session.commit()
#         return redirect('/'+ UserName+'/'+ Tracker_name+'/logs')

