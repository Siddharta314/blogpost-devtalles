from rest_framework import serializers
from .models import Like


def validate_post_for_like(post):
    """
    Valida que un post esté disponible para recibir likes.
    """
    if not post.is_published:
        raise serializers.ValidationError("No puedes dar like a un post no publicado.")

    if post.deleted_at is not None:
        raise serializers.ValidationError("No puedes dar like a un post eliminado.")

    return post


class LikeSerializer(serializers.ModelSerializer):
    """
    Serializer para mostrar likes.
    """

    user = serializers.StringRelatedField(read_only=True)
    post = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Like
        fields = ("id", "user", "post", "created_at")
        read_only_fields = ("id", "created_at")


class LikeCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear likes.
    """

    class Meta:
        model = Like
        fields = ("post",)

    def validate_post(self, value):
        """Valida que el post esté disponible para likes."""
        return validate_post_for_like(value)

    def create(self, validated_data):
        """Crea un like con el usuario actual."""
        user = self.context["request"].user
        post = validated_data["post"]

        # Verificar si ya existe un like
        if Like.objects.filter(user=user, post=post).exists():
            raise serializers.ValidationError("Ya has dado like a este post.")

        validated_data["user"] = user
        return super().create(validated_data)


class LikeToggleSerializer(serializers.Serializer):
    """
    Serializer para alternar likes (crear o eliminar).
    """

    post = serializers.PrimaryKeyRelatedField(queryset=None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar solo posts publicados y no eliminados
        from posts.models import Post

        self.fields["post"].queryset = Post.objects.filter(
            is_published=True, deleted_at__isnull=True
        )

    def validate_post(self, value):
        """Valida que el post esté disponible para likes."""
        return validate_post_for_like(value)

    def save(self, **kwargs):
        """Alterna el like: crea si no existe, elimina si existe."""
        user = self.context["request"].user
        post = self.validated_data["post"]

        like, created = Like.toggle_like(user, post)

        if created:
            like_data = LikeSerializer(like, context=self.context).data
            return {"like": like_data, "created": created, "action": "created"}
        else:
            return {"like": None, "created": created, "action": "deleted"}


class PostLikeStatsSerializer(serializers.Serializer):
    """
    Serializer para mostrar estadísticas de likes de un post.
    """

    post_id = serializers.IntegerField(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    user_has_liked = serializers.BooleanField(read_only=True)

    def to_representation(self, instance):
        """Genera las estadísticas de likes para un post."""
        request = self.context.get("request")
        user = request.user if request and request.user.is_authenticated else None

        return {
            "post_id": instance.id,
            "likes_count": Like.get_likes_count_for_post(instance),
            "user_has_liked": Like.user_has_liked_post(user, instance) if user else False,
        }
