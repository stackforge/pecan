import sys
from inspect import getmembers

from webob.exc import HTTPFound

from .util import iscontroller, _cfg
from .routing import lookup_controller

__all__ = [
    'PecanHook', 'TransactionHook', 'HookController',
    'RequestViewerHook'
]


def walk_controller(root_class, controller, hooks):
    if not isinstance(controller, (int, dict)):
        for name, value in getmembers(controller):
            if name == 'controller':
                continue
            if name.startswith('__') and name.endswith('__'):
                continue

            if iscontroller(value):
                for hook in hooks:
                    value._pecan.setdefault('hooks', []).append(hook)
            elif hasattr(value, '__class__'):
                if name.startswith('__') and name.endswith('__'):
                    continue
                walk_controller(root_class, value, hooks)


class HookControllerMeta(type):
    '''
    A base class for controllers that would like to specify hooks on
    their controller methods. Simply create a list of hook objects
    called ``__hooks__`` as a member of the controller's namespace.
    '''

    def __init__(cls, name, bases, dict_):
        walk_controller(cls, cls, dict_.get('__hooks__', []))


HookController = HookControllerMeta(
    'HookController',
    (object,),
    {'__doc__': ("A base class for controllers that would like to specify "
                 "hooks on their controller methods. Simply create a list "
                 "of hook objects called ``__hooks__`` as a class attribute "
                 "of your controller.")}
)


class PecanHook(object):
    '''
    A base class for Pecan hooks. Inherit from this class to create your
    own hooks. Set a priority on a hook by setting the ``priority``
    attribute for the hook, which defaults to 100.
    '''

    priority = 100

    def on_route(self, state):
        '''
        Override this method to create a hook that gets called upon
        the start of routing.

        :param state: The Pecan ``state`` object for the current request.
        '''
        return

    def before(self, state):
        '''
        Override this method to create a hook that gets called after
        routing, but before the request gets passed to your controller.

        :param state: The Pecan ``state`` object for the current request.
        '''
        return

    def after(self, state):
        '''
        Override this method to create a hook that gets called after
        the request has been handled by the controller.

        :param state: The Pecan ``state`` object for the current request.
        '''
        return

    def on_error(self, state, e):
        '''
        Override this method to create a hook that gets called upon
        an exception being raised in your controller.

        :param state: The Pecan ``state`` object for the current request.
        :param e: The ``Exception`` object that was raised.
        '''
        return


class TransactionHook(PecanHook):
    '''
    :param start: A callable that will bind to a writable database and
                  start a transaction.
    :param start_ro: A callable that will bind to a readable database.
    :param commit: A callable that will commit the active transaction.
    :param rollback: A callable that will roll back the active
                     transaction.
    :param clear: A callable that will clear your current context.

    A basic framework hook for supporting wrapping requests in
    transactions. By default, it will wrap all but ``GET`` and ``HEAD``
    requests in a transaction. Override the ``is_transactional`` method
    to define your own rules for what requests should be transactional.
    '''

    def __init__(self, start, start_ro, commit, rollback, clear):

        self.start = start
        self.start_ro = start_ro
        self.commit = commit
        self.rollback = rollback
        self.clear = clear

    def is_transactional(self, state):
        '''
        Decide if a request should be wrapped in a transaction, based
        upon the state of the request. By default, wraps all but ``GET``
        and ``HEAD`` requests in a transaction, along with respecting
        the ``transactional`` decorator from :mod:pecan.decorators.

        :param state: The Pecan state object for the current request.
        '''

        controller = getattr(state, 'controller', None)
        if controller:
            force_transactional = _cfg(controller).get('transactional', False)
        else:
            force_transactional = False

        if state.request.method not in ('GET', 'HEAD') or force_transactional:
            return True
        return False

    def on_route(self, state):
        state.request.error = False
        if self.is_transactional(state):
            state.request.transactional = True
            self.start()
        else:
            state.request.transactional = False
            self.start_ro()

    def before(self, state):
        if self.is_transactional(state) \
                and not getattr(state.request, 'transactional', False):
            self.clear()
            state.request.transactional = True
            self.start()

    def on_error(self, state, e):
        #
        # If we should ignore redirects,
        # (e.g., shouldn't consider them rollback-worthy)
        # don't set `state.request.error = True`.
        #
        trans_ignore_redirects = (
            state.request.method not in ('GET', 'HEAD')
        )
        if state.controller is not None:
            trans_ignore_redirects = (
                _cfg(state.controller).get(
                    'transactional_ignore_redirects',
                    trans_ignore_redirects
                )
            )
        if type(e) is HTTPFound and trans_ignore_redirects is True:
            return
        state.request.error = True

    def after(self, state):
        if getattr(state.request, 'transactional', False):
            action_name = None
            if state.request.error:
                action_name = 'after_rollback'
                self.rollback()
            else:
                action_name = 'after_commit'
                self.commit()

            #
            # If a controller was routed to, find any
            # after_* actions it may have registered, and perform
            # them.
            #
            if action_name:
                controller = getattr(state, 'controller', None)
                if controller is not None:
                    actions = _cfg(controller).get(action_name, [])
                    for action in actions:
                        action()

        self.clear()


class RequestViewerHook(PecanHook):
    '''
    :param config:   A (optional) dictionary that can hold ``items`` and/or
                     ``blacklist`` keys.
    :param writer:   The stream writer to use. Can redirect output to other
                     streams as long as the passed in stream has a
                     ``write`` callable method.
    :param terminal: Outputs to the chosen stream writer (usually
                     the terminal)
    :param headers:  Sets values to the X-HTTP headers

    Returns some information about what is going on in a single request.  It
    accepts specific items to report on but uses a default list of items when
    none are passed in.  Based on the requested ``url``, items can also be
    blacklisted.
    Configuration is flexible, can be passed in (or not) and can contain
    some or all the keys supported.

    **items**

    This key holds the items that this hook will display. When this key is
    passed only the items in the list will be used.  Valid items are *any*
    item that the ``request`` object holds, by default it uses the
    following:

    * path
    * status
    * method
    * controller
    * params
    * hooks

    .. note::
        This key should always use a ``list`` of items to use.

    **blacklist**

    This key holds items that will be blacklisted based on ``url``. If
    there is a need to omit urls that start with `/javascript`, then this
    key would look like::

        'blacklist': ['/javascript']

    As many blacklisting items as needed can be contained in the list. The hook
    will verify that the url is not starting with items in this list to display
    results, otherwise it will get omitted.

    .. note::
        This key should always use a ``list`` of items to use.

    For more detailed documentation about this hook, please see
    :ref:`requestviewerhook`
    '''

    available = ['path', 'status', 'method', 'controller', 'params', 'hooks']

    def __init__(self, config=None, writer=sys.stdout, terminal=True,
                 headers=True):

        if not config:
            self.config = {'items': self.available}
        else:
            if config.__class__.__name__ == 'Config':
                self.config = config.to_dict()
            else:
                self.config = config
        self.writer = writer
        self.items = self.config.get('items', self.available)
        self.blacklist = self.config.get('blacklist', [])
        self.terminal = terminal
        self.headers = headers

    def after(self, state):

        # Default and/or custom response information
        responses = {
            'controller': lambda self, state: self.get_controller(state),
            'method': lambda self, state: state.request.method,
            'path': lambda self, state: state.request.path,
            'params': lambda self, state: [
                (p[0].encode('utf-8'), p[1].encode('utf-8'))
                for p in state.request.params.items()
            ],
            'status': lambda self, state: state.response.status,
            'hooks': lambda self, state: self.format_hooks(state.app.hooks),
        }

        is_available = [
            i for i in self.items
            if i in self.available or hasattr(state.request, i)
        ]

        terminal = []
        headers = []
        will_skip = [
            i for i in self.blacklist
            if state.request.path.startswith(i)
        ]

        if will_skip:
            return

        for request_info in is_available:
            try:
                value = responses.get(request_info)
                if not value:
                    value = getattr(state.request, request_info)
                else:
                    value = value(self, state)
            except Exception as e:
                value = e

            terminal.append('%-12s - %s\n' % (request_info, value))
            headers.append((request_info, value))

        if self.terminal:
            self.writer.write(''.join(terminal))
            self.writer.write('\n\n')

        if self.headers:
            for h in headers:
                key = str(h[0])
                value = str(h[1])
                name = 'X-Pecan-%s' % key
                state.response.headers[name] = value

    def get_controller(self, state):
        '''
        Retrieves the actual controller name from the application
        Specific to Pecan (not available in the request object)
        '''
        path = state.request.pecan['routing_path'].split('/')[1:]
        controller, reminder = lookup_controller(state.app.root, path)
        return controller.__str__().split()[2]

    def format_hooks(self, hooks):
        '''
        Tries to format the hook objects to be more readable
        Specific to Pecan (not available in the request object)
        '''
        str_hooks = [str(i).split()[0].strip('<') for i in hooks]
        return [i.split('.')[-1] for i in str_hooks if '.' in i]
