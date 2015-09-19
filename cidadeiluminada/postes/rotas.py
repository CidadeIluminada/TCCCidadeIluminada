# coding: UTF-8
from __future__ import absolute_import

from flask import Blueprint, render_template

bp = Blueprint('postes', __name__, template_folder='templates',
               static_folder='static')


def init_app(app, url_prefix='/postes'):
    app.register_blueprint(bp, url_prefix=url_prefix)


@bp.route('/')
def index():
    return render_template('index_poste.html')
