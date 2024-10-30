from django.urls import reverse
from sidekick.front.models import Page


def theme(request):
    return {
        'menus': {
            'header': [
                {
                    'label': 'Archive',
                    'url': reverse('post_list')
                }
            ],
            'footer': [
                {
                    'label': 'Archive',
                    'url': reverse('post_list')
                }
            ] + [
                {
                    'label': page.title,
                    'url': page.get_absolute_url()
                } for page in Page.objects.all()
            ] + [
                {
                    'label': 'Get Notion',
                    'bold': True,
                    'url': 'https://affiliate.notion.so/o1arb6q3quzi'
                }
            ]
        }
    }
