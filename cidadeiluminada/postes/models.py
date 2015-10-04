# coding: UTF-8
from __future__ import absolute_import

from datetime import datetime
import re

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship, validates
from sqlalchemy.types import Integer, String, DateTime, Text

from cidadeiluminada.base import db
from cidadeiluminada.services import postmon

cep_re = re.compile(r'^\d{5}-?\d{3}$')

class Poste(db.Model):

    id = Column(Integer, primary_key=True)

    cep = Column(String(10))
    estado = Column(String(2))
    cidade = Column(Text)
    bairro_id = Column(Integer, ForeignKey('bairro.id'))
    bairro = relationship('Bairro', backref='postes')
    logradouro = Column(Text)
    numero = Column(Integer)

    @property
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
        return u'{} - {}'.format(self.nome, self.zona.nome)


class Pendencia(db.Model):
    id = Column(Integer, primary_key=True)
    criacao = Column(DateTime, default=datetime.now)

    cep = Column(String(10))
    estado = Column(String(2))
    cidade = Column(Text)
    bairro_id = Column(Integer, ForeignKey('bairro.id'))
    bairro = relationship('Bairro', backref='pendencias')
    logradouro = Column(Text)
    numero = Column(Integer)

    @validates('cep')
    def validate_cep(self, key, cep):
        if not cep:
            raise ValueError(u'CEP não pode ser vazio')
        if not cep_re.match(cep):
            raise ValueError(u'CEP inválido')
        info = postmon.get_by_cep(cep)
        self.cidade = info['cidade']
        self.estado = info['estado']
        self.logradouro = info['logradouro']
        nome_bairro = info['bairro']
        print nome_bairro
        bairro = Bairro.query.filter_by(nome=nome_bairro).first()
        self.bairro = bairro
        return cep

    @property
    def has_full_address(self):
        return bool(self.estado and self.cidade and self.bairro and self.logradouro)

    poste_id = Column(Integer, ForeignKey('poste.id'))
    poste = relationship('Poste', backref='pendencias')
