from django.urls import path
from .views import (
    PostListView, PostDetailView,
    CreateSubscriberView, SubscriberCreatedView, SubscriberUpdatedView,
    EmailPreview
)


urlpatterns = (
    path('posts/', PostListView.as_view(), name='post_list'),
    path('posts/<slug:slug>/', PostDetailView.as_view(), name='post_detail'),
    path('subscribe/', CreateSubscriberView.as_view(), name='create_subscriber'),  # NOQA
    path('subscribed/', SubscriberCreatedView.as_view(), name='subscriber_created'),  # NOQA
    path('updated/', SubscriberUpdatedView.as_view(), name='subscriber_updated'),  # NOQA
    path('~/preview/', EmailPreview.as_view())
)
