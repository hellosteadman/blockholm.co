from django import forms
from django.db import transaction
from django.db.models import Count
from django.utils import timezone
from sidekick.contrib.notion import sync
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

    def __init__(self, *args, **kwargs):
        if instance := kwargs.get('instance'):
            if instance.pk and instance.excluded_tags.exists():
                initial = kwargs.get('initial', {})
                initial['include_tags'] = Tag.objects.annotate(
                    post_count=Count('posts')
                ).filter(
                    post_count__gte=2
                ).exclude(
                    pk__in=instance.excluded_tags.values_list(
                        'pk',
                        flat=True
                    )
                )

                kwargs['initial'] = initial

        super().__init__(*args, **kwargs)

    @transaction.atomic
    def save(self):
        include_tags = self.cleaned_data.get('include_tags', [])
        excluded_tags = Tag.objects.annotate(
            post_count=Count('posts')
        ).filter(
            post_count__gte=2
        ).exclude(
            pk__in=include_tags
        )

        if self.instance and self.instance.pk:
            obj = super().save(commit=False)
            obj.status = 'Subscribed'
            obj.save()

            for tag in excluded_tags:
                obj.excluded_tags.add(tag)

            obj.excluded_tags.remove(
                *Tag.objects.exclude(
                    pk__in=excluded_tags.values_list(
                        'pk',
                        flat=True
                    )
                )
            )

            obj.save()
            transaction.on_commit(
                lambda: sync.from_model(obj)
            )

            return obj

        Subscriber.objects.send_confirmation(
            email=self.cleaned_data['email'],
            name=self.cleaned_data.get('name'),
            excluded_tags=excluded_tags
        )

    class Meta:
        model = Subscriber
        fields = (
            'email',
            'name'
        )
