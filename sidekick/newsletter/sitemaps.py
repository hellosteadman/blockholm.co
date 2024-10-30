from django.contrib.sitemaps import Sitemap
from django.utils import timezone
from .models import Post


class PostSitemap(Sitemap):
    changefreq = 'monthly'
    priority = .6

    def items(self):
        return Post.objects.filter(
            published__lte=timezone.now(),
            status__iexact='published'
        )

    def lastmod(self, obj):
        return obj.published
