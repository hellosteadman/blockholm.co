from django.conf import settings
from django.contrib import admin
from django.urls import path, re_path, include
from sidekick.seo.views import RobotsTxtView
from . import sitemaps


urlpatterns = [
    path('admin/', admin.site.urls),
    path('robots.txt', RobotsTxtView.as_view(), name='robots_txt'),
    path('', include('sidekick.newsletter.urls')),
    path('', include(sitemaps))
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
