from application.workers import celery
from datetime import datetime 

@celery.task()
def export_csv(file,dir):
    file.to_csv(dir)