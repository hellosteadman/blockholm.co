from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from markdown import markdown
from .query import BlockQuerySet


class Block(models.Model):
    objects = BlockQuerySet.as_manager()

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    notion_id = models.UUIDField('Notion ID', unique=True, editable=False)
    ordering = models.PositiveIntegerField(default=0)
    type = models.CharField(max_length=300)
    properties = models.JSONField(default=dict, blank=True)
    word_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.type.capitalize().replace('_', ' ')

    def render(self, simple=False):
        typename = self.type
        if typename == 'video' and self.properties.get('remote'):
            typename = 'embed'

        return render_to_string(
            'notion/content/%s_block.html' % typename,
            {
                **self.properties,
                'simple': simple
            }
        )

    def save(self, *args, **kwargs):
        self.word_count = 0

        if text := self.properties.get('text'):
            text = strip_tags(markdown(text))
            self.word_count = len(text.split())

        super().save(*args, **kwargs)

    class Meta:
        ordering = ('ordering',)
