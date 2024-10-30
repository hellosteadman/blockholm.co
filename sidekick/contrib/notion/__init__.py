from django.conf import settings
from types import SimpleNamespace


settings = SimpleNamespace(**settings.NOTION)
