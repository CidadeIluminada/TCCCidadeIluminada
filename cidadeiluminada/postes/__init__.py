# coding: UTF-8
from __future__ import absolute_import

from flask.ext.admin import Admin

from cidadeiluminada.postes import models, rotas  # NOQA


def init_app(app):
    admin = Admin(app, endpoint='postes', template_mode='bootstrap3',
                  name='Postes', url='/postes',
                  base_template='base_poste.html')
    for view in rotas.init_app(app):
        admin.add_view(view)
