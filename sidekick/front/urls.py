from django.urls import path
from .views import IndexView, PageDetailView


urlpatterns = (
    path('', IndexView.as_view(), name='index'),
    path('<slug:slug>/', PageDetailView.as_view(), name='page_detail')
)
