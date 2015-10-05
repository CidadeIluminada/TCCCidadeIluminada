# coding: UTF-8
from __future__ import absolute_import

from flask import Flask, redirect, url_for
from flask.ext.assets import Environment

from cidadeiluminada import base, postes
from cidadeiluminada.base import AppJSONEncoder


def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('settings')
    app.config.from_pyfile('settings_local.py', silent=True)
    app.json_encoder = AppJSONEncoder

    app.config.setdefault('SQLALCHEMY_DATABASE_URI', 'postgresql+psycopg2://cidadeiluminada:cidadeiluminada@localhost/cidadeiluminada')

    if config:
        app.config.update(config)

    Environment(app)
    base.init_app(app)
    postes.init_app(app)

    @app.route('/')
    def index():
        return redirect(url_for('postes.index'))

    @app.route('/postmon/')
    def postmon():
        from flask import jsonify, request
        from cidadeiluminada.services import postmon
        cep = request.args['cep']
        data = postmon.get_by_cep(cep)
        return jsonify(data)

    @app.context_processor
    def menu_items():
        return {
            'menu_items': [
                (u'Protocolos', 'protocolos.index'),
                (u'(ALPHA) Novo protocolo', 'protocolos.novo_pagina'),
                (u'Gerenciar usuários', 'auth.gerenciar')
            ]
        }

    return app
