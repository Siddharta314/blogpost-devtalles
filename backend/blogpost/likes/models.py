from django.db import models
from django.conf import settings


class Like(models.Model):
    """
    Representa un "me gusta" de un usuario a un post.
    Un usuario no puede dar más de un like al mismo post.
    """

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="likes"
    )
    post = models.ForeignKey("posts.Post", on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "post"], name="unique_user_post_like")
        ]
        indexes = [
            models.Index(fields=["post", "created_at"]),
            models.Index(fields=["user", "created_at"]),
        ]

    def __str__(self):
        return f"{self.user.username} likes {self.post.title}"

    @classmethod
    def toggle_like(cls, user, post):
        """
        Alterna el like: si existe lo elimina, si no existe lo crea.
        Retorna (like_object, created) donde created es True si se creó.
        """
        like, created = cls.objects.get_or_create(user=user, post=post)
        if not created:
            # Si ya existía, lo eliminamos
            like.delete()
            return None, False
        return like, True

    @classmethod
    def get_likes_count_for_post(cls, post):
        """Cuenta los likes de un post específico."""
        return cls.objects.filter(post=post).count()

    @classmethod
    def user_has_liked_post(cls, user, post):
        """Verifica si un usuario ya le dio like a un post."""
        return cls.objects.filter(user=user, post=post).exists()
