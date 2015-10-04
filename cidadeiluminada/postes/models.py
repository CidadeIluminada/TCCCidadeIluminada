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

    def calcular_delta(self, numero):
        delta = abs(self.numero - numero)
        if delta <= 10:
            return delta

    def __repr__(self):
        return '{}-{}'.format(self.cep, self.numero)


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
        return cep

    def preencher_cep(self):
        info = postmon.get_by_cep(self.cep)
        self.cidade = info['cidade']
        self.estado = info['estado']
        self.logradouro = info['logradouro']
        nome_bairro = info['bairro']
        bairro = Bairro.query.filter_by(nome=nome_bairro).first()
        self.bairro = bairro

    def descobrir_poste(self):
        postes = Poste.query.filter_by(cep=self.cep).all()
        filtrados = [p for p in postes if p.calcular_delta(self.numero) is not None]
        if len(filtrados) == 1:
            self.poste = filtrados[0]

    def verificar_duplicidade(self):
        if not self.poste:
            return None
        pendencias_q = Pendencia.query.filter_by(cep=self.cep).filter(Pendencia.poste != None)
        if self.id:
            pendencias_q = pendencias_q.filter(Pendencia.id != self.id)
        pendencias = pendencias_q.all()
        for pendencia in pendencias:
            if self.poste == pendencia.poste:
                return True
        return False

    poste_id = Column(Integer, ForeignKey('poste.id'))
    poste = relationship('Poste', backref='pendencias')
