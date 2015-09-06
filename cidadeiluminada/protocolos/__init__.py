# coding: UTF-8
from __future__ import absolute_import

from cidadeiluminada.protocolos import models, rotas  # NOQA


def init_app(app):
    rotas.init_app(app)
