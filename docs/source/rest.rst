.. _rest:

Writing RESTful Web Services with Pecan
=======================================

If you need to write controllers to interact with objects, using the 
``RestController`` may help speed things up. It follows the Representational 
State Transfer Protocol, also known as REST, by routing the standard HTTP 
verbs of ``GET``, ``POST``, ``PUT``, and ``DELETE`` to individual methods::

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

By default, the ``RestController`` routes as follows:

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

Pecan's ``RestController`` uses the ``?_method=`` query string to work around
the lack of PUT/DELETE form submission support in most current browsers.

The ``RestController`` still supports the ``index``, ``_default``, and 
``_lookup`` routing overrides. If you need to override ``_route``, however, 
make sure to call ``RestController._route`` at the end of your custom 
``_route`` method so that the REST routing described above still occurs.

Nesting ``RestController``
---------------------------

``RestController`` instances can be nested so that child resources get the 
parameters necessary to look up parent resources. For example::

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

Accessing ``/authors/1/books/2`` would call ``BooksController.get`` with an 
``author_id`` of 1 and ``id`` of 2.

To determine which arguments are associated with the parent resource, Pecan 
looks at the ``get_one`` or ``get`` method signatures, in that order, in the 
parent controller. If the parent resource takes a variable number of arguments, 
Pecan will hand it everything up to the child resource controller name (e.g., 
``books`` in the above example).

Defining Custom Actions
-----------------------

In addition to the default methods defined above, you can add additional 
behaviors to a ``RestController`` by defining a special ``_custom_actions`` 
dictionary. For example::

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

Additional method names are the keys in the dictionary. The values are lists 
of valid HTTP verbs for those custom actions, including PUT and DELETE.
