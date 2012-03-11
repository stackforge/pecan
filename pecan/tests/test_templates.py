import os
import tempfile
import shutil
import subprocess
import unittest
import pkg_resources
import virtualenv
import httplib
import urllib2
import time
import pecan

def has_internet():
    try:
        response = urllib2.urlopen('http://google.com', timeout=1)
        return True
    except urllib2.URLError as err: pass # pragma: no cover
    return False


class TestTemplateBuilds(unittest.TestCase):
    """
    Used to build and test the templated quickstart project(s).
    """

    @classmethod
    @unittest.skipUnless(has_internet(), 'Internet connectivity unavailable.')
    @unittest.skipUnless(
        getattr(pecan, '__run_all_tests__', False) is True,
        'Skipping (really slow).  To run, `$ python setup.py test --slow.`'
    )
    def setUpClass(cls):
        # Make a temp install location and record the cwd
        cls.install_dir = tempfile.mkdtemp()
        cls.cwd = os.getcwd()
        cls.install()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.install_dir)
        os.chdir(cls.cwd)

    @classmethod
    def install(cls):
        # Create a new virtualenv in the temp install location
        virtualenv.create_environment(
            cls.install_dir,
            site_packages = False
        )
        # chdir into the pecan source
        os.chdir(pkg_resources.get_distribution('pecan').location)

        py = os.path.join(cls.install_dir, 'bin', 'python')
        pecan_ = os.path.join(cls.install_dir, 'bin', 'pecan')

        # env/bin/python setup.py develop (pecan)
        subprocess.check_call([
            py,
            'setup.py',
            'develop'
        ])
        # create the templated project
        os.chdir(cls.install_dir)
        subprocess.check_call([pecan_, 'create', 'Testing123'])
    
        # move into the new project directory and install
        os.chdir('Testing123')
        subprocess.check_call([
            py,
            'setup.py',
            'develop'
        ])

    def poll(self, proc):
        limit = 5
        for i in range(limit):
            time.sleep(1)
            proc.poll()

            # Make sure it's running
            if proc.returncode is None:
                break
            elif i == limit: # pragma: no cover
                raise RuntimeError("pecan serve config.py didn't start.")

    @unittest.skipUnless(has_internet(), 'Internet connectivity unavailable.')
    def test_project_pecan_serve_command(self):
        pecan_ = os.path.join(self.__class__.install_dir, 'bin', 'pecan')

        # Start the server
        proc = subprocess.Popen([
            pecan_,
            'serve',
            'config.py'
        ])

        try:
            self.poll(proc)

            # ...and that it's serving (valid) content...
            conn = httplib.HTTPConnection('localhost:8080')
            conn.request('GET', '/')
            resp = conn.getresponse()
            assert resp.status == 200
            assert 'This is a sample Pecan project.' in resp.read()
        finally:
            proc.terminate() 

    @unittest.skipUnless(has_internet(), 'Internet connectivity unavailable.')
    def test_project_pecan_shell_command(self):
        from pecan.testing import load_test_app
        pecan_ = os.path.join(self.__class__.install_dir, 'bin', 'pecan')

        # Start the server
        proc = subprocess.Popen([
            pecan_,
            'shell',
            'config.py'
        ], 
            stdout = subprocess.PIPE, 
            stderr = subprocess.PIPE,
            stdin = subprocess.PIPE
        )

        self.poll(proc)

        out, _ = proc.communicate('{"model" : model, "conf" : conf, "app" : app}')
        assert 'testing123.model' in out
        assert 'Config(' in out
        assert 'webtest.app.TestApp' in out

        try:
            # just in case stdin doesn't close
            proc.terminate()
        except: pass

    @unittest.skipUnless(has_internet(), 'Internet connectivity unavailable.')
    def test_project_tests_command(self):
        py = os.path.join(self.__class__.install_dir, 'bin', 'python')

        # Run the tests
        proc = subprocess.Popen([
            py,
            'setup.py',
            'test'
        ], 
            stdout = subprocess.PIPE, 
            stderr = subprocess.PIPE
        )
        proc.wait()

        assert proc.stderr.read().splitlines()[-1].strip() == 'OK'
