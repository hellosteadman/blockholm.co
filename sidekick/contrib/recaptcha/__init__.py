from django.conf import settings
from .fields import RecaptchaField


PUBLIC_KEY = settings.RECAPTCHA['PUBLIC_KEY']
SECRET_KEY = settings.RECAPTCHA['SECRET_KEY']


__all__ = (
    'PUBLIC_KEY',
    'SECRET_KEY',
    'RecaptchaField'
)
