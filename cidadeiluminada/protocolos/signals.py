# coding: UTF-8
from __future__ import absolute_import

from cidadeiluminada.pusher import emit


def atualiza_protocolo(protocolo, data):
    """
    Adiciona o id do protocolo e faz o emit do evento 'atualiza-protocolo'.
    """
    data['protocolo_id'] = protocolo.id
    emit('atualiza-protocolo', data)


def novo_protocolo(protocolo):
    emit('novo-protocolo', protocolo)
