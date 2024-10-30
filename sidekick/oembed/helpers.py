from django.utils.html import format_html
from django.utils.safestring import mark_safe


def get_html(
    url, width=696, height=392, format='full', discover=True, strict=False
):
    from .models import Resource

    if obj := Resource.objects.get_or_discover(
        url,
        width=width,
        discover=discover and not strict,
        get_thumbnail=format in ('simple', 'feed')
    ):
        if format == 'full':
            return mark_safe(obj.html)

        if format in ('simple', 'feed') and obj.thumbnail:
            return format_html(
                '<a href="{}"><img alt="{}" src="{}"></a>',
                url,
                'Resource thumbnail',
                obj.thumbnail.url
            )

    if not strict:
        return format_html(
            '<iframe src="{}" frameborder="0" width="100%"></iframe>',
            url
        )
