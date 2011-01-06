import cgi
import os
import string
import sys
import urllib

class LaxTemplate(string.Template):
    # This change of pattern allows for anything in braces, but
    # only identifiers outside of braces:
    pattern = r"""
    \$(?:
      (?P<escaped>\$)             |   # Escape sequence of two delimiters
      (?P<named>[_a-z][_a-z0-9]*) |   # delimiter and a Python identifier
      {(?P<braced>.*?)}           |   # delimiter and a braced identifier
      (?P<invalid>)                   # Other ill-formed delimiter exprs
    )
    """


class TypeMapper(dict):
    def __getitem__(self, item):
        options = item.split('|')
        for op in options[:-1]:
            try:
                value = eval(op, dict(self.items()))
                break
            except (NameError, KeyError):
                pass
            except Exception, ex:
                TemplateProcessor.add_exception_info(ex, 'in expression %r' % op)
                raise
        else:
            value = eval(options[-1], dict(self.items()))
        if value is None:
            return ''
        else:
            return str(value)


class TemplateProcessor(object):

    def __init__(self, vars, verbosity=0, overwrite=False):
        self.vars = vars.copy()
        self.vars.setdefault('dot', '.')
        self.vars.setdefault('plus', '+')
        self.verbosity = verbosity
        self.overwrite = overwrite
        self.standard_vars = self._create_standard_vars(vars)
    
    def process(self, template, output_dir, indent=0):
        self._process_directory(template.template_directory, output_dir, indent=indent)
    
    def _create_standard_vars(self, extra_vars={}):
        
        # method to skip a template file
        def skip_file(condition=True, *args):
            if condition:
                raise SkipFileException(*args)
        
        # build the dictionary of standard vars
        standard_vars = {
            'nothing': None,
            'html_quote': lambda s: s is None and '' or cgi.escape(str(s), 1),
            'url_quote': lambda s: s is None and '' or urllib.quote(str(s)),
            'empty': '""',
            'test': lambda check, true, false=None: check and true or false,
            'repr': repr,
            'str': str,
            'bool': bool,
            'SkipFileException': SkipFileException,
            'skip_file': skip_file,
        }
        
        # add in the extra vars
        standard_vars.update(extra_vars)
        
        return standard_vars
    
    def _process_directory(self, source, dest, indent=0):
        
        # determine the output padding
        pad = ' ' * (indent * 2)
        
        # create the destination directory
        if not os.path.exists(dest):
            if self.verbosity >= 1:
                print '%sCreating %s/' % (pad, dest)
            self._create_directory_tree(dest)
        elif self.verbosity >= 2:
            print '%sDirectory %s exists' % (pad, dest)
        
        # step through the source files/directories
        for name in sorted(os.listdir(source)):
            
            # get the full path
            full = os.path.join(source, name)
            
            # check if the file should be skipped
            reason = self._should_skip_file(name)
            if reason:
                if self.verbosity >= 2:
                    print pad + reason % {'filename': full}
                continue
            
            # get the destination filename
            dest_full = os.path.join(dest, self._substitute_filename(name))
            
            # if a directory, recurse
            if os.path.isdir(full):
                if self.verbosity:
                    print '%sRecursing into %s' % (pad, os.path.basename(full))
                self._process_directory(full, dest_full, indent=indent + 1)
                continue
            
            # check if we should substitute content
            sub_file = False
            if dest_full.endswith('_tmpl'):
                dest_full = dest_full[:-5]
                sub_file = True
            
            # read the file contents 
            f = open(full, 'rb')
            content = f.read()
            f.close()
            
            # perform the substitution
            if sub_file:
                try:
                    content = self._substitute_content(content, full)
                except SkipFileException:
                    continue
                if content is None:
                    continue
            
            # check if the file already exists
            already_exists = os.path.exists(dest_full)
            if already_exists:
                f = open(dest_full, 'rb')
                old_content = f.read()
                f.close()
                if old_content == content:
                    if self.verbosity:
                        print '%s%s already exists (same content)' % (pad, dest_full)
                    continue
                if not self.overwrite:
                    continue
            
            # write out the new file
            if self.verbosity:
                print '%sCopying %s to %s' % (pad, os.path.basename(full), dest_full)
            f = open(dest_full, 'wb')
            f.write(content)
            f.close()

    def _should_skip_file(self, name):
        """
        Checks if a file should be skipped based on its name.

        If it should be skipped, returns the reason, otherwise returns
        None.
        """
        if name.startswith('.'):
            return 'Skipping hidden file %(filename)s'
        if name.endswith('~') or name.endswith('.bak'):
            return 'Skipping backup file %(filename)s'
        if name.endswith('.pyc'):
            return 'Skipping .pyc file %(filename)s'
        if name.endswith('$py.class'):
            return 'Skipping $py.class file %(filename)s'
        if name in ('CVS', '_darcs'):
            return 'Skipping version control directory %(filename)s'
        return None

    def _create_directory_tree(self, dir):
        parent = os.path.dirname(os.path.abspath(dir))
        if not os.path.exists(parent):
            self._create_directory_tree(parent)
        os.mkdir(dir)
    
    def _substitute_filename(self, fn):
        for var, value in self.vars.items():
            fn = fn.replace('+%s+' % var, str(value))
        return fn
    
    def _substitute_content(self, content, filename):
        tmpl = LaxTemplate(content)
        try:
            return tmpl.substitute(TypeMapper(self.standard_vars.copy()))
        except Exception, ex:
            TemplateProcessor.add_exception_info(ex, ' in file %s' % filename)
            raise
    
    @staticmethod
    def add_exception_info(exc, info):
        if not hasattr(exc, 'args') or exc.args is None:
            return
        args = list(exc.args)
        if args:
            args[0] += ' ' + info
        else:
            args = [info]
        exc.args = tuple(args)


class SkipFileException(Exception):
    """
    Raised to indicate that the file should not be copied over.
    Raise this exception during the substitution of your file.
    """
    pass


class Template(object):
    
    # template information
    summary = ''
    
    @property
    def module_directory(self):
        module = sys.modules[self.__class__.__module__]
        return os.path.dirname(module.__file__)
    
    @property
    def template_directory(self):
        if getattr(self, 'directory', None) is None:
            raise Exception('Template "%s" did not set directory' % self.name)
        return os.path.join(self.module_directory, self.directory)
    
    def run(self, output_dir, vars, **options):
        self.pre(output_dir, vars, **options)
        self.write_files(output_dir, vars, **options)
        self.post(output_dir, vars, **options)
    
    def pre(self, output_dir, vars, **options):
        pass

    def write_files(self, output_dir, vars, **options):
        processor = TemplateProcessor(vars, options.get('verbosity', 0), 
                                      options.get('overwrite', False))
        processor.process(self, output_dir, indent=1)
    
    def post(self, output_dir, vars, **options):
        pass
        
    @classmethod
    def get_templates(cls, parent=None):
        templates = {}
        if not parent:
            parent = cls
        for template in parent.__subclasses__():
            if hasattr(template, 'name'):
                templates[template.name] = template
            templates.update(cls.get_templates(template))
        return templates


class DefaultTemplate(Template):
    
    # template information
    name = 'default'
    summary = 'Template for creating a basic Pecan package'
    directory = 'project'
