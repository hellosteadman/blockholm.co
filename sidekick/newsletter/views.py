from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.views.generic import ListView, DetailView, FormView, TemplateView
from sidekick.seo.views import SEOMixin, OpenGraphMixin, OpenGraphArticleMixin
from taggit.models import Tag
from .forms import SubscriberForm
from .models import Post


class PostMixin(SEOMixin):
    model = Post
    ld_type = 'BlogPost'


class PostListView(PostMixin, OpenGraphMixin, ListView):
    paginate_by = 24

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
            published__lte=timezone.now()
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
    pass


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


class SubscriberUpdatedView(SEOMixin, TemplateView):
    robots = 'noindex'
    template_name = 'newsletter/subscriber_updated.html'


class EmailPreview(ListView):
    model = Post
    paginate_by = 5
    template_name = 'newsletter/digest_email.html'
