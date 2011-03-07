.. _secure_controller:

Security and Authentication
=============
Pecan provides no out-of-the-box support for authentication, but it does give you the
necessary tools to handle authentication and authorization as you see fit.

In Pecan, you can wrap entire controller subtrees *or* individual method calls with 
function calls to determine access and secure portions of your application.

Pecan's ``secure`` method secures a method or class depending on invocation.

To decorate a method, use one argument::

    @secure('<check_permissions_method>')

To secure a class, invoke with two arguments::

    secure(<object instance>, '<check_permissions_method>')

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

Alternatively, the same functionality can also be accomplished by subclassing Pecan's ``SecureController`` class.
Implementations of ``SecureController`` should extend the ``check_permissions`` classmethod to return a ``True``
or ``False`` value (depending on whether or not the user has permissions to the controller branch)::

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
Writing Authentication/Authorization Methods
----------------
The ``check_permissions`` method should be used to determine user authentication and authorization.  The
code you implement here could range from simple session assertions (the existing user is authenticated
as an administrator) to connecting to an LDAP service.  

More on ``secure``
----------------
The ``secure`` method has several advanced uses that allow you to create robust security policies for your application.

First, you can pass via a string the name of either a classmethod or an instance method of the controller to use as the
``check_permission`` method.  Instance methods are particularly useful if you wish to authorize access to attributes
of a particular model instance.  Consider the following example of a basic virtual filesystem::

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


The ``secure`` method also accepts a function instead of a string.  When passing a function,  make sure that the function is imported from another file or defined in the same file before the class definition -- otherwise you will likely get error during module import. ::

    from pecan import expose
    from pecan.secure import secure

    from myapp.auth import user_authenitcated

    class RootController(object):
        @secure(user_authenticated)
        @expose()
        def index(self):
            return 'Logged in'


You can also use the ``secure`` method to change the behavior of a SecureController.  Decorating a method or wrapping a subcontroller tells Pecan to use another security function other than the default controller method.  This is useful for situations where you want a different level or type of security.

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

In the example above, pecan will *only* call ``admin_user`` when a request is made for ``/api/``.

Multiple Secure Controllers
---------------------------
Pecan allows you to have nested secure controllers. In the example below, when a request is made for ``/admin/index/``, Pecan first calls ``check_permissions`` on the RootController and then calls ``check_permissions`` on the AdminController. The ability to nest ``SsecureController`` instances allows you to protect controllers with an increasing level of protection. ::

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
