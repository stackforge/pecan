.. _routing:

Routing
=======

When a user requests a Pecan-powered page how does Pecan know which
controller to use? Pecan uses a method known as object-dispatch to map an
HTTP request to a controller. Object-dispatch begins by splitting the
path into a list of components and then walking an object path, starting at
the root controller. Let's look at a simple bookstore application: 

::

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
begin with Pecan breaking the request up into ``catalog``, ``books``, and
``bestsellers``. Next, Pecan would lookup ``catalog`` on the root
controller. Using the ``catalog`` object, Pecan would then lookup
``books``, followed by ``bestsellers``. What if the URL ends in a slash?
Pecan will check for an ``index`` method on the current object. 

Routing Algorithm
-----------------

Sometimes, the standard object-dispatch routing isn't adequate to properly
route a URL to a controller. Pecan provides several ways to short-circuit 
the object-dispatch system to process URLs with more control, including the
special ``_lookup``, ``_default``, and ``_route`` methods. Defining these
methods on your controller objects provides additional flexibility for 
processing all or part of a URL.


``_lookup``
-----------

The ``_lookup`` special method provides a way to process a portion of a URL, 
and then return a new controller object to route to for the remainder.

A ``_lookup`` method will accept one or more arguments, representing chunks
of the URL to be processed, split on `/`, and then provide a `*remainder` list
which will be processed by the returned controller via object-dispatch.

Additionally, the ``_lookup`` method on a controller is called as a last
resort, when no other controller matches the URL via standard object-dispatch.

::

    from pecan import expose
    from mymodel import get_student_by_name

    class StudentController(object):
        def __init__(self, student):
            self.student = student

        @expose()
        def name(self):
            return self.student.name

    class RootController(object):
        @expose()
        def _lookup(self, primary_key, *remainder):
            student = get_student_by_primary_key(primary_key)
            if student:
                return StudentController(student), remainder
            else:
                abort(404)

An HTTP GET request to `/8/name` would return the name of the student
where `primary_key == 8`.

``_default``
------------

The ``_default`` controller is called when no other controller methods
match the URL via standard object-dispatch.

::

    from pecan import expose

    class RootController(object):
        @expose()
        def hello(self):
            return 'hello'

        @expose()
        def bonjour(self):
            return 'bonjour'

        @expose()
        def _default(self):
            return 'I cannot say hi in that language'
            

Overriding ``_route``
---------------------

The ``_route`` method allows a controller to completely override the routing 
mechanism of Pecan. Pecan itself uses the ``_route`` method to implement its
``RestController``. If you want to design an alternative routing system on 
top of Pecan, defining a base controller class that defines a ``_route`` method
will enable you to have total control.


Controller Arguments
--------------------

A controller can receive arguments in a variety of ways, including ``GET`` and 
``POST`` variables, and even chunks of the URL itself. ``GET`` and ``POST`` 
arguments simply map to arguments on the controller method, while unprocessed
chunks of the URL can be passed as positional arguments to the controller method.

::

    from pecan import expose

    class RootController(object):
        @expose(generic=True)
        def index(self):
            return 'Default case'

        @index.when(method='POST')
        def index_post(self):
            return 'You POSTed to me!'

        @index.when(method='GET')
        def index_get(self):
            return 'You GET me!'


Helper Functions
----------------

Pecan also provides several useful helper functions. The ``redirect``
function allows you to issue internal or ``HTTP 302`` redirects. 
The ``redirect`` utility, along with several other useful helpers, 
are documented in :ref:`pecan_core`.


``@expose``
-----------

At its core, ``@expose`` is how you tell Pecan which methods in a class
are publically-visible controllers. ``@expose`` accepts eight optional
parameters, some of which can impact routing. 

::

    expose(template        = None,
           content_type    = 'text/html',
           schema          = None,
           json_schema     = None,
           variable_decode = False,
           error_handler   = None,
           htmlfill        = None,
           generic         = False)


Let's look at an example using template and content_type

::

    from pecan import decorators

    class RootController(object):
        @expose('json')
        @expose('text_template.mako', content_type='text/plain')
        @expose('html_template.mako')
        def hello(self):
            return {'msg': 'Hello!'}

You'll notice that we used three expose decorators. The first tells
Pecan to serialize our response namespace using JSON serialization when 
the client requests ``/hello.json``. The second tells the templating
engine to use ``text_template.mako`` when the client request ``/hello.txt``. 
The third tells Pecan to use the html_template.mako when the client
requests ``/hello.html``. If the client requests ``/hello``, Pecan will 
use the text/html template.

Please see :ref:`pecan_decorators` for more information on ``@expose``.
