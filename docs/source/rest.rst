.. _rest:

Writing RESTful Web Services with Pecan
=======================================

If you need to write controllers to interact with objects, using the 
:class:`~pecan.rest.RestController` may help speed things up. It follows the
Representational State Transfer Protocol, also known as REST, by routing the
standard HTTP verbs of ``GET``, ``POST``, ``PUT``, and ``DELETE`` to individual
methods.

::

    from pecan import expose
    from pecan.rest import RestController
    
    from mymodel import Book
    
    class BooksController(RestController):
    
        @expose()
        def get(self, id):
            book = Book.get(id)
            if not book:
                abort(404)
            return book.title

URL Mapping
-----------

By default, :class:`~pecan.rest.RestController` routes as follows:

+-----------------+--------------------------------------------------------------+--------------------------------------------+
| Method          | Description                                                  | Example Method(s) / URL(s)                 |
+=================+==============================================================+============================================+
| get_one         | Display one record.                                          | GET /books/1                               |
+-----------------+--------------------------------------------------------------+--------------------------------------------+
| get_all         | Display all records in a resource.                           | GET /books/                                |
+-----------------+--------------------------------------------------------------+--------------------------------------------+
| get             | A combo of get_one and get_all.                              | GET /books/                                |
|                 |                                                              +--------------------------------------------+
|                 |                                                              | GET /books/1                               |
+-----------------+--------------------------------------------------------------+--------------------------------------------+
| new             | Display a page to create a new resource.                     | GET /books/new                             |
+-----------------+--------------------------------------------------------------+--------------------------------------------+
| edit            | Display a page to edit an existing resource.                 | GET /books/1/edit                          |
+-----------------+--------------------------------------------------------------+--------------------------------------------+
| post            | Create a new record.                                         | POST /books/                               |
+-----------------+--------------------------------------------------------------+--------------------------------------------+
| put             | Update an existing record.                                   | POST /books/1?_method=put                  |
|                 |                                                              +--------------------------------------------+
|                 |                                                              | PUT /books/1                               |
+-----------------+--------------------------------------------------------------+--------------------------------------------+
| get_delete      | Display a delete confirmation page.                          | GET /books/1/delete                        |
+-----------------+--------------------------------------------------------------+--------------------------------------------+
| delete          | Delete an existing record.                                   | POST /books/1?_method=delete               |
|                 |                                                              +--------------------------------------------+
|                 |                                                              | DELETE /books/1                            |
+-----------------+--------------------------------------------------------------+--------------------------------------------+

Pecan's :class:`~pecan.rest.RestController` uses the ``?_method=`` query string
to work around the lack of support for the PUT and DELETE verbs when
submitting forms in most current browsers.

In addition to handling REST, the :class:`~pecan.rest.RestController` also
supports the :meth:`index`, :meth:`_default`, and :meth:`_lookup`
routing overrides. 

.. warning::

  If you need to override :meth:`_route`, make sure to call
  :func:`RestController._route` at the end of your custom method so
  that the REST routing described above still occurs.

Nesting ``RestController``
---------------------------

:class:`~pecan.rest.RestController` instances can be nested so that child
resources receive the parameters necessary to look up parent resources.

For example::

    from pecan import expose
    from pecan.rest import RestController

    from mymodel import Author, Book

    class BooksController(RestController):

        @expose()
        def get(self, author_id, id):
            author = Author.get(author_id)
            if not author_id:
                abort(404)
            book = author.get_book(id)
            if not book:
                abort(404)
            return book.title

    class AuthorsController(RestController):
    
        books = BooksController()
        
        @expose()
        def get(self, id):
            author = Author.get(id)
            if not author:
                abort(404)
            return author.name
    
    class RootController(object):
        
        authors = AuthorsController()

Accessing ``/authors/1/books/2`` invokes :func:`BooksController.get` with 
``author_id`` set to ``1`` and ``id`` set to ``2``.

To determine which arguments are associated with the parent resource, Pecan 
looks at the :func:`get_one` then :func:`get` method signatures, in that order,
in the parent controller. If the parent resource takes a variable number of
arguments, Pecan will pass it everything up to the child resource controller
name (e.g., ``books`` in the above example).

Defining Custom Actions
-----------------------

In addition to the default methods defined above, you can add additional 
behaviors to a :class:`~pecan.rest.RestController` by defining a special
:attr:`_custom_actions`
dictionary.

For example::

    from pecan import expose
    from pecan.rest import RestController
    
    from mymodel import Book
    
    class BooksController(RestController):
        
        _custom_actions = {
            'checkout': ['POST']
        }
        
        @expose()
        def checkout(self, id):
            book = Book.get(id)
            if not book:
                abort(404)
            book.checkout()

:attr:`_custom_actions` maps method names to the list of valid HTTP
verbs for those custom actions. In this case :func:`checkout` supports
``POST``.
