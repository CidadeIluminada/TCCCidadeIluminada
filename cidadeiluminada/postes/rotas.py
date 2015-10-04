# coding: UTF-8
from __future__ import absolute_import

from flask.ext.admin.contrib.sqla import ModelView

from cidadeiluminada.postes.models import Poste, Pendencia, ZonaCidade, Bairro
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
    category = 'Protocolos'

    form_widget_args = {
        'estado': {
            'readonly': True,
        },
        'cidade': {
            'readonly': True,
        }
    }

    form_args = {
        'estado': {
            'default': u'SP',
        },
        'cidade': {
            'default': u'São José dos Campos',
        }
    }


class PendenciaView(_ModelView):
    model = Pendencia
    name = 'Protocolos'
    category = 'Protocolos'


class ZonaCidadeView(_ModelView):
    model = ZonaCidade
    name = 'Zona'
    category = 'Bairro'


class BairroView(_ModelView):
    model = Bairro
    name = 'Bairro'
    category = 'Bairro'

    form_columns = ('zona', 'nome')


def init_app(app):
    return [PosteView(), PendenciaView(), ZonaCidadeView(), BairroView()]
