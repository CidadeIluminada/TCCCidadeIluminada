# coding: UTF-8
from __future__ import absolute_import

from cidadeiluminada.protocolos import models, rotas, utils


def init_app(app):

    @app.template_filter('date_format')
    def date_format(value):
        return utils.date_format(value)

    @app.template_filter('datetime_format')
    def datetime_format(value):
        return utils.datetime_format(value)

    @app.template_filter('moeda')
    def moeda(value):
        return utils.currency_format(value)

    models.init_app(app)
    rotas.init_app(app)
