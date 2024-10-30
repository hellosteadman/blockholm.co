from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from email.utils import formataddr


DEFAULT_FROM = formataddr(
    (
        settings.DEFAULT_FROM_NAME,
        settings.DEFAULT_FROM_EMAIL
    )
)


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

    message = EmailMultiAlternatives(
        subject,
        plain_text,
        DEFAULT_FROM,
        [recipient],
        headers={
            'Reply-To': settings.DEFAULT_REPLYTO_EMAIL
        }
    )

    message.attach_alternative(html_body, 'text/html')
    message.send()
