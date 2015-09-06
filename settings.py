#coding=UTF-8
import os

DEBUG = True

CSRF_ENABLED = True
SECRET_KEY = 'dontcare'

#SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://user:password@localhost:port/cidadeiluminada?client_encoding=utf8'

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'tmp')

ALLOWED_EXTENSIONS = set(['.png', '.jpg'])

POSTMON_URL = 'http://api.postmon.com.br/v1/cep/'

ASSETS_DEBUG = True

PUSHER_APP_ID = '111236'
PUSHER_KEY = 'fc395600761a186d792b'
PUSHER_SECRET = 'e48daff4ba24fdea57ac'
