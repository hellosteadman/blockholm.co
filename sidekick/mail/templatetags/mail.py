from django.conf import settings
from django.template import Library
from urllib.parse import urljoin as _urljoin


register = Library()


@register.filter()
def urljoin(value, base=None):
    if base is None:
        base = 'http%s://%s/' % (
            not settings.DEBUG and 's' or '',
            settings.DOMAIN
        )

    return _urljoin(base, value)
