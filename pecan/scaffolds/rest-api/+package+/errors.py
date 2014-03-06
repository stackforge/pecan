import json
import webob
from pecan.hooks import PecanHook


class JSONErrorHook(PecanHook):
    """
    A pecan hook that translates webob HTTP errors into a JSON format.
    """

    def on_error(self, state, exc):
        if isinstance(exc, webob.exc.HTTPError):
            return webob.Response(
                body=json.dumps({'reason': str(exc)}),
                status=exc.status,
                headerlist=exc.headerlist,
                content_type='application/json'
            )
