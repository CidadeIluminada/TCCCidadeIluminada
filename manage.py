#coding=UTF-8
from __future__ import absolute_import

from flask.ext.script import Manager, Server
from flask.ext.migrate import MigrateCommand

from cidadeiluminada import create_app
from cidadeiluminada.manage import manager as cidadeiluminada_manager

app = create_app()

manager = Manager(app)
manager.add_command('ci', cidadeiluminada_manager)
manager.add_command('db', MigrateCommand)
manager.add_command('runserver', Server())


if __name__ == '__main__':
    manager.run()
