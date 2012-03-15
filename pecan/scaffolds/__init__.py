import sys
import os
import re
import pkg_resources
from string import Template
from pecan.compat import native_, bytes_

DEFAULT_SCAFFOLD = 'base'
_bad_chars_re = re.compile('[^a-zA-Z0-9_]')


class PecanScaffold(object):

    def copy_to(self, dest, **kwargs):
        output_dir = os.path.abspath(os.path.normpath(dest))
        pkg_name = _bad_chars_re.sub('', dest.lower())
        copy_dir(self._scaffold_dir, output_dir, {'package': pkg_name})


class BaseScaffold(PecanScaffold):
    _scaffold_dir = ('pecan', os.path.join('scaffolds', 'base'))


def copy_dir(source, dest, variables, out_=sys.stdout, i=0):
    """
    Copies the ``source`` directory to the ``dest`` directory, where
    ``source`` is some tuple representing an installed package and a
    subdirectory, e.g.,

    ('pecan', os.path.join('scaffolds', 'base'))
    ('pecan_sqlalchemy', os.path.join('scaffolds', 'sqlalchemy'))

    ``variables``: A dictionary of variables to use in any substitutions.

    ``out_``: File object to write to
    """
    def out(msg):
        out_.write('%s%s' % (' ' * (i * 2), msg))
        out_.write('\n')
        out_.flush()

    names = sorted(pkg_resources.resource_listdir(source[0], source[1]))
    if not os.path.exists(dest):
        out('Creating %s' % dest)
        makedirs(dest)
    else:
        out('%s already exists' % dest)
        return

    for name in names:

        full = '/'.join([source[1], name])
        dest_full = os.path.join(dest, substitute_filename(name, variables))

        sub_file = False
        if dest_full.endswith('_tmpl'):
            dest_full = dest_full[:-5]
            sub_file = True

        if pkg_resources.resource_isdir(source[0], full):
            out('Recursing into %s' % os.path.basename(full))
            copy_dir((source[0], full), dest_full, variables, out_, i + 1)
            continue
        else:
            content = pkg_resources.resource_string(source[0], full)

        if sub_file:
            content = render_template(content, variables)
            if content is None:
                continue  # pragma: no cover

        out('Copying %s to %s' % (full, dest_full))

        f = open(dest_full, 'wb')
        f.write(content)
        f.close()


def makedirs(directory):
    parent = os.path.dirname(os.path.abspath(directory))
    if not os.path.exists(parent):
        makedirs(parent)
    os.mkdir(directory)


def substitute_filename(fn, variables):
    for var, value in variables.items():
        fn = fn.replace('+%s+' % var, str(value))
    return fn


def render_template(content, variables):
    """ Return a bytestring representing a templated file based on the
    input (content) and the variable names defined (vars)."""
    fsenc = sys.getfilesystemencoding()
    content = native_(content, fsenc)
    return bytes_(Template(content).substitute(variables), fsenc)
