from django.template import Library
from .. import get_html


register = Library()


@register.filter()
def oembed(value, width=None):
    kwargs = {}

    if width is not None:
        kwargs['width'] = width

    return get_html(value, **kwargs)


@register.filter()
def oembed_strict(value, width=None):
    kwargs = {
        'discover': False,
        'strict': True
    }

    if width is not None:
        kwargs['width'] = width

    return get_html(value, **kwargs)
