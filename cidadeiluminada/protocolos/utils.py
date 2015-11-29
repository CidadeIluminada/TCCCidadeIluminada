# coding: UTF-8
from __future__ import absolute_import

from flask.ext.babelex import format_datetime, format_date, format_currency


def datetime_format(value):
    return format_datetime(value)


def date_format(value):
    return format_date(value)


def currency_format(value):
    return format_currency(value, 'R$')
