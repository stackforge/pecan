.. _jsonify:


JSON Serialization
==================

Pecan includes a simple, easy-to-use system for generating and serving
JSON. To get started, create a file in your project called
``json.py`` and import it in your project's ``app.py``.

Your ``json`` module will contain a series of rules for generating
JSON from objects you return in your controller.

Let's say that we have a controller in our Pecan application which
we want to use to return JSON output for a :class:`User` object::
    
    from myproject.lib import get_current_user
    
    class UsersController(object):
        @expose('json')
        def current_user(self):
            '''
            return an instance of myproject.model.User which represents
            the current authenticated user
            '''
            return get_current_user()

In order for this controller to function, Pecan will need to know how to
convert the :class:`User` object into data types compatible with JSON. One
way to tell Pecan how to convert an object into JSON is to define a
rule in your ``json.py``::

    from pecan.jsonify import jsonify
    from myproject import model
    
    @jsonify.register(model.User)
    def jsonify_user(user):
        return dict(
            name = user.name,
            email = user.email,
            birthday = user.birthday.isoformat()
        )

In this example, when an instance of the :class:`model.User` class is
returned from a controller which is configured to return JSON, the
:func:`jsonify_user` rule will be called to convert the object to
JSON-compatible data. Note that the rule does not generate a JSON
string, but rather generates a Python dictionary which contains only
JSON friendly data types.

Alternatively, the rule can be specified on the object itself, by
specifying a :func:`__json__` method in the class::

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

The benefit of using a ``json.py`` module is having all of your JSON
rules defined in a central location, but some projects prefer the
simplicity of keeping the JSON rules attached directly to their
model objects.
