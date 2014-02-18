.. _routing:

Controllers and Routing
=======================

Pecan uses a routing strategy known as **object-dispatch** to map an
HTTP request to a controller, and then the method to call.
Object-dispatch begins by splitting the path into a list of components
and then walking an object path, starting at the root controller. You
can imagine your application's controllers as a tree of objects
(branches of the object tree map directly to URL paths).

Let's look at a simple bookstore application:

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
Pecan will check for an ``index`` method on the last controller object.

To illustrate further, the following paths:

::

    └── /
        ├── /hours
        └── /catalog
             └── /catalog/books
                └── /catalog/books/bestsellers

route to the following controller methods:

::

    └── RootController.index
        ├── RootController.hours
        └── CatalogController.index
             └── BooksController.index
                └── BooksController.bestsellers

Exposing Controllers
--------------------

You tell Pecan which methods in a class are publically-visible via
:func:`~pecan.decorators.expose`. If a method is *not* decorated with
:func:`~pecan.decorators.expose`, Pecan will never route a request to it.
:func:`~pecan.decorators.expose` accepts three optional parameters, some of
which can impact routing and the content type of the response body.

::

    from pecan import expose

    class RootController(object):
        @expose(
            template        = None,
            content_type    = 'text/html',
            generic         = False
        )
        def hello(self):
            return 'Hello World'


Let's look at an example using ``template`` and ``content_type``:

::

    from pecan import expose

    class RootController(object):
        @expose('json')
        @expose('text_template.mako', content_type='text/plain')
        @expose('html_template.mako')
        def hello(self):
            return {'msg': 'Hello!'}

You'll notice that we called :func:`~pecan.decoators.expose` three times, with
different arguments.

::

        @expose('json')

The first tells Pecan to serialize the response namespace using JSON
serialization when the client requests ``/hello.json``.

::

        @expose('text_template.mako', content_type='text/plain')

The second tells Pecan to use the ``text_template.mako`` template file when the
client requests ``/hello.txt``.

::

        @expose('html_template.mako')

The third tells Pecan to use the ``html_template.mako`` template file when the
client requests ``/hello.html``. If the client requests ``/hello``, Pecan will
use the ``text/html`` content type by default.

.. seealso::

  * :ref:`pecan_decorators`



Pecan's Routing Algorithm
-------------------------

Sometimes, the standard object-dispatch routing isn't adequate to properly
route a URL to a controller. Pecan provides several ways to short-circuit
the object-dispatch system to process URLs with more control, including the
special :func:`_lookup`, :func:`_default`, and :func:`_route` methods. Defining
these methods on your controller objects provides additional flexibility for
processing all or part of a URL.


Setting a Return Status Code
----------------------------

Set a specific HTTP response code (such as ``201 Created``) by
modifying the ``status`` attribute of the response object.

::

    from pecan import expose, response

    class RootController(object):

        @expose('json')
        def hello(self):
            response.status = 201
            return {'foo': 'bar'}

Use the utility function :func:`~pecan.core.abort` to raise HTTP errors.

::

    from pecan import expose, abort

    class RootController(object):

        @expose('json')
        def hello(self):
            abort(404)


:func:`~pecan.core.abort` raises an instance of
:class:`~webob.exc.WSGIHTTPException` which is used by Pecan to render
:default response bodies for HTTP errors.  This exception is stored in
:the WSGI request environ at ``pecan.original_exception``, where it
:can be accessed later in the request cycle (by, for example, other
:middleware or :ref:`errors`).


Routing to Subcontrollers with ``_lookup``
------------------------------------------

The :func:`_lookup` special method provides a way to process a portion of a URL,
and then return a new controller object to route to for the remainder.

A :func:`_lookup` method may accept one or more arguments, segments
of the URL path to be processed (split on
``/``). :func:`_lookup` should also take variable positional arguments
representing the rest of the path, and it should include any portion
of the path it does not process in its return value. The example below
uses a ``*remainder`` list which will be passed to the returned
controller when the object-dispatch algorithm continues.

In addition to being used for creating controllers dynamically,
:func:`_lookup` is called as a last resort, when no other controller
method matches the URL and there is no :func:`_default` method.

::

    from pecan import expose, abort
    from somelib import get_student_by_name

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

An HTTP GET request to ``/8/name`` would return the name of the student
where ``primary_key == 8``.

Falling Back with ``_default``
------------------------------

The :func:`_default` method is called as a last resort when no other controller
methods match the URL via standard object-dispatch.

::

    from pecan import expose

    class RootController(object):
        @expose()
        def english(self):
            return 'hello'

        @expose()
        def french(self):
            return 'bonjour'

        @expose()
        def _default(self):
            return 'I cannot say hello in that language'


In the example above, a request to ``/spanish`` would route to
:func:`RootController._default`.


Defining Customized Routing with ``_route``
-------------------------------------------

The :func:`_route` method allows a controller to completely override the routing
mechanism of Pecan. Pecan itself uses the :func:`_route` method to implement its
:class:`~pecan.rest.RestController`. If you want to design an alternative
routing system on top of Pecan, defining a base controller class that defines
a :func:`_route` method will enable you to have total control.


Interacting with the Request and Response Object
------------------------------------------------

For every HTTP request, Pecan maintains a thread-local reference to the request
and response object, ``pecan.request`` and ``pecan.response``.  These are
instances of :class:`webob.request.BaseRequest` and
:class:`webob.response.Response`, respectively, and can be interacted with from
within Pecan controller code::

    @pecan.expose()
    def login(self):
        assert pecan.request.path == '/login'
        username = pecan.request.POST.get('username')
        password = pecan.request.POST.get('password')

        pecan.response.status_int = 403
        pecan.response.body = 'Bad Login!'

While Pecan abstracts away much of the need to interact with these objects
directly, there may be situations where you want to access them, such as:

* Inspecting components of the URI
* Determining aspects of the request, such as the user's IP address, or the
  referer header
* Setting specific response headers
* Manually rendering a response body


Mapping Controller Arguments
----------------------------

In Pecan, HTTP ``GET`` and ``POST`` variables that are not consumed
during the routing process can be passed onto the controller method as
arguments.

Depending on the signature of the method, these arguments can be mapped
explicitly to arguments:

::

    from pecan import expose

    class RootController(object):
        @expose()
        def index(self, arg):
            return arg

        @expose()
        def kwargs(self, **kwargs):
            return str(kwargs)

::

    $ curl http://localhost:8080/?arg=foo
    foo
    $ curl http://localhost:8080/kwargs?a=1&b=2&c=3
    {u'a': u'1', u'c': u'3', u'b': u'2'}

or can be consumed positionally:

::

    from pecan import expose

    class RootController(object):
        @expose()
        def args(self, *args):
            return ','.join(args)

::

    $ curl http://localhost:8080/args/one/two/three
    one,two,three

The same effect can be achieved with HTTP ``POST`` body variables:

::

    from pecan import expose

    class RootController(object):
        @expose()
        def index(self, arg):
            return arg

::

    $ curl -X POST "http://localhost:8080/" -H "Content-Type: application/x-www-form-urlencoded" -d "arg=foo"
    foo

Handling File Uploads
---------------------

Pecan makes it easy to handle file uploads via standard multipart forms. Simply
define your form with a file input:

.. code-block:: html

    <form action="/upload" method="POST" enctype="multipart/form-data">
      <input type="file" name="file" />
      <button type="submit">Upload</button>
    </form>

You can then read the uploaded file off of the request object in your
application's controller:

::

    from pecan import expose, request

    class RootController(object):
        @expose()
        def upload(self):
            assert isinstance(request.POST['file'], cgi.FieldStorage)
            data = request.POST['file'].file.read()

Helper Functions
----------------

Pecan also provides several useful helper functions for moving between
different routes. The :func:`~pecan.core.redirect` function allows you to issue
internal or ``HTTP 302`` redirects.

.. seealso::

  The :func:`redirect` utility, along with several other useful
  helpers, are documented in :ref:`pecan_core`.
