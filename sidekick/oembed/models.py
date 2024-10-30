from bs4 import BeautifulSoup
from django.db import models
from hashlib import md5
from .query import ResourceQuerySet
import os


class Resource(models.Model):
    objects = ResourceQuerySet.as_manager()

    def upload_thumbnail(self, filename):
        return 'oembed/%s%s' % (
            md5(self.url.encode('utf-8')).hexdigest(),
            os.path.splitext(filename)[-1]
        )

    url = models.URLField('URL', max_length=255, unique=True)
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    html = models.TextField('HTML', null=True, blank=True)
    thumbnail = models.ImageField(
        max_length=255,
        null=True,
        blank=True,
        upload_to=upload_thumbnail
    )

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.url

    def save(self, *args, **kwargs):
        if not self.width:
            self.height = 0

            soup = BeautifulSoup(
                '<html>%s</html>' % self.html,
                'html.parser'
            )

            for iframe in soup.find_all('iframe'):
                if width := iframe.get('width'):
                    try:
                        self.width = int(width)
                    except ValueError:
                        self.width = 0

                if height := iframe.get('height'):
                    try:
                        self.height = int(height)
                    except ValueError:
                        pass

                    break

                if self.width and self.height:
                    break

        if self.width and not self.height:
            self.height = self.width / 16 * 9

        super().save(*args, **kwargs)

    @property
    def iframe_url(self):
        soup = BeautifulSoup(
            '<html>%s</html>' % self.html,
            'html.parser'
        )

        for iframe in soup.find_all('iframe'):
            if url := iframe.get('src'):
                return url

        return self.url

    class Meta:
        ordering = ('-created',)
        get_latest_by = 'created'
