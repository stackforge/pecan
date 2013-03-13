from pecan.middleware.static import (StaticFileMiddleware, FileWrapper,
                                     _dump_date)
from pecan.tests import PecanTestCase

import os


class TestStaticFileMiddleware(PecanTestCase):

    def setUp(self):
        super(TestStaticFileMiddleware, self).setUp()

        def app(environ, start_response):
            response_headers = [('Content-type', 'text/plain')]
            start_response('200 OK', response_headers)
            return ['Hello world!\n']

        self.app = StaticFileMiddleware(
            app, os.path.dirname(__file__)
        )

        self._status = None
        self._response_headers = None

    def _request(self, path):
        def start_response(status, response_headers, exc_info=None):
            self._status = status
            self._response_headers = response_headers
        return self.app(
            dict(PATH_INFO=path),
            start_response
        )

    def _get_response_header(self, header):
        for k, v in self._response_headers:
            if k.upper() == header.upper():
                return v
        return None

    def test_file_can_be_found(self):
        result = self._request('/static_fixtures/text.txt')
        assert isinstance(result, FileWrapper)

    def test_no_file_found_causes_passthrough(self):
        result = self._request('/static_fixtures/nosuchfile.txt')
        assert not isinstance(result, FileWrapper)
        assert result == ['Hello world!\n']

    def test_mime_type_works_for_png_files(self):
        self._request('/static_fixtures/self.png')
        assert self._get_response_header('Content-Type') == 'image/png'

    def test_file_can_be_closed(self):
        result = self._request('/static_fixtures/text.txt')
        assert result.close() is None

    def test_file_can_be_iterated_over(self):
        result = self._request('/static_fixtures/text.txt')
        assert len([x for x in result])

    def test_date_dumping_on_unix_timestamps(self):
        result = _dump_date(1331755274.59, ' ')
        assert result == 'Wed, 14 Mar 2012 20:01:14 GMT'

    def test_separator_sanitization_still_finds_file(self):
        os.altsep = ':'
        result = self._request(':static_fixtures:text.txt')
        assert isinstance(result, FileWrapper)
