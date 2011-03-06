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

Alternatively, the same functionality can also be accomplished by subclassing Pecan's ``SecureController`` class.
Implementations of ``SecureController`` should extend the ``check_permissions`` classmethod to return a ``True``
or ``False`` value (depending on whether or not the user has permissions to the controller branch)::

    from pecan import expose
    from pecan.secure import SecureController, unlocked
    
    class HighlyClassifiedController(object):
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
        
Writing Authentication Methods
----------------
The ``check_permissions`` method should be used to determine user authentication and authorization.  The
code you implement here could range from simple session assertions (the existing user is authenticated
as an administrator) to connecting to an LDAP service.