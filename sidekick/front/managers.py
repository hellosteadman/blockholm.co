from django.db.models import Manager
from django.utils.text import slugify
from sidekick.contrib.notion import sync as notion_sync


class PageManager(Manager):
    def sync(self):
        def clean(obj, doc):
            if not obj.slug:
                obj.slug = slugify(obj.title)

            if not obj.status:
                obj.status = 'draft'

        return notion_sync.to_model(
            self.model,
            before_clean=clean,
            blocks_field='content',
            media_handler='attach'
        )
