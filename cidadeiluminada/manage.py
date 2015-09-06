# coding: UTF-8
from __future__ import absolute_import

from flask.ext.script import Manager

from cidadeiluminada import auth

manager = Manager()


@manager.command
def criar_usuario(username, password, role='admin'):
    """
    Cria um usuário com o username e password passados.
    """
    auth.create_user(username, password, role)
