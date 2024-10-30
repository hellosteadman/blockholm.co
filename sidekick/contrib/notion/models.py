from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.template.loader import render_to_string
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

    def __str__(self):
        return self.type.capitalize().replace('_', ' ')

    def render(self, simple=False):
        return render_to_string(
            'notion/content/%s_block.html' % self.type,
            {
                **self.properties,
                'simple': simple
            }
        )

    class Meta:
        ordering = ('ordering',)
