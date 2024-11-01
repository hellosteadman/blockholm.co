from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage as static
from django.utils import timezone
from django.views.generic import TemplateView, DetailView
from sidekick.newsletter.forms import SubscriberForm
from sidekick.newsletter.models import Post
from sidekick.seo.views import (
    SEOMixin,
    OpenGraphMixin,
    OpenGraphArticleMixin,
    LinkedDataMixin
)

from .models import Page


class IndexView(SEOMixin, OpenGraphMixin, LinkedDataMixin, TemplateView):
    template_name = 'front/index.html'
    seo_title = 'Blockholm'
    seo_description = 'Notion blog and newsletter with tips and templates'
    og_type = 'website'
    og_title = 'Blockholm'
    og_description = (
        'Weekly tips and templates to help you get the most from Notion.'
    )

    ld_type = 'WebSite'
    ld_attributes = {
        'name': 'Blockholm',
        'publisher': {
            '@type': 'Person',
            'name': 'Mark Steadman',
            'givenName': 'Mark',
            'familyName': 'Steadman',
            'url': 'https://hellosteadman.com/',
            'image': {
                '@type': 'imageObject',
                'url': static.url('img/mark.jpg'),
                'width': 400,
                'height': 400
            },
            'contactPoint': {
                '@type': 'ContactPoint',
                'email': settings.DEFAULT_REPLYTO_EMAIL,
                'url': 'https://hellosteadman.com/',
                'contactType': 'customer service'
            },
            'sameAs': [
                'https://mastodon.social/@hellosteadman',
                'https://twitter.com/hellosteadman',
                'https://www.linkedin.com/in/hellosteadman/'
            ]
        },
        'copyrightNotice': '\u00a9 Hello Steadman Ltd',
        'copyrightYear': '2024'
    }

    def get_context_data(self, **kwargs):
        posts = kwargs.get(
            'posts',
            Post.objects.filter(
                published__lte=timezone.now(),
                status__iexact='published'
            )[:12]
        )

        return {
            **super().get_context_data(**kwargs),
            'form': kwargs.get('form', SubscriberForm()),
            'post_list': posts
        }


class PageDetailView(
    SEOMixin, LinkedDataMixin, OpenGraphArticleMixin, DetailView
):
    model = Page
    ld_type = 'WebPage'

    def get_og_description(self):
        return self.get_object().get_excerpt()

    def get_ld_attributes(self):
        obj = self.get_object()
        return {
            'headline': obj.title,
            'inLanguage': 'en-gb',
            'url': self.request.build_absolute_uri(
                obj.get_absolute_url()
            ),
            'description': obj.get_excerpt()
        }
