from django.contrib.contenttypes.fields import GenericRelation
from django.core.files import File
from django.core.files.storage import default_storage
from django.db import models
from django.dispatch import receiver
from django.urls import reverse
from django.utils.html import strip_tags
from hashlib import md5
from markdown import markdown
from sidekick.contrib.notion.models import Block
from sidekick.contrib.notion.signals import object_synced
from sidekick.helpers import create_og_image
from taggit.managers import TaggableManager
from tempfile import NamedTemporaryFile
from urllib.parse import urlsplit
from .managers import PageManager
import os
import requests


class Page(models.Model):
    def upload_og_image(self, filename):
        basename = md5(
            (
                self.title + '\n' + self.get_excerpt()
            ).encode('utf-8')
        ).hexdigest()

        return 'pages/%s/og_%s%s' % (
            self.pk,
            basename,
            os.path.splitext(filename)[-1]
        )

    objects = PageManager()
    notion_id = models.UUIDField(
        'Notion ID',
        unique=True,
        null=True,
        blank=True,
        editable=False
    )

    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    status = models.CharField(max_length=30)
    subtitle = models.TextField(null=True, blank=True)
    og_image = models.ImageField(
        'Open Graph image',
        upload_to=upload_og_image,
        max_length=255,
        null=True,
        blank=True
    )

    main_menu = models.BooleanField(default=False)
    ordering = models.PositiveIntegerField(default=0)
    content = GenericRelation(Block)

    def __str__(self):
        if self.pk and self.content.exists():
            block = self.content.first()

            if block.type == 'heading_1':
                return block.properties['text']

        return self.title

    @property
    def body_content(self):
        if self.pk and self.content.exists():
            block = self.content.first()

            if block.type == 'heading_1':
                return self.content.all()[1:]

        return self.content

    def get_absolute_url(self):
        return reverse('page_detail', args=(self.slug,))

    def attach(self, url):
        scheme, domain, path, query, fragment = urlsplit(url)
        baseurl = '%s://%s%s' % (scheme, domain, path)
        media = 'pages/%s/%s' % (
            self.pk,
            baseurl.split('/')[-1]
        )

        if default_storage.exists(media):
            return media

        for attachment in self.attachments.filter(
            notion_url=baseurl
        ):
            if default_storage.exists(attachment.media.name):
                return attachment.media.name

            attachment.delete()

        response = requests.get(url)
        response.raise_for_status()

        with NamedTemporaryFile(
            suffix=os.path.splitext(path)[-1]
        ) as temp:
            temp.write(response.content)
            temp.seek(0)

            attachment = self.attachments.create(
                notion_url=baseurl,
                media=File(temp)
            )

            return attachment.media.name

    def get_excerpt(self):
        if self.subtitle:
            return self.subtitle

        text = ''
        for block in self.content.filter(type='paragraph'):
            if block_text := block.properties.get('text'):
                text += ' ' + block_text
                if len(text) > 200:
                    break

        return strip_tags(markdown(text.strip()))

    class Meta:
        ordering = ('ordering',)


class Attachment(models.Model):
    def upload_media(self, filename):
        return 'pages/%s/%s' % (
            self.page_id,
            self.notion_url.split('/')[-1]
        )

    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name='attachments'
    )

    notion_url = models.URLField('Notion URL', max_length=512, unique=True)
    media = models.FileField(max_length=255, upload_to=upload_media)
    tags = TaggableManager(
        blank=True,
        related_name='page_attachments'
    )

    def __str__(self):
        return self.notion_url.split('/')[-1]


@receiver(object_synced, sender=Page)
def page_synced(sender, instance, direction, **kwargs):
    if direction == 'up':
        return

    imgname = instance.upload_og_image('image.png')
    if instance.og_image and imgname == instance.og_image.name:
        return

    img = create_og_image(
        instance.title,
        instance.get_excerpt()
    )

    instance.og_image = File(
        open(img, 'rb')
    )

    instance.save()
