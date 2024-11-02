from django.urls import path
from webmention.middleware import include_webmention_information as webmention
from .feeds import PostFeed
from .views import (
    PostListView, PostDetailView,
    CreateSubscriberView, SubscriberCreatedView, SubscriberUpdatedView,
    ConfirmSubscriberView, SubscriberConfirmedView,
    UpdateSubscriberView, UnsubscribeView, UnsubscribedView,
    EmailPreview
)


urlpatterns = (
    path('posts/', PostListView.as_view(), name='post_list'),
    path('posts/feed/', PostFeed(), name='post_feed'),
    path(
        'posts/<slug:slug>/',
        webmention(PostDetailView.as_view()),
        name='post_detail'
    ),
    path('subscribe/', CreateSubscriberView.as_view(), name='create_subscriber'),  # NOQA
    path('subscribe/confirmed/', SubscriberConfirmedView.as_view(), name='subscriber_confirmed'),  # NOQA
    path('subscribe/<token>/', ConfirmSubscriberView.as_view(), name='confirm_subscriber'),  # NOQA
    path('subscribed/', SubscriberCreatedView.as_view(), name='subscriber_created'),  # NOQA
    path('update/<token>/', UpdateSubscriberView.as_view(), name='update_subscriber'),  # NOQA
    path('updated/', SubscriberUpdatedView.as_view(), name='subscriber_updated'),  # NOQA
    path('unsubscribe/<token>/', UnsubscribeView.as_view(), name='unsubscribe'),  # NOQA
    path('unsubscribed/', UnsubscribedView.as_view(), name='unsubscribed'),  # NOQA
    path('~/preview/', EmailPreview.as_view())
)
