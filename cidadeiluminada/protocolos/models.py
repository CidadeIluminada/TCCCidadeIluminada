# coding: UTF-8
from __future__ import absolute_import

from datetime import datetime

from sqlalchemy import Column
from sqlalchemy.types import Integer, String, DateTime, Text

from cidadeiluminada.base import db, JSONSerializationMixin


class Protocolo(db.Model, JSONSerializationMixin):

    id = Column(Integer, primary_key=True)
    cod_protocolo = Column(String(255))
    status = Column(String(255), default='NOVO')

    timestamp = Column(DateTime, default=datetime.utcnow)

    filename = Column(String(255))

    cep = Column(String(255))

    @db.validates('cep')
    def trim_cep(self, key, value):
        return value.replace('-', '')

    estado = Column(String(2))
    cidade = Column(Text)
    bairro = Column(Text)
    logradouro = Column(Text)
    numero = Column(Text)

    def has_full_address(self):
        return self.estado and self.cidade and self.bairro and self.logradouro

    nome = Column(String(255))
    email = Column(String(255))
