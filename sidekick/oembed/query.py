from django.core.files.storage import default_storage
from django.db import models, transaction
from django.template import Template, Context
from hashlib import md5
from tempfile import mkstemp
from . import settings, utils
import logging
import os
import re
import requests
import time


def handle_thumbnail(resource_url, embedded_url, width, height):
    for provider in settings.EMBED_PROVIDERS:
        if not (thumbnail := provider.get('thumbnail', {})):
            continue

        for pattern in provider['patterns']:
            compiled = re.compile(pattern)
            match = compiled.match(resource_url)

            if match is not None:
                groups = match.groups()
                if isinstance(thumbnail, str):
                    thumbnail_template = Template(thumbnail)
                    thumbnail_url = thumbnail_template.render(
                        Context(
                            {
                                'url': resource_url,
                                'params': groups
                            }
                        )
                    )

                    while True:
                        try:
                            response = requests.get(
                                thumbnail_url,
                                stream=True
                            )
                        except Exception:
                            logging.warning(
                                'Error taking thumbnail',
                                exc_info=True
                            )
                        else:
                            if response.status_code < 500:
                                response.raise_for_status()
                                break
                            else:
                                print(
                                    'Received %d error; waiting 5 seconds' % (
                                        response.status_code
                                    )
                                )

                        time.sleep(5)

                    handle, filename = mkstemp('.jpg')

                    try:
                        for chunk in response.iter_content(chunk_size=1024*1024):
                            os.write(handle, chunk)
                    finally:
                        os.close(handle)

                    image_filename = 'oembed/%s.jpg' % md5(
                        thumbnail_url.encode('utf-8')
                    ).hexdigest()

                    default_storage.save(
                        image_filename,
                        open(filename, 'rb')
                    )

                    return image_filename

    return utils.get_thumbnail(
        embedded_url,
        width,
        height
    )


class ResourceQuerySet(models.QuerySet):
    @transaction.atomic
    def get_or_discover(
        self, url, width=696, discover=True, get_thumbnail=False
    ):
        kwargs = {
            'url': url
        }

        if width is not None:
            kwargs['width'] = width

        while any(kwargs):
            for obj in self.select_for_update().filter(**kwargs):
                if get_thumbnail and not obj.thumbnail:
                    obj.thumbnail = handle_thumbnail(
                        url,
                        obj.iframe_url,
                        obj.width,
                        obj.height or ((obj.width or 720) / 16 * 9)
                    )

                    if obj.thumbnail:
                        obj.save()

                return obj

            if 'width' in kwargs:
                del kwargs['width']
                continue

            del kwargs['url']

        for provider in settings.EMBED_PROVIDERS:
            ratio = provider.get('ratio') or [16, 9]
            ratio = int(ratio[0]) / int(ratio[1])

            for pattern in provider['patterns']:
                compiled = re.compile(pattern)
                match = compiled.match(url)

                if match is not None:
                    groups = match.groups()
                    context = Context(
                        {
                            'url': url,
                            'width': width,
                            'height': width and int(width / ratio) or 405,
                            'params': groups
                        }
                    )

                    template = Template(provider['html'])
                    html = template.render(context)
                    obj = self.create(url=url, html=html)

                    if get_thumbnail:
                        obj.thumbnail = handle_thumbnail(
                            url,
                            obj.iframe_url,
                            obj.width,
                            obj.height or ((obj.width or 720) / 16 * 9)
                        )

                        if obj.thumbnail:
                            obj.save()

                    return obj

        if discover and (html := utils.discover_html(url)):
            obj = self.create(url=url, html=html)

            if get_thumbnail:
                obj.thumbnail = handle_thumbnail(
                    url,
                    obj.iframe_url,
                    obj.width,
                    obj.height or ((obj.width or 720) / 16 * 9)
                )

                if obj.thumbnail:
                    obj.save()

            return obj
