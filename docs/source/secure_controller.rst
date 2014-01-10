.. _secure_controller:

Security and Authentication
===========================

Pecan provides no out-of-the-box support for authentication, but it
does give you the necessary tools to handle authentication and
authorization as you see fit. 

``secure`` Decorator Basics
---------------------------

You can wrap entire controller subtrees *or* individual method calls
with access controls using the :func:`~pecan.secure.secure` decorator.

To decorate a method, use one argument::

    secure('<check_permissions_method_name>')

To secure a class, invoke with two arguments::

    secure(object_instance, '<check_permissions_method_name>')

::

    from pecan import expose
    from pecan.secure import secure
    
    class HighlyClassifiedController(object):
        pass

    class UnclassifiedController(object):
        pass

    class RootController(object):
        
        @classmethod
        def check_permissions(cls):
            if user_is_admin():
                return True
            return False
    
        @expose()
        def index(self):
          #
          # This controller is unlocked to everyone,
          # and will not run any security checks.
          #
          return dict()
    
        @secure('check_permissions')
        @expose()
        def topsecret(self):
            #
            # This controller is top-secret, and should
            # only be reachable by administrators.
            #
            return dict()
    
        highly_classified = secure(HighlyClassifiedController(), 'check_permissions')
        unclassified = UnclassifiedController()


``SecureController``
--------------------

Alternatively, the same functionality can also be accomplished by
subclassing Pecan's :class:`~pecan.secure.SecureController`. Implementations of
:class:`~pecan.secure.SecureController` should extend the
:meth:`~pecan.secure.SecureControllerBase.check_permissions` class method to
return ``True`` if the user has permissions to the controller branch and
``False`` if they do not.

::

    from pecan import expose
    from pecan.secure import SecureController, unlocked
    
    class HighlyClassifiedController(object):
        pass

    class UnclassifiedController(object):
        pass

    class RootController(SecureController):
        
        @classmethod
        def check_permissions(cls):
            if user_is_admin():
                return True
            return False
    
        @expose()
        @unlocked
        def index(self):
          #
          # This controller is unlocked to everyone,
          # and will not run any security checks.
          #
          return dict()
    
        @expose()
        def topsecret(self):
            #
            # This controller is top-secret, and should
            # only be reachable by administrators.
            #
            return dict()
    
        highly_classified = HighlyClassifiedController()
        unclassified = unlocked(UnclassifiedController())


Also note the use of the :func:`~pecan.secure.unlocked` decorator in the above
example, which can be used similarly to explicitly unlock a controller for
public access without any security checks.


Writing Authentication/Authorization Methods
--------------------------------------------

The :meth:`~pecan.secure.SecureControllerBase.check_permissions` method should
be used to determine user authentication and authorization.  The code you
implement here could range from simple session assertions (the existing user is
authenticated as an administrator) to connecting to an LDAP service.


More on ``secure``
------------------

The :func:`~pecan.secure.secure` method has several advanced uses that allow
you to create robust security policies for your application.

First, you can pass via a string the name of either a class method or an 
instance method of the controller to use as the
:meth:`~pecan.secure.SecureControllerBase.check_permissions` method.  Instance
methods are particularly useful if you wish to authorize access to attributes
of a model instance.  Consider the following example of a basic virtual
filesystem.

::

    from pecan import expose
    from pecan.secure import secure
    
    from myapp.session import get_current_user
    from myapp.model import FileObject
    
    class FileController(object):
        def __init__(self, name):
            self.file_object = FileObject(name)
    
        def read_access(self):
            self.file_object.read_access(get_current_user())
    
        def write_access(self):
            self.file_object.write_access(get_current_user())
    
        @secure('write_access')
        @expose()
        def upload_file(self):
            pass
    
        @secure('read_access')
        @expose()
        def download_file(self):
            pass 
    
    class RootController(object):
        @expose()
        def _lookup(self, name, *remainder):
            return FileController(name), remainder


The :func:`~pecan.secure.secure` method also accepts a function argument. When
passing a function,  make sure that the function is imported from another 
file or defined in the same file before the class definition, otherwise 
you will likely get error during module import.

::

    from pecan import expose
    from pecan.secure import secure

    from myapp.auth import user_authenitcated

    class RootController(object):
        @secure(user_authenticated)
        @expose()
        def index(self):
            return 'Logged in'


You can also use the :func:`~pecan.secure.secure` method to change the behavior
of a :class:`~pecan.secure.SecureController`. Decorating a method or wrapping
a subcontroller tells Pecan to use another security function other than the
default controller method. This is useful for situations where you want
a different level or type of security.

::

    from pecan import expose
    from pecan.secure import SecureController, secure

    from myapp.auth import user_authenticated, admin_user

    class ApiController(object):
        pass

    class RootController(SecureController):
        @classmethod
        def check_permissions(cls):
            return user_authenticated()

        @classmethod
        def check_api_permissions(cls):
            return admin_user()

        @expose()
        def index(self):
            return 'logged in user'

        api = secure(ApiController(), 'check_api_permissions')

In the example above, pecan will *only* call :func:`admin_user` when a request is
made for ``/api/``.


Multiple Secure Controllers
---------------------------

Secure controllers can be nested to provide increasing levels of
security on subcontrollers. In the example below, when a request is
made for ``/admin/index/``, Pecan first calls
:func:`~pecan.secure.SecureControllerBase.check_permissions` on the
:class:`RootController` and then
calls :func:`~pecan.secure.SecureControllerBase.check_permissions` on the
:class:`AdminController`.

::

    from pecan import expose
    from pecan.secure import SecureController

    from myapp.auth import user_logged_in, is_admin

    class AdminController(SecureController):
        @classmethod
        def check_permissions(cls):
            return is_admin()

        @expose()
        def index(self):
            return 'admin dashboard'

    class RootController(SecureController):
        @classmethod
        def check_permissions(cls):
            return user_logged_in

        @expose()
        def index(self):
            return 'user dashboard'
