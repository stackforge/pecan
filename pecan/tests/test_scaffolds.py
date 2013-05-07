import os
import sys
import tempfile
import shutil

from six.moves import cStringIO as StringIO

from pecan.tests import PecanTestCase

if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest  # noqa


class TestPecanScaffold(PecanTestCase):

    def test_normalize_pkg_name(self):
        from pecan.scaffolds import PecanScaffold
        s = PecanScaffold()
        assert s.normalize_pkg_name('sam') == 'sam'
        assert s.normalize_pkg_name('sam1') == 'sam1'
        assert s.normalize_pkg_name('sam_') == 'sam_'
        assert s.normalize_pkg_name('Sam') == 'sam'
        assert s.normalize_pkg_name('SAM') == 'sam'
        assert s.normalize_pkg_name('sam ') == 'sam'
        assert s.normalize_pkg_name(' sam') == 'sam'
        assert s.normalize_pkg_name('sam$') == 'sam'
        assert s.normalize_pkg_name('sam-sam') == 'samsam'


class TestScaffoldUtils(PecanTestCase):

    def setUp(self):
        super(TestScaffoldUtils, self).setUp()
        self.scaffold_destination = tempfile.mkdtemp()
        self.out = sys.stdout

        sys.stdout = StringIO()

    def tearDown(self):
        shutil.rmtree(self.scaffold_destination)
        sys.stdout = self.out

    def test_copy_dir(self):
        from pecan.scaffolds import PecanScaffold

        class SimpleScaffold(PecanScaffold):
            _scaffold_dir = ('pecan', os.path.join(
                'tests', 'scaffold_fixtures', 'simple'
            ))

        SimpleScaffold().copy_to(os.path.join(
            self.scaffold_destination,
            'someapp'
        ), out_=StringIO())

        assert os.path.isfile(os.path.join(
            self.scaffold_destination, 'someapp', 'foo'
        ))
        assert os.path.isfile(os.path.join(
            self.scaffold_destination, 'someapp', 'bar', 'spam.txt'
        ))
        assert open(os.path.join(
            self.scaffold_destination, 'someapp', 'foo'
        ), 'r').read().strip() == 'YAR'
        assert open(os.path.join(
            self.scaffold_destination, 'someapp', 'foo'
        ), 'r').read().strip() == 'YAR'

    def test_destination_directory_levels_deep(self):
        from pecan.scaffolds import copy_dir
        f = StringIO()
        copy_dir(
            (
                'pecan', os.path.join('tests', 'scaffold_fixtures', 'simple')
            ),
            os.path.join(self.scaffold_destination, 'some', 'app'),
            {},
            out_=f
        )

        assert os.path.isfile(os.path.join(
            self.scaffold_destination, 'some', 'app', 'foo')
        )
        assert os.path.isfile(os.path.join(
            self.scaffold_destination, 'some', 'app', 'bar', 'spam.txt')
        )
        assert open(os.path.join(
            self.scaffold_destination, 'some', 'app', 'foo'
        ), 'r').read().strip() == 'YAR'
        assert open(os.path.join(
            self.scaffold_destination, 'some', 'app', 'bar', 'spam.txt'
        ), 'r').read().strip() == 'Pecan'

    def test_destination_directory_already_exists(self):
        from pecan.scaffolds import copy_dir
        f = StringIO()
        copy_dir(
            (
                'pecan', os.path.join('tests', 'scaffold_fixtures', 'simple')
            ),
            os.path.join(self.scaffold_destination),
            {},
            out_=f
        )
        assert 'already exists' in f.getvalue()

    def test_copy_dir_with_filename_substitution(self):
        from pecan.scaffolds import copy_dir
        copy_dir(
            (
                'pecan', os.path.join('tests', 'scaffold_fixtures', 'file_sub')
            ),
            os.path.join(
                self.scaffold_destination, 'someapp'
            ),
            {'package': 'thingy'},
            out_=StringIO()
        )

        assert os.path.isfile(os.path.join(
            self.scaffold_destination, 'someapp', 'foo_thingy')
        )
        assert os.path.isfile(os.path.join(
            self.scaffold_destination, 'someapp', 'bar_thingy', 'spam.txt')
        )
        assert open(os.path.join(
            self.scaffold_destination, 'someapp', 'foo_thingy'
        ), 'r').read().strip() == 'YAR'
        assert open(os.path.join(
            self.scaffold_destination, 'someapp', 'bar_thingy', 'spam.txt'
        ), 'r').read().strip() == 'Pecan'

    def test_copy_dir_with_file_content_substitution(self):
        from pecan.scaffolds import copy_dir
        copy_dir(
            (
                'pecan',
                os.path.join('tests', 'scaffold_fixtures', 'content_sub'),
            ),
            os.path.join(
                self.scaffold_destination, 'someapp'
            ),
            {'package': 'thingy'},
            out_=StringIO()
        )

        assert os.path.isfile(os.path.join(
            self.scaffold_destination, 'someapp', 'foo')
        )
        assert os.path.isfile(os.path.join(
            self.scaffold_destination, 'someapp', 'bar', 'spam.txt')
        )
        assert open(os.path.join(
            self.scaffold_destination, 'someapp', 'foo'
        ), 'r').read().strip() == 'YAR thingy'
        assert open(os.path.join(
            self.scaffold_destination, 'someapp', 'bar', 'spam.txt'
        ), 'r').read().strip() == 'Pecan thingy'
