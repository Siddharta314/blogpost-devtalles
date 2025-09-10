from rest_framework import serializers
from .models import User, UserAuthProvider


class UserAuthProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAuthProvider
        fields = (
            "provider",
            "provider_user_id",
            "username",
        )
        read_only_fields = (
            "provider",
            "provider_user_id",
            "username",
        )


class UserSerializer(serializers.ModelSerializer):
    auth_providers = UserAuthProviderSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "avatar_url",
            "auth_providers",  # muestra proveedores asociados
        )
        read_only_fields = (
            "id",
            "auth_providers",
        )
        extra_kwargs = {
            "email": {"required": True},
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exclude(pk=getattr(self.instance, "pk", None)).exists():
            raise serializers.ValidationError("Este email ya está registrado.")
        return value
