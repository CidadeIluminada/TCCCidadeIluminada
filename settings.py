#coding=UTF-8

CSRF_ENABLED = True
SECRET_KEY = 'dontcare'

SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://user:password@localhost:port/cidadeiluminada?client_encoding=utf8'

POSTMON_URL = 'http://api.postmon.com.br/v1/cep/'

BABEL_DEFAULT_LOCALE = 'pt_br'

SECURITY_URL_PREFIX = '/auth'

MAIL_SERVER = 'smtp.xxx'
MAIL_PORT = 420
MAIL_USERNAME = 'username'
MAIL_PASSWORD = 'password'
MAIL_DEFAULT_SENDER = ('No reply', 'no-reply@xxx')

SECURITY_REGISTERABLE = True
SECURITY_SEND_REGISTER_EMAIL = False
SECURITY_SEND_PASSWORD_CHANGE_EMAIL = False
SECURITY_SEND_PASSWORD_RESET_NOTICE_EMAIL = False
