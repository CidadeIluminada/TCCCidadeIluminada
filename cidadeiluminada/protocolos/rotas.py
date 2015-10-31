# coding: UTF-8
from __future__ import absolute_import

import os
from datetime import datetime
from StringIO import StringIO
from tempfile import mkstemp

from flask import request, abort, redirect, url_for, jsonify, render_template, send_file, \
    current_app
from flask.ext.admin import Admin, expose, AdminIndexView
from flask.ext.admin.model import typefmt
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.contrib.sqla.fields import QuerySelectField
from flask.ext.admin.form.widgets import Select2Widget
from flask.ext.security import current_user, login_required
from flask.ext.babelex import format_datetime
from xhtml2pdf import pisa
from wtforms.validators import Required

from cidadeiluminada.models import User, Role
from cidadeiluminada.protocolos.models import Regiao, Bairro, Logradouro, \
    Poste, ItemManutencao, Protocolo, OrdemServico, ItemManutencaoOrdemServico
from cidadeiluminada.base import db


class IndexView(AdminIndexView):

    @expose('/', methods=['GET', 'POST'])
    @login_required
    def index(self):
        im_query = ItemManutencao.query.join(Poste).join(Logradouro).join(Bairro).join(Regiao) \
            .filter(ItemManutencao.status == 'aberto')  # NOQA
        regioes_select_map = {}
        regioes_qty_map = {}
        for regiao in db.session.query(Regiao.id, Regiao.nome):
            qty_im = im_query.filter(Regiao.id == regiao.id).count()
            regioes_select_map[regiao.id] = u'Região {}'.format(regiao.nome)
            regioes_qty_map[regiao.id] = qty_im
        return self.render('admin/index_postes.html', regioes_map=regioes_select_map,
                           regioes_qty=regioes_qty_map)


def _date_format(view, value):
    return format_datetime(value)

default_formatters = dict(typefmt.BASE_FORMATTERS, **{
    datetime: _date_format
})


class _ModelView(ModelView):

    category = None

    column_type_formatters = default_formatters

    def is_accessible(self):
        return current_user.is_authenticated()

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('name', self.name)
        kwargs.setdefault('category', self.category)
        super(_ModelView, self).__init__(self.model, db.session, *args, **kwargs)


class RegiaoView(_ModelView):
    model = Regiao
    name = u'Região'
    category = u'Endereço'

    form_excluded_columns = ('bairros', )

    @expose('/bairros')
    def get_bairros(self):
        regiao_id = request.args['regiao_id']
        regiao = self.model.query.get(regiao_id)
        im_query = ItemManutencao.query.join(Poste).join(Logradouro).join(Bairro) \
            .filter(ItemManutencao.status == 'aberto')
        bairros = []
        for bairro in regiao.bairros:
            qty_im = im_query.filter(Bairro.id == bairro.id).count()
            serialized = bairro.serialize()
            serialized['qty_im'] = qty_im
            bairros.append(serialized)
        return jsonify({
            'payload': bairros,
        })


class BairroView(_ModelView):
    model = Bairro
    name = 'Bairro'
    category = u'Endereço'

    form_excluded_columns = ('logradouros', )

    column_labels = {
        'regiao': u'Região',
    }

    @expose('/itens_manutencao')
    def get_itens_manutencao(self):
        bairro_id = request.args['bairro_id']
        im_query = ItemManutencao.query.join(Poste).join(Logradouro).join(Bairro) \
            .filter(ItemManutencao.status == 'aberto').filter(Bairro.id == bairro_id)
        postes = []
        for item_manutencao in im_query:
            poste = item_manutencao.poste
            serialized = poste.serialize()

            serialized['label'] = u'{} - {} - Nº {}'.format(poste.logradouro.cep,
                                                             poste.logradouro.logradouro,
                                                             poste.numero)
            postes.append(serialized)
        return jsonify({
            'payload': postes,
        })


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

    column_labels = {
        'cep': 'CEP',
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

    column_labels = {
        'numero': u'Número',
    }

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

    column_labels = {
        'criacao': u'Criação',
        'cod_protocolo': u'Código do protocolo',
        'nome_municipe': u'Nome do munícipe',
        'contato_municipe': u'Contato do munícipe',
    }

    form_extra_fields = {
        'poste': QuerySelectField(query_factory=lambda: Poste.query.all(), allow_blank=True,
                                  widget=Select2Widget(),
                                  validators=[Required(u'Campo obrigatório')])
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

    column_labels = {
        'criacao': u'Criação'
    }


class OrdemServicoView(_ModelView):
    def __init__(self, *args, **kwargs):
        super(OrdemServicoView, self).__init__(*args, **kwargs)
        self.itens_manutencao_adicionar = None

    def item_manutencao_query(self):
        return ItemManutencao.query.join(Poste).filter(ItemManutencao.status == 'aberto')  # NOQA

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

    column_labels = {
        'criacao': u'Criação',
    }

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
            print request.form
            postes_id = request.form.getlist('postes')
            if not postes_id:
                abort(400)
            query = self.item_manutencao_query().filter(Poste.id.in_(postes_id))
            count = query.count()
            print count
            if count <= 0 or count > 50:
                abort(400)
            self.itens_manutencao_adicionar = query.all()
        return super(OrdemServicoView, self).create_view()

    @expose('/edit/', methods=('GET', 'POST'))
    def edit_view(self):
        self._template_args['email_urbam'] = current_app.config.get('EMAIL_URBAM')
        return super(OrdemServicoView, self).edit_view()

    def _gerar_pdf(self, template):
        fd, temp_path = mkstemp()
        with open(temp_path, 'wb') as pdf_file:
            pisa.CreatePDF(StringIO(template), pdf_file)
        os.close(fd)
        return temp_path

    @expose('/enviar_pdf/<ordem_servico_id>', methods=['POST'])
    def enviar_pdf(self, ordem_servico_id):
        from cidadeiluminada.base import mail
        from flask import flash
        from flask.ext.mail import Message
        model = self.model.query.get(ordem_servico_id)
        recipients = [request.form['email_urbam']]
        recipients.extend(current_app.config.get('MAIL_DEFAULT_RECIPIENTS'))
        print recipients
        assunto = current_app.config.get('MAIL_DEFAULT_SUBJECT')
        email_template = render_template('email/ordem_servico.txt')
        email = Message(subject=assunto.format(ordem_servico_id=model.id), recipients=recipients,
                        body=email_template)
        mail.send(email)
        # pdf_template = render_template('pdf/ordem_servico.html', model=model)
        # pdf_path = self._gerar_pdf(pdf_template)
        flash('Email enviado.', 'success')
        return redirect(url_for('ordemservico.edit_view', id=model.id))


    @expose('/pdf/<ordem_servico_id>')
    def mostrar_pdf(self, ordem_servico_id):
        model = self.model.query.get(ordem_servico_id)
        template = render_template('pdf/ordem_servico.html', model=model)
        if not request.args.get('render_html'):
            pdf_path = self._gerar_pdf(template)
            return send_file(pdf_path,  as_attachment=True, mimetype='application/pdf',
                             attachment_filename=u'ordem serviço #{}.pdf'.format(model.id))
        else:
            return template


class UserView(_ModelView):
    model = User
    name = u'Usuários'
    category = u'Usuários'

    column_labels = {
        'password': u'Senha',
    }


class RoleView(_ModelView):
    model = Role
    name = u'Role'
    category = u'Usuários'

    column_labels = {
        'name': u'Nome',
        'description': u'Descrição'
    }

    form_excluded_columns = ['users']


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
        OrdemServicoView(),
        UserView(),
        RoleView(),
    ]
    index = IndexView(name='Principal', **config)
    admin = Admin(app, template_mode='bootstrap3', index_view=index, name='Protocolos',
                  **config)
    for view in views:
        admin.add_view(view)
