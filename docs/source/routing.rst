.. _routing:

Routing
=======

When a user requests a Pecan-powered page how does Pecan know which
controller to use? Pecan uses a method known as Object-dispatch to map a
HTTP request to a controller. Object-dispatch begins by splitting the
path into a list of components and then walking an object path starting at
the root controller. Let's look at a simple store application: 

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
begin by Pecan breaking the request up into ``catalog``, ``books``, and
``bestsellers``. Next, Pecan would then lookup ``catalog`` on the root
controller. Using the ``catalog`` object, Pecan would then lookup
``books`` followed by ``bestsellers``. What if the URL ends in a slash?
Pecan will check for an ``index`` method on the current object. In the
example above, you may have noticed the ``expose`` decorator.

Routing Algorithm
-----------------

Sometimes, the standard object-dispatch routing isn't adequate to properly
route a URL to a controller. Pecan provides several ways to short-circuit 
the object-dispatch system to process URLs with more control, including the
``_lookup``, ``_default``, and ``_route`` special methods. Defining these
methods on your controller objects provide several additional ways to 
process all or part of a URL.


``_lookup``
-----------

The ``_lookup`` special method provides a way to process part of a URL, 
and then return a new controller object to route on for the remainder.

A ``_lookup`` method will accept one or more arguments representing chunks
of the URL to be processed, split on `/`, and then a `*remainder` list which
will be processed by the returned controller via object-dispatch.

The ``_lookup`` method must return a two-tuple including the controller to
process the remainder of the URL, and the remainder of the URL itself.

The ``_lookup`` method on a controller is called when no other controller 
matches the URL via standard object-dispatch.


Example 

::

    from pecan import expose
    from mymodel import get_student_by_name

    class StudentController(object):
        def __init__(self, student):
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

The ``_default`` controller is called when no other controller methods
match the URL vis standard object-dispatch.


Example 

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

Example  

::

    from pecan import expose

    class RootController(object):
        @expose()
        def say(self, msg):
            return msg


In this example, if a ``GET`` request is sent to ``/say/hello``, the controller
returns "hello". On the other hand, if a ``GET`` request is sent to 
``/say?msg=World``, then the controller returns "World".

Keyword arguments are also supported for defaults.

kwargs    

::

    from pecan import expose
    
    class RootController(object):
        @expose()
        def say(self, msg="No message"):
            return msg

In this example, if the client requests ``/say?msg=hello`` the controller returns 
"hello". However, if the client requests ``/say`` without any arguments, the 
controller returns "No message".


Generic Functions
-----------------

Pecan also provides a unique and useful way to dispatch from a controller to other
methods based upon the ``HTTP`` method (``GET``, ``POST``, ``PUT``, etc.) using
a system called "generic functions." A controller can be flagged as generic via a
keyword argument on the ``@expose`` decorator. This makes it possible to utilize
the ``@when`` decorator on the controller itself to define controllers to be called
instead when certain ``HTTP`` methods are sent.


Example

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
are controllers. ``@expose`` accepts eight optional parameters some of
which can impact routing. 

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
