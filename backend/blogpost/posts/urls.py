from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PostViewSet, TagViewSet, CategoryViewSet

# Router para ViewSets
router = DefaultRouter()
router.register(r"posts", PostViewSet, basename="posts")
router.register(r"tags", TagViewSet, basename="tags")
router.register(r"categories", CategoryViewSet, basename="categories")

app_name = "posts"

urlpatterns = [
    path("", include(router.urls)),
]
