import os

import sqlalchemy
basedir = os.path.abspath(os.path.dirname(__file__))

class Config():
    DEBUG = False 
    SQLITE_DB_DIR = None
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False 
    WTF_CSRF_ENABLED = False
    SECURITY_TOKEN_AUTHENTICATION_HEADER = "Authentication-Token"
    CELERY_BROKER_URL = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND = "redis://localhost:6379/2"

class LocalDevelopmentConfig(Config):
    SQLITE_DB_DIR = os.path.join(basedir,"../db_directory")
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.sqlite3'
    DEBUG = True 
    SECRET_KEY = "5ls3k26nv35lvci25"
    SECURITY_PASSWORD_HASH = "bcrypt"
    SECURITY_PASSWORD_SALT = "asdlj236mfg90al"
    SECURITY_REGISTERABLE = True
    SECURITY_SEND_REGISTER_EMAIL = False
    SECURITY_UNAUTHORIZED_VIEW = None
    SECURITY_USERNAME_ENABLE = True
    CELERY_BROKER_URL = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND = "redis://localhost:6379/2"
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300