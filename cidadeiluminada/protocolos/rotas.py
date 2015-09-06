# coding: UTF-8
from __future__ import absolute_import
import os
from datetime import datetime

from flask import Blueprint, jsonify, request, current_app,\
    send_from_directory, render_template
from flask.ext.login import login_required
from werkzeug import secure_filename

from cidadeiluminada.base import db
from cidadeiluminada.services import postmon
from cidadeiluminada.protocolos import signals
from cidadeiluminada.protocolos.models import Protocolo
from cidadeiluminada.protocolos.forms import ProtocoloForm

bp = Blueprint('protocolos', __name__, template_folder='templates',
               static_folder='static')


def init_app(app, url_prefix='/protocolos'):
    app.register_blueprint(bp, url_prefix=url_prefix)


@bp.route('/')
@login_required
def index():
    return render_template('protocolos.html')


@bp.route('/protocolo.json')
def buscar_cod_protocolo():
    cod_protocolo = request.args['cod_protocolo']
    protocolo = Protocolo.query.filter_by(cod_protocolo=cod_protocolo).first()
    response = {
        'status': 'OK',
        'protocolo': protocolo
    }
    return jsonify(response), 200


@bp.route('/protocolos.json')
@login_required
def lista():
    protocolos_q = Protocolo.query
    cod_protocolo = request.args.get('cod_protocolo')
    if cod_protocolo:
        protocolos_q = protocolos_q.filter_by(cod_protocolo=cod_protocolo)
    protocolos = protocolos_q.order_by(Protocolo.id.desc()).all()
    response = {
        'status': 'OK',
        'protocolos': protocolos
    }
    return jsonify(response), 200


@bp.route('/novo/', methods=['POST'])
def novo():
    form = ProtocoloForm(csrf_enabled=False)
    if form.validate():
        cod_protocolo_recebido = form.cod_protocolo.data
        protocolo_existente = Protocolo.query \
            .filter_by(cod_protocolo=cod_protocolo_recebido).first()
        if protocolo_existente:
            return jsonify({
                'status': 'OK',
                'protocolo': protocolo_existente
            })
        arquivo = form.arquivo_protocolo.data
        filename = secure_filename(arquivo.filename)
        protocolo = Protocolo(cod_protocolo=cod_protocolo_recebido,
                              cep=form.cep.data,  email=form.email.data,
                              logradouro=form.logradouro.data,
                              cidade=form.cidade.data, bairro=form.bairro.data,
                              numero=form.numero.data, estado=form.estado.data,
                              nome=form.nome.data)
        if not protocolo.has_full_address():
            endereco = postmon.get_by_cep(protocolo.cep)
            protocolo.estado = endereco['estado']
            protocolo.cidade = endereco['cidade']
            protocolo.bairro = endereco['bairro']
            protocolo.logradouro = endereco['logradouro']
        db.session.add(protocolo)
        db.session.commit()
        agora = datetime.now().isoformat()
        filename_completo = "-".join([str(protocolo.id), agora, filename])
        arquivo.save(os.path.join(current_app.config['UPLOAD_FOLDER'],
                     filename_completo))
        protocolo.filename = filename_completo
        db.session.commit()
        signals.novo_protocolo(protocolo)
        protocolo_response = {
            'cod_protocolo': protocolo.cod_protocolo,
            'status': protocolo.status,
        }
        return jsonify({
            'status': 'OK',
            'protocolo': protocolo_response,
        }), 200
    else:
        return jsonify({
            'status': 'ERROR',
            'errors': form.errors,
        }), 400


@bp.route('/novo/form/')
@login_required
def novo_pagina():
    form = ProtocoloForm()
    return render_template('novo.html', form=form)


@bp.route('/<protocolo_id>/foto/')
@login_required
def foto(protocolo_id):
    protocolo = Protocolo.query.filter_by(id=protocolo_id).first_or_404()
    return send_from_directory(current_app.config['UPLOAD_FOLDER'],
                               protocolo.filename)


@bp.route('/<protocolo_id>/status/', methods=['POST'])
@login_required
def status(protocolo_id):
    protocolo = Protocolo.query.filter_by(id=protocolo_id).first_or_404()
    protocolo.status = request.json['status']
    db.session.commit()
    signals.atualiza_protocolo(protocolo, {
        'status': protocolo.status,
    })
    return jsonify({
        'status': 'OK',
        'protocolo': {
            'status': protocolo.status,
        }
    }), 200
