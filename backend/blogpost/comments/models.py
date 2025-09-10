from django.db import models
from django.conf import settings
from django.utils import timezone


class CommentManager(models.Manager):
    """
    Manager personalizado que filtra automáticamente los comentarios eliminados.
    """

    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class Comment(models.Model):
    """
    Comentarios realizados sobre los posts.
    """

    id = models.BigAutoField(primary_key=True)
    content = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments"
    )
    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE, related_name="comments")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies"
    )

    is_approved = models.BooleanField(default=True)
    is_edited = models.BooleanField(default=False)

    # Managers
    objects = CommentManager()  # Manager personalizado (filtra eliminados)
    all_objects = models.Manager()  # Manager para ver todos (incluyendo eliminados)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["post", "created_at"]),
            models.Index(fields=["author", "created_at"]),
            models.Index(fields=["parent", "created_at"]),
        ]

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"

    def delete(self, *args, **kwargs):
        """Soft delete: marca el comentario como eliminado en vez de borrarlo."""
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])

    @property
    def is_deleted(self):
        """Verifica si el comentario está marcado como eliminado (soft delete)."""
        return self.deleted_at is not None

    @property
    def is_reply(self):
        """Verifica si es una respuesta a otro comentario."""
        return self.parent is not None

    def get_replies_count(self):
        """Cuenta las respuestas a este comentario."""
        return self.replies.filter(deleted_at__isnull=True).count()
