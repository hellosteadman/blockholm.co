from django.conf import settings
from django.contrib.auth.models import User
from django.http.response import Http404
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone
from django.views.generic import (
    ListView,
    DetailView,
    FormView,
    UpdateView,
    TemplateView
)

from hashlib import md5
from sidekick.seo.views import (
    SEOMixin,
    OpenGraphMixin,
    OpenGraphArticleMixin,
    LinkedDataMixin
)

from taggit.models import Tag
from urllib.parse import urlencode
from .forms import SubscriberForm
from .models import Post, Subscriber
import jwt


class PostMixin(SEOMixin, LinkedDataMixin):
    model = Post
    ld_type = 'BlogPost'


class PostListView(PostMixin, OpenGraphMixin, ListView):
    paginate_by = 24
    og_title = 'Post archive'
    og_description = 'Drown in an ocean of posts about Notion.'
    ld_type = 'Blog'
    ld_attributes = {
        'name': 'Notion Sidekick'
    }

    def get_tags(self):
        if not hasattr(self, '_tags'):
            slugs = self.request.GET.getlist('tag')
            self._tags = Tag.objects.none()

            if any(slugs):
                self._tags = Tag.objects.filter(
                    slug__in=slugs
                ).distinct()

        return self._tags

    def get_author(self):
        if not hasattr(self, '_author'):
            self._author = None

            if username := self.request.GET.get('author'):
                self._author = User.objects.filter(
                    username=username
                ).first()

        return self._author

    def get_queryset(self):
        queryset = super().get_queryset().filter(
            published__lte=timezone.now(),
            status__iexact='published'
        )

        if tags := self.get_tags():
            queryset = queryset.filter(
                tags__in=tags
            )

        if author := self.get_author():
            queryset = queryset.filter(
                author=author
            )

        return queryset.distinct()

    def get_seo_title(self):
        title = 'Notion Sidekick posts'

        if tags := self.get_tags():
            title += ' tagged %s' % ', '.join(
                [tag.name for tag in tags]
            )

        if author := self.get_author():
            title += ' by %s' % author.get_full_name()

        return title

    def get_context_data(self, **kwargs):
        tags = kwargs.get('tags', self.get_tags())
        user = kwargs.get('user', self.get_author())

        return {
            **super().get_context_data(**kwargs),
            'tags': tags,
            'author': user
        }


class PostDetailView(PostMixin, OpenGraphArticleMixin, DetailView):
    ld_type = 'BlogPosting'

    def get_og_description(self):
        return self.get_object().get_excerpt()
    
    def get_ld_attributes(self):
        obj = self.get_object()
        attrs = {
            'headline': obj.title,
            'inLanguage': 'en-gb',
            'url': self.request.build_absolute_uri(
                reverse('post_list')
            ),
            'description': obj.get_excerpt(),
            'author': {
                '@type': 'Person',
                'name': obj.author.get_full_name(),
                'givenName': obj.author.first_name,
                'familyName': obj.author.last_name,
                'image': {
                    '@type': 'imageObject',
                    'url': 'https://secure.gravatar.com/avatar/%s?%s' % (
                        md5(obj.author.email.encode('utf-8')).hexdigest(),
                        urlencode(
                            {
                                's': 400,
                                'd': 'mp',
                                'r': 'g'
                            }
                        )
                    ),
                    'width': 400,
                    'height': 400
                }
            }
        }

        if obj.published:
            attrs['datePublished'] = obj.published

        return attrs


class CreateSubscriberView(SEOMixin, FormView):
    template_name = 'newsletter/subscriber_form.html'
    form_class = SubscriberForm
    seo_title = 'Subscribe to the Notion Sidekick newsletter'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('subscriber_created')


class SubscriberCreatedView(SEOMixin, TemplateView):
    robots = 'noindex'
    template_name = 'newsletter/subscriber_created.html'


class UpdateSubscriberView(SEOMixin, UpdateView):
    robots = 'noindex'
    form_class = SubscriberForm
    
    def get_seo_title(self):
        return 'Update your email preferences'

    def get_object(self):
        token = jwt.decode(
            self.kwargs['token'],
            settings.SECRET_KEY,
            algorithms=('HS256',)
        )

        try:
            return Subscriber.objects.get(
                notion_id=token['n']
            )
        except Subscriber.DoesNotExist:
            raise Http404('Subscriber not found.')

    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except jwt.InvalidTokenError:
            return TemplateResponse(
                self.request,
                'newsletter/invalid_token.html',
                status=400
            )

    def get_success_url(self):
        return reverse('subscriber_updated')


class SubscriberUpdatedView(SEOMixin, TemplateView):
    robots = 'noindex'
    template_name = 'newsletter/subscriber_updated.html'


class EmailPreview(ListView):
    model = Post
    paginate_by = 5
    template_name = 'newsletter/digest_email.html'
