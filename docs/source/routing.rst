.. _routing:

Routing
=======

.. note::
    This portion of the documentation is still a work in progress.

When a user requests a Pecan-powered page how does Pecan know which
controller to use? Pecan uses a method known as Object-dispatch to map a
HTTP request to a controller. Obejct-dispatch begins by splitting the
path into a list of components and then walking object path starting at
the root controller. Let's look at a simple store application: ::

    from pecan import expose

    class BooksController(object):
        @expose()
        def index(self):
            return "Welcome to book section."

        @expose()
        def bestsellers(self):
            return "We have 5 books in the top 10."

    class CatalogController(object):
        @expose()
        def index(self):
            return "Welcome to the catalog."

        books = BooksController()

    class RootController(object):
        @expose()
        def index(self):
            return "Welcome to store.example.com!"

        @expose()
        def hours(self):
            return "Open 24/7 on the web."

        catalog = CatalogController()

A request for ``/catalog/books/bestsellers`` from the online store would
begin by Pecan breaking the request up into ``catalog``, ``books``, and
``bestsellers``. Next, Pecan would then lookup ``catalog`` on the root
controller. Using the ``catalog`` object, Pecan would then lookup
``books`` followed by ``bestsellers``. What if the URL ends in a slash?
Pecan will check for an ``index`` method on the current object. In the
example above, you may have noticed the ``expose`` decorator.

Routing Algorithm
-----------------



``_lookup``
-----------

Example ::

    from pecan import expose
    from mymodel import get_student_by_name

    class StudentController(object):
        def __init__(self, person):
            self.student = student

        @expose()
        def name(self):
            return self.student.name

    class ClassController(object):
        @expose()
        def _lookup(self, name, *remainder):
            student = get_student_by_name(name)
            if student:
                return StudentController(student), remainder
            else:
                abort(404)

``_default``
------------

Example ::

    from pecan import expose

    class RootController(object):
        @expose()
        def hello(self):
            return 'hello'

        @expose():
        def bonjour(self):
            return 'bonjour'

        @expose():
        def _default(self):
            return 'I cannot say hi in that language'
            

Overriding ``_route``
---------------------

Example  ::

    from pecan import expose

Controller Args
---------------

Example  ::

    from pecan import expose

    class RootController(object):
        @expose()
        def say(self, msg):
            return msg

Client requests ``/say/hi`` the controller returns "hi".

kwargs    ::

    from pecan import expose
    
    class RootController(object):
        @expose():
        def say(self, msg=None):
            if msg is None:
                return "I not sure what to say"
            else:
                return msg

Client requests ``/say?msg=hello`` the controller returns "hello".

Generic Functions
-----------------

Example  ::

    from pecan import expose

    class RootController(object):
        @expose(generic=True)
        def index(self):
            pass

        @index.when(method='POST'):
        def index_post(self):
            pass

        @index.when(method='GET'):
        def index_get(self):
            pass

Helper Functions
----------------

redirect
abort

``@expose``
-----------

At its core, ``expose`` is how you tell Pecan which methods in a class
are controllers. ``expose`` accepts eight optional parameters some of
which can impact routing. ::

    def expose(template    = None,
           content_type    = 'text/html',
           schema          = None,
           json_schema     = None,
           variable_decode = False,
           error_handler   = None,
           htmlfill        = None,
           generic         = False):

Let's look at an example using template and content_type::

    from pecan import decorators

    class RootController(object):
        @expose('json')
        @expose('text_template.mako', content_type='text/plain')
        @expose('html_template.mako')
        def hello(self):
            return {'msg': 'Hello!'}

You'll notice that we used three expose decorators. The first tells
Pecan to serialize ``dict`` using JSON serialization when the client
requests ``/hello.json``. The second tells the templating engine to use
``text_template.mako`` when the client request ``/hello.txt``. The third
tells Pecan to use the html_template.mako when the client requests
``/hello.html``. If the client requests ``/hello``, Pecan will use the
text/html template.

Advanced Routing
----------------
Hooks
Security
REST Controller
