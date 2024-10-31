from django.core.files.storage import default_storage
from django.template import Library
from django.template.loader import render_to_string
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

    return render_to_string(
        'notion/video_player.html',
        {
            'src': default_storage.url(src),
            'poster': default_storage.url(poster)
        }
    )
