import sys, os
import subprocess

class MonitorableProcess(object):
    
    _reloader_environ_key = 'PYTHON_RELOADER_SHOULD_RUN'
    
    def start_monitoring(self):
        if os.environ.get(self._reloader_environ_key):
            from paste import reloader
            reloader.install()
        else:
            return self.restart_with_reloader()        
    
    def restart_with_reloader(self):
        print 'Starting subprocess with file monitor'
        while 1:
            args = [self.quote_first_command_arg(sys.executable)] + sys.argv
            new_environ = os.environ.copy()
            new_environ[self._reloader_environ_key] = 'true'
            proc = None
            try:
                try:
                    _turn_sigterm_into_systemexit()
                    proc = subprocess.Popen(args, env=new_environ)
                    exit_code = proc.wait()
                    proc = None
                except KeyboardInterrupt:
                    print '^C caught in monitor process'
                    raise
            finally:
                if (proc is not None
                    and hasattr(os, 'kill')):
                    import signal
                    try:
                        os.kill(proc.pid, signal.SIGTERM)
                    except (OSError, IOError):
                        pass
            
            # Reloader always exits with code 3; but if we are
            # a monitor, any exit code will restart
            if exit_code != 3:
                return exit_code
            print '-'*20, 'Restarting', '-'*20
            
    def quote_first_command_arg(self, arg):
        """
        There's a bug in Windows when running an executable that's
        located inside a path with a space in it.  This method handles
        that case, or on non-Windows systems or an executable with no
        spaces, it just leaves well enough alone.
        """
        if (sys.platform != 'win32'
            or ' ' not in arg):
            # Problem does not apply:
            return arg
        try:
            import win32api
        except ImportError:
            raise ValueError(
                "The executable %r contains a space, and in order to "
                "handle this issue you must have the win32api module "
                "installed" % arg)
        arg = win32api.GetShortPathName(arg)
        return arg            
            
def _turn_sigterm_into_systemexit():
    """
    Attempts to turn a SIGTERM exception into a SystemExit exception.
    """
    try:
        import signal
    except ImportError:
        return
    def handle_term(signo, frame):
        raise SystemExit
    signal.signal(signal.SIGTERM, handle_term)