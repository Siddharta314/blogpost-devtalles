from rest_framework import serializers
from .models import Comment


class CommentListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar comentarios.
    """

    author = serializers.StringRelatedField(read_only=True)
    replies_count = serializers.SerializerMethodField()
    is_reply = serializers.ReadOnlyField()
    is_edited = serializers.ReadOnlyField()

    class Meta:
        model = Comment
        fields = (
            "id",
            "content",
            "author",
            "created_at",
            "updated_at",
            "is_approved",
            "is_edited",
            "is_reply",
            "replies_count",
        )
        read_only_fields = ("id", "created_at", "updated_at", "is_edited")

    def get_replies_count(self, obj):
        """Cuenta las respuestas a este comentario."""
        return obj.get_replies_count()


class CommentDetailSerializer(serializers.ModelSerializer):
    """
    Serializer completo para mostrar un comentario individual con sus respuestas.
    """

    author = serializers.StringRelatedField(read_only=True)
    replies = CommentListSerializer(many=True, read_only=True)
    is_reply = serializers.ReadOnlyField()
    is_deleted = serializers.ReadOnlyField()

    class Meta:
        model = Comment
        fields = (
            "id",
            "content",
            "author",
            "post",
            "parent",
            "created_at",
            "updated_at",
            "deleted_at",
            "is_approved",
            "is_edited",
            "is_reply",
            "is_deleted",
            "replies",
        )
        read_only_fields = ("id", "created_at", "updated_at", "is_edited", "is_deleted")


class CommentCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear y actualizar comentarios.
    """

    class Meta:
        model = Comment
        fields = ("content", "post", "parent")

    def validate_content(self, value):
        """Valida que el contenido no esté vacío."""
        if not value.strip():
            raise serializers.ValidationError("El contenido del comentario no puede estar vacío.")
        return value.strip()

    def validate_parent(self, value):
        """Valida que el comentario padre pertenezca al mismo post."""
        if value and self.initial_data.get("post"):
            if value.post_id != self.initial_data["post"]:
                raise serializers.ValidationError(
                    "El comentario padre debe pertenecer al mismo post."
                )
        return value

    def create(self, validated_data):
        """Crea un nuevo comentario con el autor actual."""
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Marca el comentario como editado al actualizarlo."""
        instance.is_edited = True
        return super().update(instance, validated_data)


class CommentReplySerializer(serializers.ModelSerializer):
    """
    Serializer específico para crear respuestas a comentarios.
    """

    class Meta:
        model = Comment
        fields = ("content",)

    def validate_content(self, value):
        """Valida que el contenido no esté vacío."""
        if not value.strip():
            raise serializers.ValidationError("El contenido del comentario no puede estar vacío.")
        return value.strip()

    def create(self, validated_data):
        """Crea una respuesta a un comentario."""
        parent_comment = self.context["parent_comment"]
        validated_data.update(
            {
                "author": self.context["request"].user,
                "post": parent_comment.post,
                "parent": parent_comment,
            }
        )
        return super().create(validated_data)
