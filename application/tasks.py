from application.workers import celery
from datetime import datetime 
import pandas as pd
from celery.schedules import crontab
from .models import *
from jinja2 import Template
import requests,smtplib
from sqlalchemy import extract
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMPTP_SERVER_HOST = "localhost"
SMPTP_SERVER_PORT = 1025
SENDER_ADDRESS = "sharan@mailhog.com"
SENDER_PASSOWRD = ""

@celery.on_after_finalize.connect
def periodic_tasks(sender,**kwargs):
    sender.add_periodic_task(crontab(hour=6,minute=19),daily_reminder.s('There are some tasks left to be done.'),)
    
    sender.add_periodic_task(crontab(day_of_month=1),send_email.s())

@celery.task()
def daily_reminder(msg):
        if not all(x.Date_completed for x in Cards.query.all()):
            url = 'https://chat.googleapis.com/v1/spaces/AAAAqRfiqNA/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=0is9XR063ddfzdHyrGBXWVzTqJi3RAnTGohcAy1wSlA%3D'
            response = requests.post(url,json={"text":msg})
        return

@celery.task()
def export_csv(file,dir):
    df = pd.DataFrame(file)
    df.to_csv(dir)
    return

@celery.task()
def send_email():
    currtime = datetime.datetime.now()
    cards = Cards.query.filter(extract('month',Cards.Date_created) == currtime.month).all()
    
    tasks_completed = sum([card.Date_completed != None for card in cards])
    late = sum([int(card.Date_completed > card.Deadline if card.Date_completed else 0) for card in cards])
    hours_spent = sum([card.Value for card in cards])

    msg = MIMEMultipart()
    msg["From"] = SENDER_ADDRESS
    msg["To"] = "sharan342.kumar@example.com"
    msg["Subject"] = "Monthly Reminder"

    file = open('templates/monthly.html')
    message = Template(file.read())
    
    msg.attach(MIMEText(message.render(tasks_completed=tasks_completed,late=late,hours_spent=hours_spent),'html'))
    
    s = smtplib.SMTP(host=SMPTP_SERVER_HOST, port=SMPTP_SERVER_PORT)
    s.login(SENDER_ADDRESS,SENDER_PASSOWRD)
    s.send_message(msg)
    s.quit()

    return True 
