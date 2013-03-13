import sys
import os
if sys.version_info < (2, 7):
    from unittest2 import TestCase  # pragma: nocover
else:
    from unittest import TestCase  # pragma: nocover


class PecanTestCase(TestCase):

    def setUp(self):
        self.addCleanup(self._reset_global_config)

    def _reset_global_config(self):
        from pecan import configuration
        configuration.set_config(
            dict(configuration.initconf()),
            overwrite=True
        )
        os.environ.pop('PECAN_CONFIG', None)
