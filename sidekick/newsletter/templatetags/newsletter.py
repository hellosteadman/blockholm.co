from django.template import Library
from django.utils.safestring import mark_safe
from hashlib import md5
from markdown import markdown as _markdown
from urllib.parse import urlencode


register = Library()


@register.filter()
def markdown(value):
    return mark_safe(
        _markdown(value)
    )


@register.filter()
def gravatar(email, size=64):
    return 'https://secure.gravatar.com/avatar/%s?%s' % (
        md5((email or 'none@example.com').encode('utf-8')).hexdigest(),
        urlencode(
            {
                's': size * 2,
                'd': 'mp',
                'r': 'g'
            }
        )
    )
