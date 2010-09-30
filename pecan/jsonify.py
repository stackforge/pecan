try:
    from json import JSONEncoder, dumps
except ImportError:
    from simplejson import JSONEncoder, dumps

from datetime        import datetime, date
from decimal         import Decimal
from webob.multidict import MultiDict
from simplegeneric   import generic


#
# exceptions
#

class JsonEncodeError(Exception):
    pass


#
# encoders
#

class BaseEncoder(JSONEncoder):
    def is_saobject(self, obj):
        return hasattr(obj, '_sa_class_manager')
    
    def jsonify(self, obj):
        return dumps(self.encode(obj))
    
    def encode(self, obj):
        if hasattr(obj, '__json__') and callable(obj.__json__):
            return obj.__json__()
        elif isinstance(obj, (date, datetime)):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif self.is_saobject(obj):
            props = {}
            for key in obj.__dict__:
                if not key.startswith('_sa_'):
                    props[key] = getattr(obj, key)
            return props
        elif isinstance(obj, MultiDict):
            return obj.mixed()
        else:
            try:
                from sqlalchemy.engine.base import ResultProxy, RowProxy
                if isinstance(obj, ResultProxy):
                    return dict(rows=list(obj), count=obj.rowcount)
                elif isinstance(obj, RowProxy):
                    return dict(rows=dict(obj), count=1)
            except:
                pass
        return obj
        

# 
# generic function support
#

encoder = BaseEncoder()

@generic
def jsonify(obj):
    return encoder.encode(obj)

def encode(obj):
    return dumps(jsonify(obj))