from django.db import models
from django.conf import settings


class Category(models.Model):
    """
    Categorías para clasificar los posts.
    """

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Tag(models.Model):
    """
    Etiquetas para etiquetar los posts.
    """

    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    color = models.CharField(
        max_length=7, default="#007bff", help_text="Color en formato hex (ej: #007bff)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Post(models.Model):
    """
    Modelo principal para las publicaciones del blog.
    """

    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    content = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    is_published = models.BooleanField(default=False)
    tags = models.ManyToManyField("Tag", blank=True)
    category = models.ForeignKey(
        "Category", null=True, blank=True, on_delete=models.SET_NULL, related_name="posts"
    )
    image = models.ImageField(upload_to="posts/", null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["is_published", "created_at"]),
            models.Index(fields=["author", "created_at"]),
            models.Index(fields=["category", "created_at"]),
        ]

    def __str__(self):
        return self.title

    @property
    def is_deleted(self):
        """Verifica si el post está marcado como eliminado (soft delete)."""
        return self.deleted_at is not None
