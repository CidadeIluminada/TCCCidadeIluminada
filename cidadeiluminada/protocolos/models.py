# coding: UTF-8
from __future__ import absolute_import

from datetime import datetime, date
import re

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship, validates
from sqlalchemy.types import Integer, String, DateTime, Boolean, Numeric, Date, Text
from sqlalchemy.ext.hybrid import hybrid_property

from cidadeiluminada.base import db, JSONSerializationMixin

cep_re = re.compile(r'^\d{5}-?\d{3}$')


class Regiao(db.Model):
    id = Column(Integer, primary_key=True)
    nome = Column(String(255))

    def __repr__(self):
        return self.nome


class Bairro(db.Model, JSONSerializationMixin):
    id = Column(Integer, primary_key=True)

    _serialize_ignore_fields = ['regiao']

    nome = Column(String(255))
    regiao_id = Column(Integer, ForeignKey('regiao.id'))
    regiao = relationship('Regiao', backref='bairros')

    def __repr__(self):
        regiao = self.regiao or u'(Sem região)'
        return u'{} - {}'.format(self.nome, regiao)


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


class Poste(db.Model, JSONSerializationMixin):
    _serialize_ignore_fields = ['logradouro', 'itens_manutencao']

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

    def __init__(self, poste, *args, **kwargs):
        super(Protocolo, self).__init__(*args, **kwargs)
        item_manutencao = None
        for _item_manutencao in poste.itens_manutencao:
            if _item_manutencao.aberto:
                item_manutencao = _item_manutencao
                break
        if not item_manutencao:
            item_manutencao = ItemManutencao(poste=poste)
            db.session.add(item_manutencao)
        item_manutencao.protocolos.append(self)


class Servico(db.Model):
    # Association
    id = Column(Integer, primary_key=True)

    ordem_servico_id = Column(Integer, ForeignKey('ordem_servico.id'))
    item_manutencao_id = Column(Integer, ForeignKey('item_manutencao.id'))

    feito = Column(Boolean, default=None)
    obs_urbam = Column(Text)
    obs_secretaria = Column(Text)

    criacao = Column(DateTime, default=datetime.now)
    resolucao = Column(DateTime)

    material = relationship('Material', backref='servico')

    confirmado = Column(Boolean, default=False)

    @property
    def custo(self):
        return sum(material.custo for material in self.material)

    @validates('confirmado')
    def validate_confirmado(self, key, confirmado):
        if not confirmado:
            return confirmado
        if self.feito:
            self.item_manutencao.status = 'fechado'
        else:
            self.item_manutencao.status = 'aberto'
        return confirmado


class ItemManutencao(db.Model):
    # Parent
    id = Column(Integer, primary_key=True)
    criacao = Column(DateTime, default=datetime.now)

    poste_id = Column(Integer, ForeignKey('poste.id'))
    poste = relationship('Poste', backref='itens_manutencao')

    status = Column(String(255), default='aberto')

    servicos = relationship('Servico', backref='item_manutencao')

    status_map = {
        'aberto': u'Aberto',
        'em_servico': u'Em serviço',
        'fechado': u'Fechado',
    }

    def __repr__(self):
        return u'{} - {}'.format(self.poste, self.status_map[self.status])

    @hybrid_property
    def aberto(self):
        return self.status == 'aberto'

    @hybrid_property
    def em_servico(self):
        return self.status == 'em_servico'

    @hybrid_property
    def fechado(self):
        return self.status == 'fechado'


class OrdemServico(db.Model):
    # Child
    id = Column(Integer, primary_key=True)
    criacao = Column(DateTime, default=datetime.now)
    status = Column(String(255), default='nova')

    status_map = {
        'nova': u'Nova',
        'em_servico': u'Em serviço',
        'feita': u'Feita',
        'confirmada': u'Confirmada',
    }

    @hybrid_property
    def nova(self):
        return self.status == 'nova'

    @hybrid_property
    def em_servico(self):
        return self.status == 'em_servico'

    @hybrid_property
    def feita(self):
        return self.status == 'feita'

    @hybrid_property
    def confirmada(self):
        return self.status == 'confirmada'

    servicos = relationship('Servico', backref='ordem_servico', order_by='Servico.id')

    @property
    def custo(self):
        return sum(servico.custo for servico in self.servicos)


class Equipamento(db.Model):
    id = Column(Integer, primary_key=True)
    nome = Column(String(255))
    abreviacao = Column(String(255))
    ativo = Column(Boolean, default=True)

    precos = relationship('PrecoEquipamento', backref='equipamento',
                          order_by='PrecoEquipamento.inicio_vigencia.desc()')

    @property
    def preco_atual(self):
        return self.preco_periodo(datetime.today())

    def preco_periodo(self, periodo):
        precos_vigentes = PrecoEquipamento.query.filter_by(equipamento=self) \
            .filter(PrecoEquipamento.inicio_vigencia < periodo) \
            .order_by(PrecoEquipamento.inicio_vigencia.desc()).all()
        return precos_vigentes[0]

    materiais = relationship('Material', backref='equipamento')

    def __str__(self):
        return self.nome


class Material(db.Model):
    id = Column(Integer, primary_key=True)

    quantidade = Column(Integer)

    servico_id = Column(Integer, ForeignKey('servico.id'))
    equipamento_id = Column(Integer, ForeignKey('equipamento.id'))

    em_garantia = Column(Boolean, default=False)

    @property
    def custo(self):
        if self.em_garantia:
            return 0
        resolucao = self.servico.resolucao
        return self.quantidade * self.equipamento.preco_periodo(resolucao).preco


class PrecoEquipamento(db.Model):
    id = Column(Integer, primary_key=True)
    preco = Column(Numeric(scale=2), default=0)
    garantia = Column(Integer, default=30)
    inicio_vigencia = Column(Date, default=date.today)

    equipamento_id = Column(Integer, ForeignKey('equipamento.id'))

    def __repr__(self):
        return u'{} - {} - {}'.format(self.equipamento.abreviacao, self.inicio_vigencia, self.preco)


def init_app(app):
    pass
