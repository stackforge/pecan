try:
    from simplejson import JSONEncoder
except ImportError:                     # pragma: no cover
    from json import JSONEncoder        # noqa

from datetime import datetime, date
from decimal import Decimal

# depending on the version WebOb might have 2 types of dicts
try:
    # WebOb <= 1.1.1
    from webob.multidict import MultiDict, UnicodeMultiDict
    webob_dicts = (MultiDict, UnicodeMultiDict)  # pragma: no cover
except ImportError:  # pragma no cover
    # WebOb >= 1.2
    from webob.multidict import MultiDict
    webob_dicts = (MultiDict,)

import six
try:
    from functools import singledispatch
except ImportError:  # pragma: no cover
    from singledispatch import singledispatch

try:
    from sqlalchemy.engine.result import ResultProxy, RowProxy
except ImportError:  # pragma no cover
    try:
        from sqlalchemy.engine.base import ResultProxy, RowProxy
    except ImportError:  # pragma no cover
        # dummy classes since we don't have SQLAlchemy installed

        class ResultProxy(object):  # noqa
            pass

        class RowProxy(object):  # noqa
            pass


#
# encoders
#

def is_saobject(obj):
    return hasattr(obj, '_sa_class_manager')


class GenericJSON(JSONEncoder):
    '''
    Generic JSON encoder.  Makes several attempts to correctly JSONify
    requested response objects.
    '''
    def default(self, obj):
        '''
        Converts an object and returns a ``JSON``-friendly structure.

        :param obj: object or structure to be converted into a
                    ``JSON``-ifiable structure

        Considers the following special cases in order:

        * object has a callable __json__() attribute defined
            returns the result of the call to __json__()
        * date and datetime objects
            returns the object cast to str
        * Decimal objects
            returns the object cast to float
        * SQLAlchemy objects
            returns a copy of the object.__dict__ with internal SQLAlchemy
            parameters removed
        * SQLAlchemy ResultProxy objects
            Casts the iterable ResultProxy into a list of tuples containing
            the entire resultset data, returns the list in a dictionary
            along with the resultset "row" count.

            .. note:: {'count': 5, 'rows': [('Ed Jones',), ('Pete Jones',),
                ('Wendy Williams',), ('Mary Contrary',), ('Fred Smith',)]}

        * SQLAlchemy RowProxy objects
            Casts the RowProxy cursor object into a dictionary, probably
            losing its ordered dictionary behavior in the process but
            making it JSON-friendly.
        * webob_dicts objects
            returns webob_dicts.mixed() dictionary, which is guaranteed
            to be JSON-friendly.
        '''
        if hasattr(obj, '__json__') and six.callable(obj.__json__):
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


def with_when_type(f):
    # Add some backwards support for simplegeneric's API
    f.when_type = f.register
    return f


@with_when_type
@singledispatch
def jsonify(obj):
    return _default.default(obj)


class GenericFunctionJSON(GenericJSON):
    def default(self, obj):
        return jsonify(obj)

_instance = GenericFunctionJSON()


def encode(obj):
    return _instance.encode(obj)
