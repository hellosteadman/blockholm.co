from django.utils import timezone
from django.views.generic import TemplateView
from sidekick.newsletter.forms import SubscriberForm
from sidekick.newsletter.models import Post


class IndexView(TemplateView):
    template_name = 'front/index.html'

    def get_context_data(self, **kwargs):
        posts = kwargs.get(
            'posts',
            Post.objects.filter(
                published__lte=timezone.now()
            )[:12]
        )

        return {
            **super().get_context_data(**kwargs),
            'form': kwargs.get('form', SubscriberForm()),
            'post_list': posts
        }
