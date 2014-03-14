.. _simple_forms_processing:

Example Application: Simple Forms Processing
============================================

This guide will walk you through building a simple Pecan web application that will do some simple forms processing.

Project Setup
-------------

First, you'll need to install Pecan:

::

$ pip install pecan

Use Pecan's basic template support to start a new project:

::

$ pecan create mywebsite
$ cd mywebsite

Install the new project in development mode:

::

$ python setup.py develop

With the project ready, go into the ``templates`` folder and edit the ``index.html`` file. Modify it so that it resembles this:

.. code-block:: html

    <%inherit file="layout.html" />

    <%def name="title()">
        Welcome to Pecan!
    </%def>
        <header>
            <h1><img src="/images/logo.png" /></h1>
        </header>
        <div id="content">
            <form method="POST" action="/">
                <fieldset>
                    <p>Enter a message: <input name="message" /></p>
                    <p>Enter your first name: <input name="first_name" /></p>
                    <input type="submit" value="Submit" />
                </fieldset>
            </form>
            % if not form_post_data is UNDEFINED:
                <p>${form_post_data['first_name']}, your message is: ${form_post_data['message']}</p>
            % endif
        </div>

**What did we just do?**

#. Modified the contents of the ``form`` tag to have two ``input`` tags. The first is named ``message`` and the second is named ``first_name``
#. Added a check if ``form_post_data`` has not been defined so we don't show the message or wording
#. Added code to display the message from the user's ``POST`` action

Go into the ``controllers`` folder now and edit the ``root.py`` file. There will be two functions inside of the ``RootController`` class which will display the ``index.html`` file when your web browser hits the ``'/'`` endpoint. If the user puts some data into the textbox and hits the submit button then they will see the personalized message displayed back at them.

Modify the ``root.py`` to look like this:

.. code-block:: python

    from pecan import expose


    class RootController(object):

        @expose(generic=True, template='index.html')
        def index(self):
            return dict()

        @index.when(method='POST', template='index.html')
        def index_post(self, **kwargs):
            return dict(form_post_data=kwargs)

**What did we just do?**

#. Modified the ``index`` function to render the initial ``index.html`` webpage
#. Modified the ``index_post`` function to return the posted data via keyword arguments

Run the application:

::

$ pecan serve config.py

Open a web browser: `http://127.0.0.1:8080/ <http://127.0.0.1:8080/>`_

Adding Validation
-----------------

Enter a message into the textbox along with a name in the second textbox and press the submit button. You should see a personalized message displayed below the form once the page posts back.

One problem you might have noticed is if you don't enter a message or a first name then you simply see no value entered for that part of the message. Let's add a little validation to make sure a message and a first name was actually entered. For this, we will use `WTForms <http://wtforms.simplecodes.com/>`_ but you can substitute anything else for your projects.

Add support for the `WTForms <http://wtforms.simplecodes.com/>`_ library:

::

$ pip install wtforms

.. note::

    Keep in mind that Pecan is not opinionated when it comes to a particular library when working with form generation, validation, etc. Choose which libraries you prefer and integrate those with Pecan. This is one way of doing this, there are many more ways so feel free to handle this however you want in your own projects.

Go back to the ``root.py`` files and modify it like this:

.. code-block:: python

    from pecan import expose, request
    from wtforms import Form, TextField, validators


    class PersonalizedMessageForm(Form):
        message = TextField(u'Enter a message',
                            validators=[validators.required()])
        first_name = TextField(u'Enter your first name',
                               validators=[validators.required()])


    class RootController(object):

        @expose(generic=True, template='index.html')
        def index(self):
            return dict(form=PersonalizedMessageForm())

        @index.when(method='POST', template='index.html')
        def index_post(self):
            form = PersonalizedMessageForm(request.POST)
            if form.validate():
                return dict(message=form.message.data,
                            first_name=form.first_name.data)
            else:
                return dict(form=form)

**What did we just do?**

#. Added the ``PersonalizedMessageForm`` with two textfields and a required field validator for each
#. Modified the ``index`` function to create a new instance of the ``PersonalizedMessageForm`` class and return it
#. In the ``index_post`` function modify it to gather the posted data and validate it. If its valid, then set the returned data to be displayed on the webpage. If not valid, send the form which will contain the data plus the error message(s)

Modify the ``index.html`` like this:

.. code-block:: html

    <%inherit file="layout.html" />

    ## provide definitions for blocks we want to redefine
    <%def name="title()">
        Welcome to Pecan!
    </%def>
        <header>
            <h1><img src="/images/logo.png" /></h1>
        </header>
        <div id="content">
            % if not form:
                <p>${first_name}, your message is: ${message}</p>
            % else:
                <form method="POST" action="/">
                    <div>
                        ${form.message.label}:
                        ${form.message}
                        % if form.message.errors:
                            <strong>${form.message.errors[0]}</strong>
                        % endif
                    </div>
                   <div>
                        ${form.first_name.label}:
                        ${form.first_name}
                        % if form.first_name.errors:
                            <strong>${form.first_name.errors[0]}</strong>
                        % endif
                    </div>
                    <input type="submit" value="Submit">
                </form>
            % endif
        </div>

.. note::

    Keep in mind when using the `WTForms <http://wtforms.simplecodes.com/>`_ library you can customize the error messages and more. Also, you have multiple validation rules so make sure to catch all the errors which will mean you need a loop rather than the simple example above which grabs the first error item in the list. See the `documentation <http://wtforms.simplecodes.com/>`_ for more information.

Run the application:

::

$ pecan serve config.py

Open a web browser: `http://127.0.0.1:8080/ <http://127.0.0.1:8080/>`_

Try the form with valid data and with no data entered.
