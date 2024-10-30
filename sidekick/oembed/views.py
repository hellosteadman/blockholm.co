from django.http.response import HttpResponse
from django.conf import settings
from django.views.generic import View
from .helpers import get_html
import json
import jwt


class ResourceView(View):
    def get(self, request, token):
        try:
            decoded = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=('HS256',)
            )

            url = decoded['u']
            discover = decoded['d']
        except Exception:
            return HttpResponse(
                json.dumps(
                    {
                        'error': 'Invalid token'
                    }
                ),
                content_type='application/json',
                status=400
            )

        try:
            html = get_html(url, discover=discover)
            return HttpResponse(
                json.dumps(
                    {
                        'html': html
                    }
                ),
                content_type='application/json'
            )
        except Exception as ex:
            return HttpResponse(
                json.dumps(
                    {
                        'error': str(ex.args[0])
                    }
                ),
                content_type='application/json',
                status=500
            )
