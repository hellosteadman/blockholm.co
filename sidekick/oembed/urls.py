from django.urls import path
from .views import ResourceView


urlpatterns = (
    path('oembed/<token>/', ResourceView.as_view(), name='oembed_resource'),
)
