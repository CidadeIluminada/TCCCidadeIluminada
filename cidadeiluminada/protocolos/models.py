# coding: UTF-8
from __future__ import absolute_import

from datetime import datetime
import re

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship, validates
from sqlalchemy.types import Integer, String, DateTime, Boolean

from cidadeiluminada.base import db

cep_re = re.compile(r'^\d{5}-?\d{3}$')


class Regiao(db.Model):
    id = Column(Integer, primary_key=True)
    nome = Column(String(255))

    def __repr__(self):
        return self.nome


class Bairro(db.Model):
    id = Column(Integer, primary_key=True)

    nome = Column(String(255))
    regiao_id = Column(Integer, ForeignKey('regiao.id'))
    regiao = relationship('Regiao', backref='bairros')

    def __repr__(self):
        return u'{} - {}'.format(self.nome, self.regiao)


class Logradouro(db.Model):
    id = Column(Integer, primary_key=True)

    logradouro = Column(String(255))
    cep = Column(String(255))
    bairro_id = Column(Integer, ForeignKey('bairro.id'))
    bairro = relationship('Bairro')

    @validates('cep')
    def validate_cep(self, key, cep):
        if not cep:
            raise ValueError(u'CEP não pode ser vazio')
        if not cep_re.match(cep):
            raise ValueError(u'CEP inválido')
        return cep

    def __repr__(self):
        return u'{} - {} - {}'.format(self.bairro, self.cep, self.logradouro)


class Poste(db.Model):

    id = Column(Integer, primary_key=True)

    logradouro_id = Column(Integer, ForeignKey('logradouro.id'))
    logradouro = relationship('Logradouro', backref='postes')
    numero = Column(Integer)

    def __repr__(self):
        return u'{} - Número {}'.format(self.logradouro, self.numero)


class Protocolo(db.Model):
    # AKA Protocolo 156
    id = Column(Integer, primary_key=True)
    cod_protocolo = Column(String(255))
    criacao = Column(DateTime, default=datetime.now)

    nome_municipe = Column(String(255))
    contato_municipe = Column(String(255))

    item_manutencao_id = Column(Integer, ForeignKey('item_manutencao.id'))
    item_manutencao = relationship('ItemManutencao', backref='protocolos')


class ItemManutencao(db.Model):
    # Parent
    id = Column(Integer, primary_key=True)
    criacao = Column(DateTime, default=datetime.now)

    poste_id = Column(Integer, ForeignKey('poste.id'))
    poste = relationship('Poste', backref='itens_manutencao')

    status = Column(String(255), default='aberto')

    @property
    def aberto(self):
        return self.status == 'aberto'

    @property
    def em_servico(self):
        return self.status == 'em_servico'

    @property
    def fechado(self):
        return self.status == 'fechado'


class ItemManutencaoOrdemServico(db.Model):
    # Association
    id = Column(Integer, primary_key=True)

    ordem_servico_id = Column(Integer, ForeignKey('ordem_servico.id'))
    item_manutencao_id = Column(Integer, ForeignKey('item_manutencao.id'))

    servico_feito = Column(Boolean, default=False)

    ordens_servico = relationship('ItemManutencao', backref='ordens_servico')


class OrdemServico(db.Model):
    # Child
    id = Column(Integer, primary_key=True)
    criacao = Column(DateTime, default=datetime.now)

    itens_manutencao = relationship('ItemManutencaoOrdemServico', backref='ordem_servico')


def init_app(app):
    pass
