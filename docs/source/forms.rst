.. _forms:

Generating and Validating Forms
===============================

Pecan provides no opinionated support for working with
form generation and validation libraries, but it’s easy to import your
library of choice with minimal effort.

This article details best practices for integrating the popular forms library,
`WTForms <http://wtforms.simplecodes.com/>`_, into your Pecan project.

Defining a Form Definition
--------------------------

Let's start by building a basic form with a required ``first_name``
field and an optional ``last_name`` field.

::

    from wtforms import Form, TextField, validators

    class MyForm(Form):
        first_name = TextField(u'First Name', validators=[validators.required()])
        last_name = TextField(u'Last Name', validators=[validators.optional()])

    class SomeController(object):
        pass

Rendering a Form in a Template
------------------------------

Next, let's add a controller, and pass a form instance to the template.

::

    from pecan import expose
    from wtforms import Form, TextField, validators

    class MyForm(Form):
        first_name = TextField(u'First Name', validators=[validators.required()])
        last_name = TextField(u'Last Name', validators=[validators.optional()])

    class SomeController(object):

        @expose(template='index.html')
        def index(self):
            return dict(form=MyForm())

Here's the Mako_ template file:

.. _Mako: http://www.makeotemplates.org/

.. code-block:: html

    <form method="post" action="/">
        <div>
            ${form.first_name.label}:
            ${form.first_name}
        </div>
        <div>
            ${form.last_name.label}:
            ${form.last_name}
        </div>
        <input type="submit" value="submit">
    </form>

Validating POST Values
----------------------

Using the same :class:`MyForm` definition, let's redirect the user if the form is 
validated, otherwise, render the form again.

.. code-block:: python

    from pecan import expose, request
    from wtforms import Form, TextField, validators

    class MyForm(Form):
        first_name = TextField(u'First Name', validators=[validators.required()])
        last_name = TextField(u'Last Name', validators=[validators.optional()])

    class SomeController(object):

        @expose(template='index.html')
        def index(self):
            my_form = MyForm(request.POST)
            if request.method == 'POST' and my_form.validate():
                # save_values()
                redirect('/success')
            else:
                return dict(form=my_form)
