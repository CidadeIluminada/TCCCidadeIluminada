# coding: UTF-8
from __future__ import absolute_import

from flask.ext.babelex import format_datetime, format_date


def datetime_format(value):
    return format_datetime(value)


def date_format(value):
    return format_date(value)
