from django.conf import settings
from django.template.loader import render_to_string
from email.utils import formataddr
from .tasks import send_mail


def render_to_inbox(recipient, subject, template, context, plain_text=''):
    html_body = render_to_string(
        template,
        {
            'BASE_URL': 'http%s://%s' % (
                not settings.DEBUG and 's' or '',
                settings.DOMAIN
            ),
            'preferences_url': '#',
            'unsubscribe_url': '#',
            **context
        }
    )

    if isinstance(recipient, (list, tuple)) and len(recipient) == 2:
        if recipient[0]:
            recipient = formataddr(recipient)
        else:
            recipient = recipient[1]

    send_mail.delay(subject, recipient, plain_text, html_body)
