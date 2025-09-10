from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserAuthProvider


class UserAuthProviderInline(admin.TabularInline):
    model = UserAuthProvider
    extra = 0  # sin filas extra por defecto
    readonly_fields = ("provider", "provider_user_id", "username")


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = [UserAuthProviderInline]  # se muestran los proveedores
    list_display = ("id", "username", "email", "is_staff", "is_active")
    search_fields = ("username", "email")
