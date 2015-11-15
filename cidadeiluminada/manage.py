# coding: UTF-8
from __future__ import absolute_import

from flask.ext.script import Manager

_help = 'Comandos do cidadeiluminada'

manager = Manager(help=_help, description=_help)


@manager.command
def criar_admin():
    from cidadeiluminada.models import user_datastore
    admin_role = user_datastore.find_or_create_role('admin')
    user_datastore.create_user(email='admin@cidadeiluminada', password='admin',
                               roles=[admin_role])
    user_datastore.commit()
