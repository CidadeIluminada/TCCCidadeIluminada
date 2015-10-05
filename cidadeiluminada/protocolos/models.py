# coding: UTF-8
from __future__ import absolute_import

from datetime import datetime
import re

from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.orm import relationship, validates
from sqlalchemy.types import Integer, String, DateTime

from cidadeiluminada.base import db
from cidadeiluminada.services import postmon

cep_re = re.compile(r'^\d{5}-?\d{3}$')


class Poste(db.Model):

    id = Column(Integer, primary_key=True)

    rua_id = Column(Integer, ForeignKey('rua.id'))
    rua = relationship('Rua', backref='postes')
    numero = Column(Integer)

    def calcular_delta(self, numero):
        delta = abs(self.numero - numero)
        if delta <= 10:
            return delta

    def __repr__(self):
        return '{}-{}'.format(self.rua.cep, self.numero)


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


class Rua(db.Model):
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


class Protocolo(db.Model):
    id = Column(Integer, primary_key=True)
    cod_protocolo = Column(String(255))
    criacao = Column(DateTime, default=datetime.now)

    nome_municipe = Column(String(255))
    contato_municipe = Column(String(255))

    pendencia_id = Column(Integer, ForeignKey('pendencia.id'))
    pendencia = relationship('Pendencia', backref='protocolos')


class Pendencia(db.Model):
    id = Column(Integer, primary_key=True)
    criacao = Column(DateTime, default=datetime.now)

    poste_id = Column(Integer, ForeignKey('poste.id'))
    poste = relationship('Poste', backref='pendencias')
    rua_id = Column(Integer, ForeignKey('rua.id'))
    rua = relationship('Rua', backref='pendencias')

    def preencher_endereco(self):
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
            if self.poste == pendencia.poste or self.numero == pendencia.numero:
                return True
        return False

protocolo_ordem_servico = Table('protocolos_ordens', db.metadata,
                                Column('id', Integer, primary_key=True),
                                Column('ordem_servico_id', Integer, ForeignKey('ordem_servico.id')),
                                Column('pendencia_id', Integer, ForeignKey('pendencia.id')))


class OrdemServico(db.Model):
    id = Column(Integer, primary_key=True)
    criacao = Column(DateTime, default=datetime.now)

    pendencias = relationship('Pendencia', secondary=protocolo_ordem_servico,
                              backref='ordens_servico')

    @validates('pendencias')
    def validate_protocolos(self, key, pendencias):
        if len(self.pendencias) == 50:
            raise ValueError(u'Máximo de serviços atingidos na Ordem de serviço')
        return pendencias
