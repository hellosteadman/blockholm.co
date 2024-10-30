from django.core.files import File
from django.core.files.storage import default_storage
from django.db import models
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags
from hashlib import md5
from markdown import markdown
from sidekick.contrib.notion import sync
from sidekick.contrib.notion.signals import object_synced
from sidekick.helpers import create_og_image
from sidekick.mail import render_to_inbox
from taggit.managers import TaggableManager
from tempfile import NamedTemporaryFile
from urllib.parse import urlsplit
from .managers import PostManager, SubscriberManager
from .query import BlockQuerySet
import os
import requests


class Post(models.Model):
    def upload_og_image(self, filename):
        basename = md5(
            (
                self.title + '\n' + self.get_excerpt()
            ).encode('utf-8')
        ).hexdigest()

        return 'newsletter/%s/og_%s%s' % (
            self.pk,
            basename,
            os.path.splitext(filename)[-1]
        )

    objects = PostManager()
    notion_id = models.UUIDField(
        'Notion ID',
        unique=True,
        null=True,
        blank=True,
        editable=False
    )

    author = models.ForeignKey(
        'auth.User',
        related_name='newsletter_posts',
        on_delete=models.SET_NULL,
        null=True
    )

    title = models.CharField(max_length=100)
    published = models.DateTimeField(null=True, blank=True)
    slug = models.SlugField(max_length=100, unique=True)
    status = models.CharField(max_length=30)
    subtitle = models.TextField(null=True, blank=True)
    tags = TaggableManager(
        blank=True,
        related_name='posts'
    )

    og_image = models.ImageField(
        'Open Graph image',
        upload_to=upload_og_image,
        max_length=255,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', args=(self.slug,))

    def attach(self, url):
        scheme, domain, path, query, fragment = urlsplit(url)
        baseurl = '%s://%s%s' % (scheme, domain, path)
        media = 'newsletter/%s/%s' % (
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
        ordering = ('-published',)
        get_latest_by = 'published'


class Attachment(models.Model):
    def upload_media(self, filename):
        return 'newsletter/%s/%s' % (
            self.post_id,
            self.notion_url.split('/')[-1]
        )

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='attachments'
    )

    notion_url = models.URLField('Notion URL', max_length=255, unique=True)
    media = models.FileField(max_length=255, upload_to=upload_media)
    tags = TaggableManager(
        blank=True,
        related_name='attachments'
    )

    def __str__(self):
        return self.notion_url.split('/')[-1]


class Block(models.Model):
    objects = BlockQuerySet.as_manager()
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='content'
    )

    notion_id = models.UUIDField('Notion ID', unique=True, editable=False)
    ordering = models.PositiveIntegerField(default=0)
    type = models.CharField(max_length=300)
    properties = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.type.capitalize().replace('_', ' ')

    def render(self, simple=False):
        return render_to_string(
            'newsletter/content/%s_block.html' % self.type,
            {
                **self.properties,
                'simple': simple
            }
        )

    class Meta:
        ordering = ('ordering',)


class Subscriber(models.Model):
    objects = SubscriberManager()

    notion_id = models.UUIDField(
        'Notion ID',
        unique=True,
        null=True,
        blank=True,
        editable=False
    )

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    subscribed = models.DateTimeField()
    excluded_tags = TaggableManager(
        blank=True,
        related_name='excluded_subscribers'
    )

    sent_posts = models.ManyToManyField(
        Post,
        related_name='sent_to',
        blank=True
    )

    def __str__(self):
        return self.name

    def send_digest(self):
        now = timezone.now()
        posts = Post.objects.exclude(
            pk__in=self.sent_posts.all()
        ).filter(
            published__gte=now - timezone.timedelta(days=90),
            published__lte=now
        )

        if self.excluded_tags.exists():
            posts = posts.exclude(
                tags__in=self.excluded_tags.all()
            )

        if not posts.exists():
            return

        name = 'there'
        if self.name:
            name = self.name.split()[0].capitalize()

        posts = posts.order_by('published')[:5]
        render_to_inbox(
            (self.name, self.email),
            'Your weekly digest from Notino Sidekick',
            'newsletter/digest_email.html',
            {
                'name': name,
                'object_list': posts
            },
            'Tips and templates to help you get the most out of Notion.'
        )

        self.sent_posts.add(*posts)
        sync.from_model(self)

    class Meta:
        ordering = ('-subscribed',)


@receiver(object_synced, sender=Post)
def post_synced(sender, instance, direction, **kwargs):
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
