from rest_framework import serializers
from .models import Post, Tag, Category


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "slug", "color", "created_at")
        read_only_fields = ("id", "created_at")


class CategorySerializer(serializers.ModelSerializer):
    posts_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ("id", "name", "slug", "description", "created_at", "updated_at", "posts_count")
        read_only_fields = ("id", "created_at", "updated_at", "posts_count")

    def get_posts_count(self, obj):
        """Cuenta los posts publicados en esta categoría."""
        return obj.posts.filter(is_published=True, deleted_at__isnull=True).count()


class PostListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar posts (sin contenido completo).
    """

    author = serializers.StringRelatedField(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    excerpt = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "slug",
            "excerpt",
            "author",
            "created_at",
            "updated_at",
            "is_published",
            "tags",
            "category",
            "image",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def get_excerpt(self, obj):
        """Genera un extracto del contenido (primeros 150 caracteres)."""
        if len(obj.content) <= 150:
            return obj.content
        return obj.content[:150] + "..."


class PostDetailSerializer(serializers.ModelSerializer):
    """
    Serializer completo para mostrar un post individual.
    """

    author = serializers.StringRelatedField(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    is_deleted = serializers.ReadOnlyField()

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "slug",
            "content",
            "author",
            "created_at",
            "updated_at",
            "deleted_at",
            "is_published",
            "tags",
            "category",
            "image",
            "is_deleted",
        )
        read_only_fields = ("id", "created_at", "updated_at", "is_deleted")


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear y actualizar posts.
    """

    class Meta:
        model = Post
        fields = ("title", "slug", "content", "is_published", "tags", "category", "image")

    def validate_slug(self, value):
        """Valida que el slug sea único."""
        if self.instance and self.instance.slug == value:
            return value

        if Post.objects.filter(slug=value, deleted_at__isnull=True).exists():
            raise serializers.ValidationError("Un post con este slug ya existe.")

        return value

    def validate_title(self, value):
        """Valida que el título no esté vacío."""
        if not value.strip():
            raise serializers.ValidationError("El título no puede estar vacío.")
        return value.strip()

    def validate_content(self, value):
        """Valida que el contenido no esté vacío."""
        if not value.strip():
            raise serializers.ValidationError("El contenido no puede estar vacío.")
        return value.strip()
