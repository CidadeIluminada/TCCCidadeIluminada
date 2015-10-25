# coding: UTF-8
from __future__ import absolute_import

from flask.ext.security import SQLAlchemyUserDatastore, UserMixin, RoleMixin

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.types import Integer, String, Boolean

from cidadeiluminada.base import db, security

# Define models
roles_users = db.Table(
    'roles_users',
    Column('user_id', Integer(), ForeignKey('user.id')),
    Column('role_id', Integer(), ForeignKey('role.id'))
)


class Role(db.Model, RoleMixin):
    id = Column(Integer(), primary_key=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))

    def __repr__(self):
        return self.name


class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    password = Column(String(255))
    roles = relationship('Role', secondary=roles_users,
                         backref=backref('users', lazy='dynamic'))
    active = Column(Boolean(), default=True)

    def __repr__(self):
        return '{} ({})'.format(self.email, ', '.join([role.name for role in self.roles]))


def init_app(app):
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security.init_app(app, user_datastore)
