# coding: UTF-8
from __future__ import absolute_import

from flask.ext.admin import Admin

from cidadeiluminada.postes import models, rotas  # NOQA


def init_app(app):
    admin_config = {
        'endpoint': 'postes',
        'url': '/postes',
        'name': 'Postes'
    }
    index_view, views = rotas.init_app(app, admin_config)
    admin = Admin(app, template_mode='bootstrap3', index_view=index_view, **admin_config)
    for view in views:
        admin.add_view(view)
