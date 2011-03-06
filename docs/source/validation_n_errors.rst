.. _validation_n_errors:

Validation and Error Handling
============
Pecan provides a variety of tools to help you handle common form validation and
error handling activities, like:

* Validating the presence of submitted form contents with a schema.
* Transforming strings from form submissions into useful Python objects.
* Simplifying the process of re-displaying form values and associated error messages inline.

Rather than re-inventing the wheel, Pecan uses `FormEncode <http://formencode.org/>`_ for schemas and form validation.

Writing and Applying Schemas
------------------------------
Here's a simple example of a schema and how to apply it to a controller method using
Pecan's ``expose`` decorator::

    from pecan import expose
    from formencode import Schema, validators as v

    class SimpleSchema(Schema):    
        username = v.String(not_empty=True)
        password = v.String(not_empty=True)
        
    class LoginController(object):

        @expose(schema=SimpleSchema)
        def login(self, **kw):
            if authenticate(
              kw['username'],
              kw['password']
            ):
              set_cookie()
            return dict()

Validating JSON Content
------------------------------
In addition to simple form arguments, Pecan also makes it easy to validate JSON request bodies.
Often, especially in AJAX requests, the request content is encoded as JSON in the request body.
Pecan's validation can handle the decoding for you and apply schema validation to the decoded
data structure::

    from pecan import expose
    from formencode import Schema, validators as v
    from myproject.lib import authenticate

    class JSONSchema(Schema):
        """
        This schema would decode a JSON request body
        that looked like:
        
        {
          'username' : 'pecan',
          'password' : 'dotpy
        }
        
        """
        username = v.String(not_empty=True)
        password = v.String(not_empty=True)
    
    class LoginController(object):

        @expose(json_schema=JSONSchema)
        def login(self, **kw):
            authenticate(
              kw['username'],
              kw['password']
            )
            return dict()

Handling Schema Failures
------------------------------
When schema validation fails, the validation errors from FormEncode are applied to
``pecan.request.validation_errors``.  This list can be browsed in your controller
methods to react to errors appropriately::

    from pecan import expose, request
    from myproject.schemas import SimpleSchema

    class LoginController(object):

        @expose(schema=SimpleSchema)
        def login(self, **kw):
            if request.validation_errors:
                pass # Don't Panic!
            return dict()

Error Handlers and Template Filling
------------------------------
When schema validation fails, Pecan allows you to redirect to another controller internally
for error handling via the `error_handler` keyword argument to ``@expose()``.
This is especially useful when used in combination with generic
controller methods::

  from pecan import request, expose
  from formencode import Schema, validators as v

  class ProfileSchema(Schema):    
      name = v.String(not_empty=True)
      email = v.String(not_empty=True)

  class ProfileController(object):
  
      @expose(generic=True)
      def index(self):
          pass
          
      @index.when(method="GET", template='profile.html')
      def index_get(self):
          """
          This method will be called to render the original template.
          It will also be used for generating a form pre-filled with values
          when schema failures occur.
          """
          return dict()
          
      @index.when(method="POST", schema=ProfileSchema(), error_handler=lambda: request.path)
      def index_post(self, **kw):
          """
          This method will do something with POST arguments.
          If the schema validation fails, an internal redirect will
          cause the `profile.html` template to be rendered via the
          ``index_get`` method.
          """
          
          name = kw.get('name')
          email = ke.get('email')
          
          redirect('/profile')
          
In this example, when form validation errors occur (for example, the email provided is invalid),
Pecan will handle pre-filling the form values in ``profile.html`` for you.  Additionally, inline
errors will be appended to the template using FormEncode's ``htmlfill``.

Bypassing ``htmlfill``
------------------------------
Sometimes you want certain fields in your templates to be ignored (i.e., not pre-filled) by ``htmlfill``.
A perfect use case for this is password and hidden input fields.  The default Pecan template namespace
includes a built-in function, ``static``, which allows you to enforce a static value for form fields,
preventing ``htmlfill`` from filling in submitted form variables::

    <form method="POST">
      <dl>
        <dt>Username:</dt>
          <dd><input type="text" name="username" /></dd>
        <dt>Password:</dt>        
          <dd><input type="password" name="password" value="${static('password', '')}" /></dd>
        <input type="hidden" name="ticket" value="${static('ticket', 'RANDOM_PER_REQUEST_VALUE')}" />
      </dl>
      <button>Login</button>
    </form>

Working with ``variabledecode``
------------------------------
Pecan also lets you take advantage of FormEncode's ``variabledecode`` for transforming flat HTML form
submissions into nested structures::

    from pecan import expose
    from myproject import SimpleSchema

    class ProfileController(object):

        @expose(schema=SimpleSchema(), variable_decode=True)
        def index(self):
            return dict()