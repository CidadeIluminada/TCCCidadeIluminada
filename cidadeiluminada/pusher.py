# coding: UTF-8
from __future__ import absolute_import

from flask import current_app
from flask.ext.pusher import Pusher
from flask.ext.login import current_user


def emit(event, data, channel='cidadeiluminada'):
    pusher = current_app.extensions["pusher"]
    try:
        pusher.trigger(channel, event, data)
    except:
        current_app.logger \
            .exception(u"Falha no envio de mensagem para o Pusher. {}-{}-{}"
                       .format(channel, event, data))


def init_app(app):
    pusher = Pusher(app)

    @pusher.auth
    def pusher_auth(channel_name, socket_id):
        return current_user.is_authenticated()

    @app.context_processor
    def pusher_token():
        return {
            "pusher_token": current_app.config["PUSHER_KEY"]
        }
