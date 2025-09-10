from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserAuthProvider


class UserAuthProviderInline(admin.TabularInline):
    model = UserAuthProvider
    extra = 0  # sin filas extra por defecto
    readonly_fields = (
        "provider",
        "provider_user_id",
        "username",
        "access_token",
        "refresh_token",
        "token_expires_at",
    )
    fields = (
        "provider",
        "provider_user_id",
        "username",
        "access_token",
        "refresh_token",
        "token_expires_at",
    )


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [UserAuthProviderInline]  # se muestran los proveedores

    # Campos a mostrar en la lista
    list_display = (
        "id",
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "date_joined",
    )
    list_filter = ("is_staff", "is_active", "is_superuser", "date_joined")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("-date_joined",)
    date_hierarchy = "date_joined"

    # Campos en el formulario de edición
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email", "avatar_url")}),
        (
            "Permissions",
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    # Campos en el formulario de creación
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                ),
            },
        ),
    )


@admin.register(UserAuthProvider)
class UserAuthProviderAdmin(admin.ModelAdmin):
    list_display = ("user", "provider", "provider_user_id", "username", "token_expires_at")
    list_filter = ("provider", "token_expires_at")
    search_fields = ("user__username", "user__email", "provider_user_id", "username")
    readonly_fields = (
        "provider",
        "provider_user_id",
        "username",
        "access_token",
        "refresh_token",
        "token_expires_at",
    )
    date_hierarchy = "token_expires_at"
    ordering = ("-token_expires_at",)
