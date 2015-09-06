# coding: UTF-8
from __future__ import absolute_import

from datetime import datetime

from flask.json import JSONEncoder
from flask.ext.migrate import Migrate
from flask.ext.sqlalchemy import SQLAlchemy

from cidadeiluminada import pusher

db = SQLAlchemy()


class JSONSerializationMixin(object):

    ignored_fields = []

    serialize_property = []

    @classmethod
    def deserialize(cls, data):
        return cls(**data)

    def serialize(self):
        _d = {k: v.value for k, v in
              dict(self._sa_instance_state.attrs).items()
              if not k.startswith('_') and k not in self.ignored_fields}
        _update = {_property: getattr(self, _property) for _property
                   in self.serialize_property}
        _d.update(_update)
        return _d


class AppJSONEncoder(JSONEncoder):

    def default(self, o):
        if isinstance(o, JSONSerializationMixin):
            return o.serialize()
        if isinstance(o, datetime):
            return o.strftime('%Y-%m-%dT%H:%M:%SZ')
        return super(AppJSONEncoder, self).default(o)


def init_app(app):
    db.init_app(app)
    Migrate(app, db)
    pusher.init_app(app)
