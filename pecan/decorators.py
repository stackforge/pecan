from inspect import getmembers, isclass, ismethod, isfunction

import six

from .util import _cfg, getargspec

__all__ = [
    'expose', 'transactional', 'accept_noncanonical', 'after_commit',
    'after_rollback'
]


def when_for(controller):
    def when(method=None, **kw):
        def decorate(f):
            expose(**kw)(f)
            _cfg(f)['generic_handler'] = True
            controller._pecan['generic_handlers'][method.upper()] = f
            controller._pecan['allowed_methods'].append(method.upper())
            return f
        return decorate
    return when


def expose(template=None,
           content_type='text/html',
           generic=False):

    '''
    Decorator used to flag controller methods as being "exposed" for
    access via HTTP, and to configure that access.

    :param template: The path to a template, relative to the base template
                     directory.
    :param content_type: The content-type to use for this template.
    :param generic: A boolean which flags this as a "generic" controller,
                    which uses generic functions based upon
                    ``functools.singledispatch`` generic functions.  Allows you
                    to split a single controller into multiple paths based upon
                    HTTP method.
    '''

    if template == 'json':
        content_type = 'application/json'

    def decorate(f):
        # flag the method as exposed
        f.exposed = True

        # set a "pecan" attribute, where we will store details
        cfg = _cfg(f)
        cfg['content_type'] = content_type
        cfg.setdefault('template', []).append(template)
        cfg.setdefault('content_types', {})[content_type] = template

        # handle generic controllers
        if generic:
            cfg['generic'] = True
            cfg['generic_handlers'] = dict(DEFAULT=f)
            cfg['allowed_methods'] = []
            f.when = when_for(f)

        # store the arguments for this controller method
        cfg['argspec'] = getargspec(f)

        return f

    return decorate


def transactional(ignore_redirects=True):
    '''
    If utilizing the :mod:`pecan.hooks` ``TransactionHook``, allows you
    to flag a controller method or class as being wrapped in a transaction,
    regardless of HTTP method.

    :param ignore_redirects: Indicates if the hook should ignore redirects
                             for this controller or not.
    '''

    def deco(f):
        if isclass(f):
            for meth in [
                m[1] for m in getmembers(f)
                if (isfunction if six.PY3 else ismethod)(m[1])
            ]:
                if getattr(meth, 'exposed', False):
                    _cfg(meth)['transactional'] = True
                    _cfg(meth)['transactional_ignore_redirects'] = _cfg(
                        meth
                    ).get(
                        'transactional_ignore_redirects',
                        ignore_redirects
                    )
        else:
            _cfg(f)['transactional'] = True
            _cfg(f)['transactional_ignore_redirects'] = ignore_redirects
        return f
    return deco


def after_action(action_type, action):
    '''
    If utilizing the :mod:`pecan.hooks` ``TransactionHook``, allows you
    to flag a controller method to perform a callable action after the
    action_type is successfully issued.

    :param action: The callable to call after the commit is successfully
    issued.  '''

    if action_type not in ('commit', 'rollback'):
        raise Exception('action_type (%s) is not valid' % action_type)

    def deco(func):
        _cfg(func).setdefault('after_%s' % action_type, []).append(action)
        return func
    return deco


def after_commit(action):
    '''
    If utilizing the :mod:`pecan.hooks` ``TransactionHook``, allows you
    to flag a controller method to perform a callable action after the
    commit is successfully issued.

    :param action: The callable to call after the commit is successfully
                   issued.
    '''
    return after_action('commit', action)


def after_rollback(action):
    '''
    If utilizing the :mod:`pecan.hooks` ``TransactionHook``, allows you
    to flag a controller method to perform a callable action after the
    rollback is successfully issued.

    :param action: The callable to call after the rollback is successfully
                   issued.
    '''
    return after_action('rollback', action)


def accept_noncanonical(func):
    '''
    Flags a controller method as accepting non-canoncial URLs.
    '''

    _cfg(func)['accept_noncanonical'] = True
    return func
