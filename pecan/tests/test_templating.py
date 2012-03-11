from unittest import TestCase

from pecan.templating import RendererFactory, format_line_context

import tempfile


class TestTemplate(TestCase):
    def setUp(self):
        self.rf = RendererFactory()

    def test_available(self):
        self.assertTrue(self.rf.available('json'))
        self.assertFalse(self.rf.available('badrenderer'))

    def test_create_bad(self):
        self.assertEqual(self.rf.get('doesnotexist', '/'), None)

    def test_extra_vars(self):
        extra_vars = self.rf.extra_vars
        self.assertEqual(extra_vars.make_ns({}), {})

        extra_vars.update({'foo': 1})
        self.assertEqual(extra_vars.make_ns({}), {'foo': 1})

    def test_update_extra_vars(self):
        extra_vars = self.rf.extra_vars
        extra_vars.update({'foo': 1})

        self.assertEqual(extra_vars.make_ns({'bar': 2}), {'foo': 1, 'bar': 2})
        self.assertEqual(extra_vars.make_ns({'foo': 2}), {'foo': 2})


class TestTemplateLineFormat(TestCase):

    def setUp(self):
        self.f = tempfile.NamedTemporaryFile()

    def tearDown(self):
        del self.f

    def test_format_line_context(self):
        for i in range(11):
            self.f.write('Testing Line %d\n' % i)
        self.f.flush()

        assert format_line_context(self.f.name, 0).count('Testing Line') == 10
