from django.conf import settings
from django.contrib import admin
from django.http.response import JsonResponse
from django.urls import path, re_path, include
from django.utils import timezone
from django.views.generic import TemplateView, View
from sidekick.seo.views import RobotsTxtView
from . import sitemaps


LOADED = timezone.now()


class ReadyView(View):
    def get(self, request):
        return JsonResponse(
            {
                'uptime': int(
                    (timezone.now() - LOADED).total_seconds()
                )
            }
        )


urlpatterns = [
    path('admin/rq/', include('django_rq.urls')),
    path('admin/', admin.site.urls),
    path('robots.txt', RobotsTxtView.as_view(), name='robots_txt'),
    path('', include('sidekick.newsletter.urls')),
    path('', include(sitemaps)),
    path('~/ready/', ReadyView.as_view())
]

if settings.DEBUG:
    from django.views.static import serve as static_serve

    urlpatterns += (
        re_path(
            r'^media/(?P<path>.*)$',
            static_serve,
            {
                'document_root': settings.MEDIA_ROOT
            }
        ),
    )


urlpatterns += (
    path('', include('sidekick.front.urls')),
)
