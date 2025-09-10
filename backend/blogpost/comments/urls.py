from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CommentViewSet

# Router para ViewSets
router = DefaultRouter()
router.register(r"comments", CommentViewSet, basename="comments")

app_name = "comments"

urlpatterns = [
    path("", include(router.urls)),
]
