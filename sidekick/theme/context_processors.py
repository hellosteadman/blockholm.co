from django.urls import reverse


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
                },
                {
                    'label': 'Get Notion',
                    'bold': True,
                    'url': 'https://affiliate.notion.so/o1arb6q3quzi'
                }
            ]
        }
    }
