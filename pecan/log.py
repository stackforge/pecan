import logging

from logutils.colorize import ColorizingStreamHandler


class DefaultColorizer(ColorizingStreamHandler):

    level_map = {
        logging.DEBUG: (None, 'blue', True),
        logging.INFO: (None, None, True),
        logging.WARNING: (None, 'yellow', True),
        logging.ERROR: (None, 'red', True),
        logging.CRITICAL: (None, 'red', True),
    }


class ColorFormatter(logging.Formatter):
    """
    A very basic logging formatter that not only applies color to the
    levels of the ouput but can also add padding to the the level names so that
    they do not alter the visuals of logging when presented on the terminal.

    The padding is provided by a convenient keyword that adds padding to the
    ``levelname`` so that log output is easier to follow::

        %(padded_color_levelname)s

    Which would result in log level output that looks like::

        [INFO    ]
        [WARNING ]
        [ERROR   ]
        [DEBUG   ]
        [CRITICAL]

    If colored output is not supported, it falls back to non-colored output
    without any extra settings.
    """

    def __init__(self, _logging=None, colorizer=None, *a, **kw):
        self.logging = _logging or logging
        self.color = colorizer or DefaultColorizer()
        logging.Formatter.__init__(self, *a, **kw)

    def format(self, record):
        levelname = record.levelname
        padded_level = '%-8s' % levelname

        record.color_levelname = self.color.colorize(levelname, record)
        record.padded_color_levelname = self.color.colorize(
            padded_level,
            record
        )
        return self.logging.Formatter.format(self, record)
