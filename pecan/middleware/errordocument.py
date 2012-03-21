from recursive import ForwardRequestException


class ErrorDocumentMiddleware(object):

    def __init__(self, app, error_map):
        self.app = app
        self.error_map = error_map

    def __call__(self, environ, start_response):

        def replacement_start_response(status, headers, exc_info=None):
            try:
                status_code = status.split(' ')[0]
            except ValueError, TypeError:
                raise Exception((
                    'ErrorDocumentMiddleware received an invalid '
                    'status %s' % status
                ))

            if status_code in self.error_map:
                raise ForwardRequestException(self.error_map[status_code])

            return start_response(status, headers, exc_info)

        app_iter = self.app(environ, replacement_start_response)
        return app_iter
