# coding: UTF-8
from __future__ import absolute_import

from cidadeiluminada.protocolos import models, rotas, utils


def init_app(app):

    @app.template_filter('datetime_format')
    def datetime_format(input):
        return utils.datetime_format(input)

    models.init_app(app)
    rotas.init_app(app)
