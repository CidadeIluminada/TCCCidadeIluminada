# coding: UTF-8
from __future__ import absolute_import

from flask import request, jsonify
from flask.ext.admin import Admin, expose, AdminIndexView
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.contrib.sqla.fields import QuerySelectField
from flask.ext.admin.form.widgets import Select2Widget

from cidadeiluminada.protocolos.models import Regiao, Bairro, Logradouro, \
    Poste, ItemManutencao, Protocolo, OrdemServico, ItemManutencaoOrdemServico
from cidadeiluminada.base import db

_endereco_widget_args = {
    'estado': {
        'readonly': True,
    },
    'cidade': {
        'readonly': True,
    }
}

_endereco_args = {
    'estado': {
        'default': u'SP',
    },
    'cidade': {
        'default': u'São José dos Campos',
    }
}


class IndexView(AdminIndexView):

    @expose('/')
    def index(self):
        # return super(IndexView, self).index()
        # pendencias_acao = Pendencia.query.filter(Pendencia.poste == None)
        # return self.render('admin/index_postes.html', pendencias_acao=pendencias_acao)
        return self.render('admin/index_postes.html', pendencias_acao=[])

    # @expose('/ordem_servico/nova/')
    # def ordem_servico(self):
    #     regioes = Regiao.query.all()
    #     return self.render('admin/index_postes.html', regioes=regioes)


class _ModelView(ModelView):

    category = None

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('name', self.name)
        kwargs.setdefault('category', self.category)
        super(_ModelView, self).__init__(self.model, db.session, *args, **kwargs)


class RegiaoView(_ModelView):
    model = Regiao
    name = u'Região'
    category = u'Endereço'


class BairroView(_ModelView):
    model = Bairro
    name = 'Bairro'
    category = u'Endereço'

    form_columns = ('regiao', 'nome')


class LogradouroView(_ModelView):
    model = Logradouro
    name = 'Logradouro'
    category = u'Endereço'

    create_template = 'admin/model/edit_modelo_cep.html'
    edit_template = 'admin/model/edit_modelo_cep.html'

    form_columns = ('bairro', 'logradouro', 'cep')

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
        self._template_args['list_columns'] = self.item_manutencao_view.get_list_columns()
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

    form_extra_fields = {
        'poste': QuerySelectField(query_factory=lambda: Poste.query.all(), allow_blank=True,
                                  widget=Select2Widget())
    }

    @expose('/new/', methods=('GET', 'POST'))
    def create_view(self):
        print request.form
        return super(ProtocoloView, self).create_view()

    @expose('/edit/', methods=('GET', 'POST'))
    def edit_view(self):
        print request.form
        return super(ProtocoloView, self).edit_view()


class ItemManutencaoView(_ModelView):
    model = ItemManutencao
    name = u'Itens Manutenção'
    category = 'Protocolos'

    column_exclude_list = ('poste', )


class OrdemServicoView(_ModelView):
    model = OrdemServico
    name = u'Ordem de Serviço'
    category = 'Protocolos'

    form_excluded_columns = ('protocolos')

    edit_template = 'admin/model/edit_os.html'

    form_widget_args = {
        'criacao': {
            'readonly': True,
            'disabled': True,
        },
    }

# class PendenciaView(_ModelView):
#     model = Pendencia
#     name = 'Protocolos'
#     category = 'Protocolos'

#     can_edit = True
#     can_delete = True
#     can_create = False

#     named_filter_urls = True
#     column_filters = ('ordens_servico', 'ordens_servico.id')

#     form_args = _endereco_args
#     form_widget_args = dict(_endereco_widget_args, **{
#         'bairro': {
#             'readonly': True,
#             'disabled': True,
#         },
#         'criacao': {
#             'readonly': True,
#             'disabled': True,
#         },
#         'cep': {
#             'readonly': True,
#         },
#         'logradouro': {
#             'readonly': True,
#         },
#         'numero': {
#             'readonly': True,
#         }
#     })

#     def on_model_change(self, form, model, is_created):
#         if not is_created:
#             return
#         model.preencher_endereco()
#         model.descobrir_poste()
#         duplicidade = model.verificar_duplicidade()
#         if duplicidade:
#             raise ValueError(u'Em duplicidade')
#         pass

#     @expose('/nova_pendencia/', methods=['POST'])
#     def nova_pendencia(self):
#         form = self.create_form(request.form)
#         if form.validate():
#             try:
#                 pendencia = self.create_model(form)
#             except ValueError as ex:
#                 return jsonify(payload={'status': 'ERRO', 'erros': [ex.message]}), 400
#             return jsonify(payload={'pendencia_id': pendencia.id, 'status': 'OK'}), 200
#         return jsonify(payload={'status': 'ERRO', 'erros': form.errors}), 400


def init_app(app):
    config = {
        'endpoint': 'protocolos',
        'url': '/',
    }
    views = [
        RegiaoView(),
        BairroView(),
        LogradouroView(),
        PosteView(ItemManutencaoView()),
        ItemManutencaoView(),
        ProtocoloView(),
        OrdemServicoView(),
    ]
    index = IndexView(name='Principal', **config)
    admin = Admin(app, template_mode='bootstrap3', index_view=index, name='Protocolos',
                  **config)
    for view in views:
        admin.add_view(view)
