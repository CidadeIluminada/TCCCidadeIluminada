# coding: UTF-8
from __future__ import absolute_import
from datetime import datetime, date

from flask import request, abort, redirect, url_for
from flask.ext.admin import Admin, expose, AdminIndexView
from flask.ext.admin.model import typefmt
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.contrib.sqla.fields import QuerySelectField
from flask.ext.admin.form.widgets import Select2Widget
from flask.ext.babelex import format_datetime

from wtforms.validators import Required

from cidadeiluminada.protocolos.models import Regiao, Bairro, Logradouro, \
    Poste, ItemManutencao, Protocolo, OrdemServico, ItemManutencaoOrdemServico
from cidadeiluminada.base import db


class IndexView(AdminIndexView):

    @expose('/', methods=['GET', 'POST'])
    def index(self):
        im_query = ItemManutencao.query.join(Poste).join(Logradouro).join(Bairro).join(Regiao) \
            .filter(ItemManutencao.status == 'aberto')  # NOQA
        regioes_select_map = {}
        regioes_qty_map = {}
        for regiao in db.session.query(Regiao.id, Regiao.nome):
            qty_im = im_query.filter(Regiao.id == regiao.id).count()
            regioes_select_map[regiao.id] = u'Região {} - {} items em aberto'.format(regiao.nome,
                                                                                      qty_im)
            regioes_qty_map[regiao.id] = qty_im
        return self.render('admin/index_postes.html', regioes_map=regioes_select_map,
                           regioes_qty=regioes_qty_map)


def _date_format(view, value):
    return format_datetime(value)

default_formatters = dict(typefmt.BASE_FORMATTERS, **{
    date: _date_format,
    datetime: _date_format
})


class _ModelView(ModelView):

    category = None

    column_type_formatters = default_formatters

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('name', self.name)
        kwargs.setdefault('category', self.category)
        super(_ModelView, self).__init__(self.model, db.session, *args, **kwargs)


class RegiaoView(_ModelView):
    model = Regiao
    name = u'Região'
    category = u'Endereço'

    form_excluded_columns = ('bairros', )


class BairroView(_ModelView):
    model = Bairro
    name = 'Bairro'
    category = u'Endereço'

    form_excluded_columns = ('logradouros', )


class LogradouroView(_ModelView):
    model = Logradouro
    name = 'Logradouro'
    category = u'Endereço'

    create_template = 'admin/model/edit_modelo_cep.html'
    edit_template = 'admin/model/edit_modelo_cep.html'

    form_columns = ('cep', 'bairro', 'logradouro')

    form_widget_args = {
        'logradouro': {
            'readonly': True,
        },
    }

    def _inject_bairros(self):
        bairros = Bairro.query
        bairro_id_nome = {bairro.nome: bairro.id for bairro in bairros}
        self._template_args['bairro_id_nome_map'] = bairro_id_nome

    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        self._inject_bairros()
        return super(LogradouroView, self).create_view()

    @expose('/edit/', methods=('GET', 'POST'))
    def edit_view(self):
        self._inject_bairros()
        return super(LogradouroView, self).edit_view()


class PosteView(_ModelView):
    def __init__(self, item_manutencao_view, *args, **kwargs):
        super(PosteView, self).__init__(*args, **kwargs)
        self.item_manutencao_view = item_manutencao_view

    model = Poste
    name = 'Postes'
    category = 'Protocolos'

    form_columns = ('logradouro', 'numero')

    edit_template = 'admin/model/edit_poste.html'

    @expose('/edit/', methods=('GET', 'POST'))
    def edit_view(self):
        cols = self.item_manutencao_view.get_list_columns()
        cols.remove(('poste', 'Poste'))
        self._template_args['list_columns'] = cols
        self._template_args['get_item_manutencao_value'] = self.item_manutencao_view.get_list_value
        return super(PosteView, self).edit_view()


class ProtocoloView(_ModelView):
    model = Protocolo
    name = 'Protocolos 156'
    category = 'Protocolos'

    column_exclude_list = ('item_manutencao', )
    column_filters = ('item_manutencao.id', )

    named_filter_urls = True

    can_delete = False

    form_excluded_columns = ('item_manutencao', )
    edit_template = 'admin/model/edit_protocolo.html'

    form_extra_fields = {
        'poste': QuerySelectField(query_factory=lambda: Poste.query.all(), allow_blank=True,
                                  widget=Select2Widget(), validators=[Required(u'Campo obrigatório')])
    }

    def on_model_change(self, form, protocolo, is_created):
        if is_created:
            poste = form.poste.data
            item_manutencao = None
            for _item_manutencao in poste.itens_manutencao:
                if _item_manutencao.aberto:
                    item_manutencao = _item_manutencao
                    break
            if not item_manutencao:
                item_manutencao = ItemManutencao(poste=poste)
                db.session.add(item_manutencao)
            item_manutencao.protocolos.append(protocolo)
            db.session.commit()

    @expose('/edit/', methods=('GET', 'POST'))
    def edit_view(self):
        protocolo_id = request.args['id']
        protocolo = Protocolo.query.get(protocolo_id)
        poste_id = protocolo.item_manutencao.poste_id
        self._template_args['poste_id'] = poste_id
        return super(ProtocoloView, self).edit_view()


class ItemManutencaoView(_ModelView):
    model = ItemManutencao
    name = u'Itens Manutenção'
    category = 'Protocolos'


class OrdemServicoView(_ModelView):
    def __init__(self, item_manutencao_view, *args, **kwargs):
        super(OrdemServicoView, self).__init__(*args, **kwargs)
        self.item_manutencao_view = item_manutencao_view
        self.itens_manutencao_adicionar = None

    def item_manutencao_query(self):
        return ItemManutencao.query.join(Poste).join(Logradouro).join(Bairro).join(Regiao) \
            .filter(ItemManutencao.status == 'aberto')  # NOQA

    model = OrdemServico
    name = u'Ordem de Serviço'
    category = 'Protocolos'

    form_widget_args = {
        'criacao': {
            'readonly': True,
            'disabled': True,
        },
    }

    edit_template = 'admin/model/edit_os.html'

    form_excluded_columns = ('itens_manutencao', )

    def on_model_change(self, form, ordem_servico, is_created):
        if is_created:
            itens_manutencao = self.itens_manutencao_adicionar
            self.itens_manutencao_adicionar = None
            for item_manutencao in itens_manutencao:
                item_manutencao.status = 'em_servico'
                assoc = ItemManutencaoOrdemServico()
                assoc.ordem_servico = ordem_servico
                assoc.item_manutencao = item_manutencao
                db.session.add(assoc)
            db.session.commit()

    @expose('/atualizar_item_manutencao/', methods=['POST'])
    def atualizar_item_manutencao(self):
        feito = request.form['feito']
        if feito == 'false':
            feito = False
        elif feito == 'true':
            feito = True
        ordem_servico_id = request.form['ordem_servico_id']
        item_manutencao_ordem_servico_id = request.form['item_manutencao_ordem_servico_id']
        item = ItemManutencaoOrdemServico.query.get(item_manutencao_ordem_servico_id)
        item.servico_feito = feito
        db.session.commit()
        return redirect(url_for('.edit_view', id=ordem_servico_id))

    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        if request.method == 'POST':
            regioes_id = request.form.getlist('regiao')
            query = self.item_manutencao_query().filter(Regiao.id.in_(regioes_id))
            count = query.count()
            if count <= 0 or count > 50:
                abort(400)
            self.itens_manutencao_adicionar = query.all()
        return super(OrdemServicoView, self).create_view()


def init_app(app):
    config = {
        'endpoint': 'admin_protocolos',
        'url': '/',
    }
    imv = ItemManutencaoView()
    views = [
        RegiaoView(),
        BairroView(),
        LogradouroView(),
        PosteView(imv),
        imv,
        ProtocoloView(),
        OrdemServicoView(imv),
    ]
    index = IndexView(name='Principal', **config)
    admin = Admin(app, template_mode='bootstrap3', index_view=index, name='Protocolos',
                  **config)
    for view in views:
        admin.add_view(view)
