# coding: UTF-8
from __future__ import absolute_import

from flask import current_app

import requests


def get_by_cep(cep):
    url = current_app.config['POSTMON_URL']
    response = requests.get(url + cep)
    return response.json()
