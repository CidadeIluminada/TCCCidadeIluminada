# coding: UTF-8
from __future__ import absolute_import

from flask.ext.script import Manager
from unicodecsv import DictReader

_help = 'Comandos do cidadeiluminada'

manager = Manager(help=_help, description=_help)


@manager.command
def criar_admin():
    from cidadeiluminada.models import user_datastore
    admin_role = user_datastore.find_or_create_role('admin')
    user_datastore.create_user(email='admin@cidadeiluminada', password='admin',
                               roles=[admin_role])
    user_datastore.commit()


@manager.command
def carregar_enderecos(filename):
    from cidadeiluminada.base import db
    from cidadeiluminada.protocolos.models import Bairro, Logradouro
    with open(filename, 'r') as csvfile:
        csvreader = DictReader(csvfile)
        bairro = Bairro()
        logradouro = Logradouro()
        for row in csvreader:
            cidade = row['cidade']
            if cidade != u'São José dos Campos':
                continue
            bairro_ = row['bairro']
            if bairro.nome != bairro_:
                bairro = Bairro.query.filter_by(nome=bairro_).first()
                if not bairro:
                    bairro = Bairro(nome=bairro_)
                    db.session.add(bairro)
            cep = row['cep']
            logradouro_ = row['rua']
            logradouro = Logradouro.query.filter_by(cep=cep).first()
            if not logradouro:
                logradouro = Logradouro(cep=cep, logradouro=logradouro_)
                db.session.add(logradouro)
            logradouro.bairro = bairro
    db.session.commit()
