from django.contrib import admin
from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("author", "post", "content", "is_approved", "is_edited", "created_at")
    list_filter = ("is_approved", "created_at")
    search_fields = ("content", "author__username", "post__title")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
