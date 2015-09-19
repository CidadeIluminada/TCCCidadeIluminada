# coding: UTF-8
from __future__ import absolute_import

from datetime import datetime

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String, DateTime, Text

from cidadeiluminada.base import db, JSONSerializationMixin


class Poste(db.Model, JSONSerializationMixin):

    id = Column(Integer, primary_key=True)
    cod_poste = Column(String(255))

    cep = Column(String(10))
    estado = Column(String(2))
    cidade = Column(Text)
    bairro = Column(Text)
    logradouro = Column(Text)
    numero = Column(Text)

    def has_full_address(self):
        return self.estado and self.cidade and self.bairro and self.logradouro

    tipo_poste = Column(String(255))


class Pendencia(db.Model, JSONSerializationMixin):
    id = Column(Integer, primary_key=True)

    timestamp = Column(DateTime, default=datetime.now)

    tipo = Column(String(255))
    status = Column(String(255))
    obs = Column(Text)

    poste_id = Column(Integer, ForeignKey('poste.id'))
    poste = relationship('Poste', backref='pendencias')
