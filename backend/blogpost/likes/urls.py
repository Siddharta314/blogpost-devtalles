from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import LikeViewSet

app_name = "likes"

router = DefaultRouter()
router.register(r"likes", LikeViewSet, basename="likes")

urlpatterns = [
    path("", include(router.urls)),
]
