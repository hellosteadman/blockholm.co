from django.core.files.storage import default_storage
from django.template import Library
from django.utils.html import format_html
from sidekick.contrib.notion.helpers import create_poster
import os


register = Library()


@register.filter
def video(src):
    basename, ext = os.path.splitext(src)
    poster = '%s.poster.png' % basename

    if not default_storage.exists(poster):
        dest = create_poster(
            default_storage.path(src)
        )

        try:
            default_storage.save(
                poster,
                open(dest, 'rb')
            )
        finally:
            os.remove(dest)

    return format_html(
        '<video src="{}" poster="{}" controls></video>',
        default_storage.url(src),
        default_storage.url(poster)
    )
