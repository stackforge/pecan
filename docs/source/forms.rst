.. _forms:

Generating and Validating Forms
===============================
Out of the box, Pecan provides no opinionated support for working with
form generation and validation libraries, but it’s easy to import your
library of choice with minimal effort.

This article details best practices for integrating the popular forms library,
`WTForms <http://wtforms.simplecodes.com/>`_, into your Pecan project.

Defining a Form Definition
--------------------------

A basic form with a first name field that is required and a last name optional
field.

.. code-block:: python

    from wtforms import Form, TextField, validators

    class SomeController(object):
        ...
        class MyForm(Form):
            first_name = TextField(u'First Name', validators=[validators.required()])
            last_name = TextField(u'Last Name', validators=[validators.optional()])

Rendering a Form in a Template
------------------------------

Using that same MyForm definition we can render it to a template.

In the controller file:

.. code-block:: python

    class SomeController(object):
        @expose(template='index.html)
        def index(self):
            return dict(form=self.MyForm())

In the template file using `Mako <http://www.makeotemplates.org/>`_:

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

Using the same MyForm definition we will redirect if the form is validated,
otherwise, render the form again.

.. code-block:: python

    from pecan import request

    class SomeController(object):
        @expose(method='POST', template='index.html')
        def index(self):
            my_form = MyForm(request.POST)
            if request.method == 'POST' && my_form.validate():
                save_values()
                redirect('/success')
            else:
                return dict(form=my_form)
        ...

