# coding: UTF-8
from __future__ import absolute_import

from cidadeiluminada.protocolos import models, rotas


def init_app(app):
    @app.template_filter('checkmark')
    def checkmark(input):
        return u'\u2713' if input else u'\u2718'

    models.init_app(app)
    rotas.init_app(app)
