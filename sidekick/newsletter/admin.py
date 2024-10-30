from django.contrib import admin
from .models import Post, Block, Subscriber


class BlockInline(admin.StackedInline):
    model = Block
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'published', 'status')
    date_hierarchy = 'published'
    list_filter = ('status', 'tags')
    inlines = [BlockInline]

    def has_add_permission(self, request):
        return False


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subscribed')
    date_hierarchy = 'subscribed'
    filter_horizontal = ('sent_posts',)
