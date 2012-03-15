import sys
import os
import pkg_resources
from string import Template
from pecan.compat import native_, bytes_

DEFAULT_SCAFFOLD = 'base'


class PecanScaffold(object):

    @property
    def template_dir(self):
        if isinstance(self._scaffold_dir, tuple):
            return self._scaffold_dir
        else:
            return os.path.join(self.module_dir, self._scaffold_dir)

    @property
    def module_dir(self):
        mod = sys.modules[self.__class__.__module__]
        return os.path.dirname(mod.__file__)

    @property
    def variables(self):
        return {
            'package': self.dest
        }

    def copy_to(self, dest, **kwargs):
        self.dest = dest
        copy_dir(self.template_dir, self.dest, self.variables)


class BaseScaffold(PecanScaffold):
    _scaffold_dir = 'base'


def copy_dir(source, dest, variables, out_=sys.stdout):
    """
    Copies the ``source`` directory to the ``dest`` directory.

    ``variables``: A dictionary of variables to use in any substitutions.

    ``out_``: File object to write to
    """
    def out(msg):
        out_.write(msg)
        out_.write('\n')
        out_.flush()

    use_pkg_resources = isinstance(source, tuple)

    if use_pkg_resources:
        names = sorted(pkg_resources.resource_listdir(source[0], source[1]))
    else:
        names = sorted(os.listdir(source))
    if not os.path.exists(dest):
        out('Creating %s' % dest)
        makedirs(dest)
    else:
        out('Directory %s already exists' % dest)
        return

    for name in names:

        if use_pkg_resources:
            full = '/'.join([source[1], name])
        else:
            full = os.path.join(source, name)

        dest_full = os.path.join(dest, substitute_filename(name, variables))

        sub_file = False
        if dest_full.endswith('_tmpl'):
            dest_full = dest_full[:-5]
            sub_file = True

        if use_pkg_resources and pkg_resources.resource_isdir(source[0], full):
            out('Recursing into %s' % os.path.basename(full))
            copy_dir((source[0], full), dest_full, variables, out_)
            continue
        elif not use_pkg_resources and os.path.isdir(full):
            out('Recursing into %s' % os.path.basename(full))
            copy_dir(full, dest_full, variables, out_)
            continue
        elif use_pkg_resources:
            content = pkg_resources.resource_string(source[0], full)
        else:
            f = open(full, 'rb')
            content = f.read()
            f.close()

        if sub_file:
            content = render_template(content, variables)
            if content is None:
                continue  # pragma: no cover

        if use_pkg_resources:
            out('Copying %s to %s' % (full, dest_full))
        else:
            out('Copying %s to %s' % (
                os.path.basename(full),
                dest_full)
            )

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
