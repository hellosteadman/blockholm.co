from django import forms
from django.db import transaction
from django.db.models import Count
from django.utils import timezone
from sidekick.contrib.notion import sync
from sidekick.contrib.recaptcha.fields import RecaptchaField
from taggit.models import Tag
from .models import Subscriber


class SubscriberForm(forms.ModelForm):
    email = forms.EmailField(
        label='Your email address',
        max_length=255
    )

    name = forms.CharField(
        label='Your name (if you want to share)',
        required=False,
        max_length=100
    )

    include_tags = forms.ModelMultipleChoiceField(
        label='Which categories would you like included in your email?',
        queryset=Tag.objects.annotate(
            post_count=Count('posts')
        ).filter(
            post_count__gte=2
        ).order_by('name'),
        widget=forms.CheckboxSelectMultiple,
        initial=Tag.objects.annotate(
            post_count=Count('posts')
        ).filter(
            post_count__gte=2
        ),
        required=False
    )

    captcha = RecaptchaField()

    @transaction.atomic
    def save(self):
        obj = super().save(commit=False)
        obj.subscribed = timezone.now()
        obj.save()

        include_tags = self.cleaned_data.get('include_tags', [])
        excluded_tags = Tag.objects.annotate(
            post_count=Count('posts')
        ).filter(
            post_count__gte=2
        ).exclude(
            pk__in=include_tags
        )

        for tag in excluded_tags:
            obj.excluded_tags.add(tag)

        obj.notion_id = sync.from_model(obj)
        obj.save()

        return obj

    class Meta:
        model = Subscriber
        fields = (
            'email',
            'name'
        )
