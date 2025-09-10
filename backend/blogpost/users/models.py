from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom user model.
    Almacena información básica de Django y sirve como base para múltiples proveedores de login.
    username, password, first_name, last_name, email, is_staff, is_superuser, is_active, last_login, date_joined.
    """

    email = models.EmailField(unique=True)
    avatar_url = models.URLField(max_length=500, null=True, blank=True)

    USERNAME_FIELD = "email"  # hace que Django use el email en vez del username para login
    REQUIRED_FIELDS = [
        "username",
        "first_name",
        "last_name",
    ]  # Campos obligatorios al crear un superusuario con createsuperuser

    def __str__(self):
        return self.username or self.email


class UserAuthProvider(models.Model):
    """
    Relaciona un usuario con un proveedor de autenticación externo.
    """

    PROVIDER_CHOICES = [
        ("discord", "Discord"),
        ("google", "Google"),
        ("github", "GitHub"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auth_providers")
    provider = models.CharField(max_length=50, choices=PROVIDER_CHOICES, db_index=True)
    provider_user_id = models.CharField(max_length=255, db_index=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    access_token = models.TextField(null=True, blank=True)
    refresh_token = models.TextField(null=True, blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("provider", "provider_user_id"),
                name="uq_provider_user_id_per_provider",
            )
        ]

    def __str__(self):
        return f"{self.user.username} ({self.provider})"
