from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django_rq import job
from email.utils import formataddr


DEFAULT_FROM = formataddr(
    (
        settings.DEFAULT_FROM_NAME,
        settings.DEFAULT_FROM_EMAIL
    )
)


@job('default')
def send_mail(subject, recipient, plain_text, html_body):
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
