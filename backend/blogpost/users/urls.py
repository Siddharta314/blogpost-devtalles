from django.urls import path

from .views import RegisterView, MeView

app_name = "users"

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/me/", MeView.as_view(), name="me"),
]
