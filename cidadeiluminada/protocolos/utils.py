# coding: UTF-8
from __future__ import absolute_import

from flask.ext.babelex import format_datetime


def datetime_format(value):
    return format_datetime(value)
