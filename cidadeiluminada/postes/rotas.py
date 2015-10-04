# coding: UTF-8
from __future__ import absolute_import

from flask.ext.admin.contrib.sqla import ModelView

from cidadeiluminada.postes.models import Poste, Pendencia
from cidadeiluminada.base import db


class _ModelView(ModelView):

    category = None

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('name', self.name)
        kwargs.setdefault('category', self.category)
        super(_ModelView, self).__init__(self.model, db.session, *args, **kwargs)


class PosteView(_ModelView):
    model = Poste
    name = 'Postes'


class PendenciaView(_ModelView):
    model = Pendencia
    name = 'Pendencia'


def init_app(app):
    return [PosteView(), PendenciaView()]
