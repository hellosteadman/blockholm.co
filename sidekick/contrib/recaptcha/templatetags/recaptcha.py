from django.template import Library
from .. import PUBLIC_KEY


register = Library()


@register.inclusion_tag('recaptcha/script.html')
def recaptcha_script():
    return {
        'key': PUBLIC_KEY
    }
