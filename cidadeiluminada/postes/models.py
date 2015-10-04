# coding: UTF-8
from __future__ import absolute_import

from datetime import datetime

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String, DateTime, Text

from cidadeiluminada.base import db


class Poste(db.Model):

    id = Column(Integer, primary_key=True)

    cep = Column(String(10))
    estado = Column(String(2))
    cidade = Column(Text)
    bairro_id = Column(Integer, ForeignKey('bairro.id'))
    bairro = relationship('Bairro', backref='postes')
    logradouro = Column(Text)
    numero = Column(Text)

    def has_full_address(self):
        return bool(self.estado and self.cidade and self.bairro and self.logradouro)


class ZonaCidade(db.Model):
    id = Column(Integer, primary_key=True)
    nome = Column(String(255))

    def __repr__(self):
        return self.nome


class Bairro(db.Model):
    id = Column(Integer, primary_key=True)

    nome = Column(String(255))
    zona_id = Column(Integer, ForeignKey('zona_cidade.id'))
    zona = relationship('ZonaCidade', backref='bairros')

    def __repr__(self):
        return self.nome


class Pendencia(db.Model):
    id = Column(Integer, primary_key=True)
    criacao = Column(DateTime, default=datetime.now)

    cep = Column(String(10))
    estado = Column(String(2))
    cidade = Column(Text)
    bairro_id = Column(Integer, ForeignKey('bairro.id'))
    bairro = relationship('Bairro', backref='pendencias')
    logradouro = Column(Text)
    numero = Column(Text)

    def has_full_address(self):
        return bool(self.estado and self.cidade and self.bairro and self.logradouro)

    poste_id = Column(Integer, ForeignKey('poste.id'))
    poste = relationship('Poste', backref='pendencias')
