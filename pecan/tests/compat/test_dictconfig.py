# Copyright 2009-2010 by Vinay Sajip. All Rights Reserved.
#
# Permission to use, copy, modify, and distribute this software and its
# documentation for any purpose and without fee is hereby granted,
# provided that the above copyright notice appear in all copies and that
# both that copyright notice and this permission notice appear in
# supporting documentation, and that the name of Vinay Sajip
# not be used in advertising or publicity pertaining to distribution
# of the software without specific, written prior permission.
# VINAY SAJIP DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING
# ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL
# VINAY SAJIP BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR
# ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER
# IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
# OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import sys
try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO  # noqa

from pecan.compat.dictconfig import dictConfig
import logging
import re
from test.test_support import captured_stdout
import unittest


class BaseTest(unittest.TestCase):

    """Base class for logging tests."""

    log_format = "%(name)s -> %(levelname)s: %(message)s"
    expected_log_pat = r"^([\w.]+) -> ([\w]+): ([\d]+)$"
    message_num = 0

    def setUp(self):
        """Setup the default logging stream to an internal StringIO instance,
        so that we can examine log output as we want."""
        logger_dict = logging.getLogger().manager.loggerDict
        logging._acquireLock()
        try:
            self.saved_handlers = logging._handlers.copy()
            self.saved_handler_list = logging._handlerList[:]
            self.saved_loggers = logger_dict.copy()
            self.saved_level_names = logging._levelNames.copy()
        finally:
            logging._releaseLock()

        self.root_logger = logging.getLogger("")
        self.original_logging_level = self.root_logger.getEffectiveLevel()

        self.stream = StringIO()
        self.root_logger.setLevel(logging.DEBUG)
        self.root_hdlr = logging.StreamHandler(self.stream)
        self.root_formatter = logging.Formatter(self.log_format)
        self.root_hdlr.setFormatter(self.root_formatter)
        self.root_logger.addHandler(self.root_hdlr)

    def tearDown(self):
        """Remove our logging stream, and restore the original logging
        level."""
        self.stream.close()
        self.root_logger.removeHandler(self.root_hdlr)
        self.root_logger.setLevel(self.original_logging_level)
        logging._acquireLock()
        try:
            logging._levelNames.clear()
            logging._levelNames.update(self.saved_level_names)
            logging._handlers.clear()
            logging._handlers.update(self.saved_handlers)
            logging._handlerList[:] = self.saved_handler_list
            loggerDict = logging.getLogger().manager.loggerDict
            loggerDict.clear()
            loggerDict.update(self.saved_loggers)
        finally:
            logging._releaseLock()

    def assert_log_lines(self, expected_values, stream=None):
        """Match the collected log lines against the regular expression
        self.expected_log_pat, and compare the extracted group values to
        the expected_values list of tuples."""
        stream = stream or self.stream
        pat = re.compile(self.expected_log_pat)
        try:
            stream.reset()
            actual_lines = stream.readlines()
        except AttributeError:
            # StringIO.StringIO lacks a reset() method.
            actual_lines = stream.getvalue().splitlines()
        self.assertEquals(len(actual_lines), len(expected_values))
        for actual, expected in zip(actual_lines, expected_values):
            match = pat.search(actual)
            if not match:
                self.fail("Log line does not match expected pattern:\n" +
                            actual)
            self.assertEquals(tuple(match.groups()), expected)
        s = stream.read()
        if s:
            self.fail("Remaining output at end of log stream:\n" + s)

    def next_message(self):
        """Generate a message consisting solely of an auto-incrementing
        integer."""
        self.message_num += 1
        return "%d" % self.message_num


class ExceptionFormatter(logging.Formatter):
    """A special exception formatter."""
    def formatException(self, ei):
        return "Got a [%s]" % ei[0].__name__


def formatFunc(format, datefmt=None):
    return logging.Formatter(format, datefmt)


def handlerFunc():
    return logging.StreamHandler()


class CustomHandler(logging.StreamHandler):
    pass


class ConfigDictTest(BaseTest):

    """Reading logging config from a dictionary."""

    expected_log_pat = r"^([\w]+) \+\+ ([\w]+)$"

    # config0 is a standard configuration.
    config0 = {
        'version': 1,
        'formatters': {
            'form1': {
                'format': '%(levelname)s ++ %(message)s',
            },
        },
        'handlers': {
            'hand1': {
                'class': 'logging.StreamHandler',
                'formatter': 'form1',
                'level': 'NOTSET',
                'stream': 'ext://sys.stdout',
            },
        },
        'root': {
            'level': 'WARNING',
            'handlers': ['hand1'],
        },
    }

    # config1 adds a little to the standard configuration.
    config1 = {
        'version': 1,
        'formatters': {
            'form1': {
                'format': '%(levelname)s ++ %(message)s',
            },
        },
        'handlers': {
            'hand1': {
                'class': 'logging.StreamHandler',
                'formatter': 'form1',
                'level': 'NOTSET',
                'stream': 'ext://sys.stdout',
            },
        },
        'loggers': {
            'compiler.parser': {
                'level': 'DEBUG',
                'handlers': ['hand1'],
            },
        },
        'root': {
            'level': 'WARNING',
        },
    }

    # config2 has a subtle configuration error that should be reported
    config2 = {
        'formatters': {
            'form1': {
                'format': '%(levelname)s ++ %(message)s',
            },
        },
        'handlers': {
            'hand1': {
                'class': 'logging.StreamHandler',
                'formatter': 'form1',
                'level': 'NOTSET',
                'stream': 'ext://sys.stdbout',
            },
        },
        'loggers': {
            'compiler.parser': {
                'level': 'DEBUG',
                'handlers': ['hand1'],
            },
        },
        'root': {
            'level': 'WARNING',
        },
    }

    #As config1 but with a misspelt level on a handler
    config2a = {
        'formatters': {
            'form1': {
                'format': '%(levelname)s ++ %(message)s',
            },
        },
        'handlers': {
            'hand1': {
                'class': 'logging.StreamHandler',
                'formatter': 'form1',
                'level': 'NTOSET',
                'stream': 'ext://sys.stdout',
            },
        },
        'loggers': {
            'compiler.parser': {
                'level': 'DEBUG',
                'handlers': ['hand1'],
            },
        },
        'root': {
            'level': 'WARNING',
        },
    }

    #As config1 but with a misspelt level on a logger
    config2b = {
        'formatters': {
            'form1': {
                'format': '%(levelname)s ++ %(message)s',
            },
        },
        'handlers': {
            'hand1': {
                'class': 'logging.StreamHandler',
                'formatter': 'form1',
                'level': 'NOTSET',
                'stream': 'ext://sys.stdout',
            },
        },
        'loggers': {
            'compiler.parser': {
                'level': 'DEBUG',
                'handlers': ['hand1'],
            },
        },
        'root': {
            'level': 'WRANING',
        },
    }

    # config3 has a less subtle configuration error
    config3 = {
        'formatters': {
            'form1': {
                'format': '%(levelname)s ++ %(message)s',
            },
        },
        'handlers': {
            'hand1': {
                'class': 'logging.StreamHandler',
                'formatter': 'misspelled_name',
                'level': 'NOTSET',
                'stream': 'ext://sys.stdout',
            },
        },
        'loggers': {
            'compiler.parser': {
                'level': 'DEBUG',
                'handlers': ['hand1'],
            },
        },
        'root': {
            'level': 'WARNING',
        },
    }

    # config4 specifies a custom formatter class to be loaded
    config4 = {
        'version': 1,
        'formatters': {
            'form1': {
                '()': __name__ + '.ExceptionFormatter',
                'format': '%(levelname)s:%(name)s:%(message)s',
            },
        },
        'handlers': {
            'hand1': {
                'class': 'logging.StreamHandler',
                'formatter': 'form1',
                'level': 'NOTSET',
                'stream': 'ext://sys.stdout',
            },
        },
        'root': {
            'level': 'NOTSET',
                'handlers': ['hand1'],
        },
    }

    # As config4 but using an actual callable rather than a string
    config4a = {
        'version': 1,
        'formatters': {
            'form1': {
                '()': ExceptionFormatter,
                'format': '%(levelname)s:%(name)s:%(message)s',
            },
            'form2': {
                '()': __name__ + '.formatFunc',
                'format': '%(levelname)s:%(name)s:%(message)s',
            },
            'form3': {
                '()': formatFunc,
                'format': '%(levelname)s:%(name)s:%(message)s',
            },
        },
        'handlers': {
            'hand1': {
                'class': 'logging.StreamHandler',
                'formatter': 'form1',
                'level': 'NOTSET',
                'stream': 'ext://sys.stdout',
            },
            'hand2': {
                '()': handlerFunc,
            },
        },
        'root': {
            'level': 'NOTSET',
                'handlers': ['hand1'],
        },
    }

    # config5 specifies a custom handler class to be loaded
    config5 = {
        'version': 1,
        'formatters': {
            'form1': {
                'format': '%(levelname)s ++ %(message)s',
            },
        },
        'handlers': {
            'hand1': {
                'class': __name__ + '.CustomHandler',
                'formatter': 'form1',
                'level': 'NOTSET',
                'stream': 'ext://sys.stdout',
            },
        },
        'loggers': {
            'compiler.parser': {
                'level': 'DEBUG',
                'handlers': ['hand1'],
            },
        },
        'root': {
            'level': 'WARNING',
        },
    }

    # config6 specifies a custom handler class to be loaded
    # but has bad arguments
    config6 = {
        'formatters': {
            'form1': {
                'format': '%(levelname)s ++ %(message)s',
            },
        },
        'handlers': {
            'hand1': {
                'class': __name__ + '.CustomHandler',
                'formatter': 'form1',
                'level': 'NOTSET',
                'stream': 'ext://sys.stdout',
                '9': 'invalid parameter name',
            },
        },
        'loggers': {
            'compiler.parser': {
                'level': 'DEBUG',
                'handlers': ['hand1'],
            },
        },
        'root': {
            'level': 'WARNING',
        },
    }

    #config 7 does not define compiler.parser but defines compiler.lexer
    #so compiler.parser should be disabled after applying it
    config7 = {
        'version': 1,
        'formatters': {
            'form1': {
                'format': '%(levelname)s ++ %(message)s',
            },
        },
        'handlers': {
            'hand1': {
                'class': 'logging.StreamHandler',
                'formatter': 'form1',
                'level': 'NOTSET',
                'stream': 'ext://sys.stdout',
            },
        },
        'loggers': {
            'compiler.lexer': {
                'level': 'DEBUG',
                'handlers': ['hand1'],
            },
        },
        'root': {
            'level': 'WARNING',
        },
    }

    config8 = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'form1': {
                'format': '%(levelname)s ++ %(message)s',
            },
        },
        'handlers': {
            'hand1': {
                'class': 'logging.StreamHandler',
                'formatter': 'form1',
                'level': 'NOTSET',
                'stream': 'ext://sys.stdout',
            },
        },
        'loggers': {
            'compiler': {
                'level': 'DEBUG',
                'handlers': ['hand1'],
            },
            'compiler.lexer': {
            },
        },
        'root': {
            'level': 'WARNING',
        },
    }

    config9 = {
        'version': 1,
        'formatters': {
            'form1': {
                'format': '%(levelname)s ++ %(message)s',
            },
        },
        'handlers': {
            'hand1': {
                'class': 'logging.StreamHandler',
                'formatter': 'form1',
                'level': 'WARNING',
                'stream': 'ext://sys.stdout',
            },
        },
        'loggers': {
            'compiler.parser': {
                'level': 'WARNING',
                'handlers': ['hand1'],
            },
        },
        'root': {
            'level': 'NOTSET',
        },
    }

    config9a = {
        'version': 1,
        'incremental': True,
        'handlers': {
            'hand1': {
                'level': 'WARNING',
            },
        },
        'loggers': {
            'compiler.parser': {
                'level': 'INFO',
            },
        },
    }

    config9b = {
        'version': 1,
        'incremental': True,
        'handlers': {
            'hand1': {
                'level': 'INFO',
            },
        },
        'loggers': {
            'compiler.parser': {
                'level': 'INFO',
            },
        },
    }

    #As config1 but with a filter added
    config10 = {
        'version': 1,
        'formatters': {
            'form1': {
                'format': '%(levelname)s ++ %(message)s',
            },
        },
        'filters': {
            'filt1': {
                'name': 'compiler.parser',
            },
        },
        'handlers': {
            'hand1': {
                'class': 'logging.StreamHandler',
                'formatter': 'form1',
                'level': 'NOTSET',
                'stream': 'ext://sys.stdout',
                'filters': ['filt1'],
            },
        },
        'loggers': {
            'compiler.parser': {
                'level': 'DEBUG',
                'filters': ['filt1'],
            },
        },
        'root': {
            'level': 'WARNING',
            'handlers': ['hand1'],
        },
    }

    def apply_config(self, conf):
        dictConfig(conf)

    def test_config0_ok(self):
        # A simple config which overrides the default settings.
        with captured_stdout() as output:
            self.apply_config(self.config0)
            logger = logging.getLogger()
            # Won't output anything
            logger.info(self.next_message())
            # Outputs a message
            logger.error(self.next_message())
            self.assert_log_lines([
                ('ERROR', '2'),
            ], stream=output)
            # Original logger output is empty.
            self.assert_log_lines([])

    def test_config1_ok(self, config=config1):
        # A config defining a sub-parser as well.
        with captured_stdout() as output:
            self.apply_config(config)
            logger = logging.getLogger("compiler.parser")
            # Both will output a message
            logger.info(self.next_message())
            logger.error(self.next_message())
            self.assert_log_lines([
                ('INFO', '1'),
                ('ERROR', '2'),
            ], stream=output)
            # Original logger output is empty.
            self.assert_log_lines([])

    def test_config2_failure(self):
        # A simple config which overrides the default settings.
        self.assertRaises(StandardError, self.apply_config, self.config2)

    def test_config2a_failure(self):
        # A simple config which overrides the default settings.
        self.assertRaises(StandardError, self.apply_config, self.config2a)

    def test_config2b_failure(self):
        # A simple config which overrides the default settings.
        self.assertRaises(StandardError, self.apply_config, self.config2b)

    def test_config3_failure(self):
        # A simple config which overrides the default settings.
        self.assertRaises(StandardError, self.apply_config, self.config3)

    def test_config4_ok(self):
        # A config specifying a custom formatter class.
        with captured_stdout() as output:
            self.apply_config(self.config4)
            #logger = logging.getLogger()
            try:
                raise RuntimeError()
            except RuntimeError:
                logging.exception("just testing")
            sys.stdout.seek(0)
            self.assertEquals(output.getvalue(),
                "ERROR:root:just testing\nGot a [RuntimeError]\n")
            # Original logger output is empty
            self.assert_log_lines([])

    def test_config4a_ok(self):
        # A config specifying a custom formatter class.
        with captured_stdout() as output:
            self.apply_config(self.config4a)
            #logger = logging.getLogger()
            try:
                raise RuntimeError()
            except RuntimeError:
                logging.exception("just testing")
            sys.stdout.seek(0)
            self.assertEquals(output.getvalue(),
                "ERROR:root:just testing\nGot a [RuntimeError]\n")
            # Original logger output is empty
            self.assert_log_lines([])

    def test_config5_ok(self):
        self.test_config1_ok(config=self.config5)

    def test_config6_failure(self):
        self.assertRaises(StandardError, self.apply_config, self.config6)

    def test_config7_ok(self):
        with captured_stdout() as output:
            self.apply_config(self.config1)
            logger = logging.getLogger("compiler.parser")
            # Both will output a message
            logger.info(self.next_message())
            logger.error(self.next_message())
            self.assert_log_lines([
                ('INFO', '1'),
                ('ERROR', '2'),
            ], stream=output)
            # Original logger output is empty.
            self.assert_log_lines([])
        with captured_stdout() as output:
            self.apply_config(self.config7)
            logger = logging.getLogger("compiler.parser")
            self.assertTrue(logger.disabled)
            logger = logging.getLogger("compiler.lexer")
            # Both will output a message
            logger.info(self.next_message())
            logger.error(self.next_message())
            self.assert_log_lines([
                ('INFO', '3'),
                ('ERROR', '4'),
            ], stream=output)
            # Original logger output is empty.
            self.assert_log_lines([])

    #Same as test_config_7_ok but don't disable old loggers.
    def test_config_8_ok(self):
        with captured_stdout() as output:
            self.apply_config(self.config1)
            logger = logging.getLogger("compiler.parser")
            # Both will output a message
            logger.info(self.next_message())
            logger.error(self.next_message())
            self.assert_log_lines([
                ('INFO', '1'),
                ('ERROR', '2'),
            ], stream=output)
            # Original logger output is empty.
            self.assert_log_lines([])
        with captured_stdout() as output:
            self.apply_config(self.config8)
            logger = logging.getLogger("compiler.parser")
            self.assertFalse(logger.disabled)
            # Both will output a message
            logger.info(self.next_message())
            logger.error(self.next_message())
            logger = logging.getLogger("compiler.lexer")
            # Both will output a message
            logger.info(self.next_message())
            logger.error(self.next_message())
            self.assert_log_lines([
                ('INFO', '3'),
                ('ERROR', '4'),
                ('INFO', '5'),
                ('ERROR', '6'),
            ], stream=output)
            # Original logger output is empty.
            self.assert_log_lines([])

    def test_config_9_ok(self):
        with captured_stdout() as output:
            self.apply_config(self.config9)
            logger = logging.getLogger("compiler.parser")
            # Nothing will be output since both handler and logger are
            # set to WARNING
            logger.info(self.next_message())
            self.assert_log_lines([], stream=output)
            self.apply_config(self.config9a)
            # Nothing will be output since both handler is still set
            # to WARNING
            logger.info(self.next_message())
            self.assert_log_lines([], stream=output)
            self.apply_config(self.config9b)
            # Message should now be output
            logger.info(self.next_message())
            if sys.version_info[:2] == (2, 7):
                self.assert_log_lines([
                    ('INFO', '3'),
                ], stream=output)
            else:
                self.assert_log_lines([], stream=output)

    def test_config_10_ok(self):
        with captured_stdout() as output:
            self.apply_config(self.config10)
            logger = logging.getLogger("compiler.parser")
            logger.warning(self.next_message())
            logger = logging.getLogger('compiler')
            #Not output, because filtered
            logger.warning(self.next_message())
            logger = logging.getLogger('compiler.lexer')
            #Not output, because filtered
            logger.warning(self.next_message())
            logger = logging.getLogger("compiler.parser.codegen")
            #Output, as not filtered
            logger.error(self.next_message())
            self.assert_log_lines([
                ('WARNING', '1'),
                ('ERROR', '4'),
            ], stream=output)
