import inspect

import six


def is_bound_method(ob):
    return inspect.ismethod(ob) and six.get_method_self(ob) is not None
