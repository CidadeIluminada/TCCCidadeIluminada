# coding: UTF-8
from __future__ import absolute_import

from flask.ext.migrate import Migrate
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_app(app):
    db.init_app(app)
    Migrate(app, db)
