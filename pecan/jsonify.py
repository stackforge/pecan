try:
    from simplejson import JSONEncoder
except ImportError:                     # pragma: no cover
    from json import JSONEncoder        # noqa

from datetime               import datetime, date
from decimal                import Decimal

# depending on the version WebOb might have 2 types of dicts
try:
    # WebOb <= 1.1.1
    from webob.multidict        import MultiDict, UnicodeMultiDict
    webob_dicts = (MultiDict, UnicodeMultiDict)
except ImportError:         # pragma no cover
    # WebOb >= 1.2
    from webob.multidict        import MultiDict
    webob_dicts = (MultiDict,)

from simplegeneric          import generic

try:
    from sqlalchemy.engine.base import ResultProxy, RowProxy
except ImportError:         # pragma no cover
    # dummy classes since we don't have SQLAlchemy installed
    class ResultProxy: pass # noqa
    class RowProxy: pass    # noqa

#
# exceptions
#


class JsonEncodeError(Exception):
    pass


#
# encoders
#

def is_saobject(obj):
    return hasattr(obj, '_sa_class_manager')


class GenericJSON(JSONEncoder):
    def default(self, obj):
        if hasattr(obj, '__json__') and callable(obj.__json__):
            return obj.__json__()
        elif isinstance(obj, (date, datetime)):
            return str(obj)
        elif isinstance(obj, Decimal):
              # XXX What to do about JSONEncoder crappy handling of Decimals?
              # SimpleJSON has better Decimal encoding than the std lib
              # but only in recent versions
            return float(obj)
        elif is_saobject(obj):
            props = {}
            for key in obj.__dict__:
                if not key.startswith('_sa_'):
                    props[key] = getattr(obj, key)
            return props
        elif isinstance(obj, ResultProxy):
            props = dict(rows=list(obj), count=obj.rowcount)
            if props['count'] < 0:
                props['count'] = len(props['rows'])
            return props
        elif isinstance(obj, RowProxy):
            return dict(obj)
        elif isinstance(obj, webob_dicts):
            return obj.mixed()
        else:
            return JSONEncoder.default(self, obj)


_default = GenericJSON()


@generic
def jsonify(obj):
    return _default.default(obj)


class GenericFunctionJSON(GenericJSON):
    def default(self, obj):
        return jsonify(obj)

_instance = GenericFunctionJSON()


def encode(obj):
    return _instance.encode(obj)
