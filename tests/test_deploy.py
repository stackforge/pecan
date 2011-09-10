from pecan.deploy import deploy
from unittest import TestCase

import pytest
import os
import sys


class TestDeploy(TestCase):

    def setUp(self):
        test_config_d = os.path.join(os.path.dirname(__file__), 'test_config', 'sample_apps')

        if test_config_d not in sys.path:
            sys.path.append(test_config_d)

    def test_module_lookup(self):
        """
        1.  A config file has:
            app { 'modules': [valid_module] }
        2.  The module, `valid_module` has an app.py that defines a `def setup.py`
        """
        test_config_file = os.path.join(os.path.dirname(__file__), 'test_config', 'sample_apps', 'sample_app_config.py')
        assert deploy(test_config_file) == 'DEPLOYED!'

    def test_module_lookup_find_best_match(self):
        """
        1.  A config file has:
            app { 'modules': [invalid_module, valid_module] }
        2.  The module, `valid_module` has an app.py that defines a `def setup_app`
        """
        test_config_file = os.path.join(os.path.dirname(__file__), 'test_config', 'sample_apps', 'sample_app_config.py')
        assert deploy(test_config_file) == 'DEPLOYED!'

    def test_missing_app_file_lookup(self):
        """
        1. A config file has:
            app { 'modules': [valid_module] }
        2. The module has no `app.py` file.
        """
        test_config_file = os.path.join(os.path.dirname(__file__), 'test_config', 'sample_apps', 'sample_app_config_missing.py')
        self.assertRaises(
            Exception, 
            deploy, 
            test_config_file
        )

    def test_missing_setup_app(self):
        """
        1.  A config file has:
            app { 'modules': [valid_module] }
        2.  The module, `valid_module` has an `app.py` that contains no `def setup_app`
        """
        test_config_file = os.path.join(os.path.dirname(__file__), 'test_config', 'sample_apps', 'sample_app_config_missing_app.py')
        self.assertRaises(
            Exception, 
            deploy, 
            test_config_file
        )
