from django.contrib import admin
from .models import Post, Subscriber


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'published', 'status')
    date_hierarchy = 'published'
    list_filter = ('status', 'tags')

    def has_add_permission(self, request):
        return False


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subscribed', 'status')
    list_filter = ('status',)
    date_hierarchy = 'subscribed'
    filter_horizontal = ('sent_posts',)
