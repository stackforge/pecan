.. _jsonify:


JSON Support
============
Pecan includes a simple, easy-to-use system for generating and serving
``JSON``. To get started, create a file in your project called
``json.py`` which should be imported in your ``app.py``.

Your ``json`` module will contain a series of rules for generating
``JSON`` from objects you return in your controller, utilizing
"generic" function support from the 
`simplegeneric <http://pypi.python.org/pypi/simplegeneric>`_ library.

Let us imagine that we have a controller in our Pecan application which
we want to use to return ``JSON`` output for a ``User`` object::
    
    from myproject.lib import get_current_user
    
    class UsersController(object):
        @expose('json')
        @validate()
        def current_user(self):
            '''
            return an instance of myproject.model.User which represents
            the current authenticated user
            '''
            return get_current_user()

In order for this controller to function, Pecan will need to know how to
convert the ``User`` object into a ``JSON``-friendly data structure. One
way to tell Pecan how to convert an object into ``JSON`` is to define a
rule in your ``json.py``::

    from pecan.jsonify import jsonify
    from myproject import model
    
    @jsonify.when_type(model.User)
    def jsonify_user(user):
        return dict(
            name = user.name,
            email = user.email,
            birthday = user.birthday.isoformat()
        )

In this example, when an instance of the ``model.User`` class is
returned from a controller which is configured to return ``JSON``, the
``jsonify_user`` rule will be called to generate that ``JSON``. Note
that the rule does not generate a ``JSON`` string, but rather generates
a Python dictionary which contains only ``JSON`` friendly data types.

Alternatively, the rule can be specified on the object itself, by
specifying a ``__json__`` method on the object::

    class User(object):
        def __init__(self, name, email, birthday):
            self.name = name
            self.email = email
            self.birthday = birthday
        
        def __json__(self):
            return dict(
                name = self.name,
                email = self.email,
                birthday = self.birthday.isoformat()
            )

The benefit of using a ``json.py`` module is having all of your ``JSON``
rules defined in a central location, but some projects prefer the
simplicity of keeping the ``JSON`` rules attached directly to their
model objects.