# coding: UTF-8
from __future__ import absolute_import
import os
import re

from flask import current_app
from flask.ext.wtf import Form
from wtforms.fields import FileField
from wtforms.validators import ValidationError, Required, Email, Length, \
    Optional
from wtforms_sqlalchemy.orm import model_form

from cidadeiluminada.protocolos.models import Protocolo


def validate_cep(form, field):
    cep_re = re.compile(r'^\d{5}-?\d{3}$')
    if not cep_re.match(field.data):
        raise ValidationError(u'CEP inválido')

_protocolos_fields_args = {
    'cod_protocolo': {
        'validators': [Required()],
        'label': u'Código Protocolo',
    },
    'cep': {
        'validators': [Required(), validate_cep],
        'label': u'CEP',
    },
    'email': {
        'validators': [Email(), Optional()],
        'label': u'E-mail',
    },
    'nome': {
        'label': u'Nome',
        'validators': [Optional()]
    },
    'estado': {
        'validators': [Optional(), Length(min=2, max=2)],
        'label': u'UF',
    },
    'cidade': {
        'label': u'Cidade',
    },
    'bairro': {
        'label': u'Bairro',
    },
    'logradouro': {
        'label': u'Logradouro',
    },
    'numero': {
        'label': u'Número',
    },
}

_ProtocoloForm = model_form(Protocolo, field_args=_protocolos_fields_args,
                            base_class=Form, exclude=['timestamp'])


class ProtocoloForm(_ProtocoloForm):
    arquivo_protocolo = FileField(validators=[Required()])

    def validate_arquivo_protocolo(self, field):
        filename = field.data.filename
        allowed_filename = os.path.splitext(filename)[1] in \
            current_app.config['ALLOWED_EXTENSIONS']
        if not allowed_filename:
            raise ValidationError(u'Arquivo inválido')
