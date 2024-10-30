from django.contrib.sitemaps.views import sitemap, index
from django.urls import path
from .newsletter.sitemaps import PostSitemap


sitemaps = {
    'newsletter': PostSitemap
}

urlpatterns = [
    path(
        'sitemap.xml',
        index,
        {
            'sitemaps': sitemaps
        },
        name='django.contrib.sitemaps.views.index'
    ),
    path(
        'sitemap-<section>.xml',
        sitemap,
        {
            'sitemaps': sitemaps
        },
        name='django.contrib.sitemaps.views.sitemap'
    )
]
