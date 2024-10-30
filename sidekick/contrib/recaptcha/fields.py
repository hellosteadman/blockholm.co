from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
import logging
import requests


API_URL = 'https://www.google.com/recaptcha/api/siteverify'


class RecaptchaWidget(forms.HiddenInput):
    def get_context(self, name, value, attrs):
        attrs['data-recaptcha-key'] = settings.RECAPTCHA['PUBLIC_KEY']
        context = super().get_context(name, value, attrs)
        return context


class RecaptchaField(forms.CharField):
    default_error_messages = {
        'required': (
            'I couldn\'t tell if you were a bot or not. '
            'Please try again.'
        ),
        'low_score': (
            'It looks like you might be a bot. '
            'Please try again.'
        ),
        'error': (
            'My bot-checking service encountered an error '
            'when checking your submission. Please try again.'
        )
    }

    widget = RecaptchaWidget

    def validate(self, value):
        super().validate(value)

        threshold = settings.RECAPTCHA.get('SCORE_THRESHOLD', .5)
        response = requests.post(
            API_URL,
            {
                'secret': settings.RECAPTCHA['SECRET_KEY'],
                'response': value
            }
        )

        try:
            response.raise_for_status()
        except Exception:
            logging.getLogger('recaptcha').error(
                'Error calling reCAPTCHA',
                exc_info=True
            )

            raise ValidationError(
                self.error_messages['error'],
                code='error'
            )

        response = response.json()
        print(response)

        if any(response.get('error-codes', [])):
            raise ValidationError(
                self.error_messages['error'],
                code='error'
            )

        try:
            score = response['score']
        except KeyError:
            raise ValidationError(
                self.error_messages['error'],
                code='error'
            )

        if score < threshold:
            raise ValidationError(
                self.error_messages['low_score'],
                code='low_score'
            )
