from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend

from .models import Like
from .serializers import (
    LikeSerializer,
    LikeCreateSerializer,
    LikeToggleSerializer,
    PostLikeStatsSerializer,
)


class LikeViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar likes: crear, eliminar y utilidades.
    - create: Crea un like (requiere autenticación)
    - destroy: Elimina un like propio (requiere autenticación)
    - toggle: Alterna like (requiere autenticación)
    - stats: Estadísticas de likes de un post
    """

    queryset = Like.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {"post": ["exact"], "user": ["exact"]}

    def get_permissions(self):
        if self.action in ["create", "destroy", "toggle"]:
            return [IsAuthenticated()]
        # Acceso público para acciones de sólo lectura como stats y list/retrieve (si se usan)
        return []

    def get_serializer_class(self):
        if self.action == "create":
            return LikeCreateSerializer
        elif self.action == "toggle":
            return LikeToggleSerializer
        return LikeSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response(
                {"detail": "No puedes eliminar el like de otro usuario."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=["post"])
    def toggle(self, request):
        """Crea o elimina un like para el post indicado."""
        serializer = LikeToggleSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        http_status = (
            status.HTTP_201_CREATED
            if result.get("action") == "created"
            else status.HTTP_204_NO_CONTENT
        )
        # Cuando se elimina, retornamos sin cuerpo
        if http_status == status.HTTP_204_NO_CONTENT:
            return Response(status=http_status)
        return Response(result, status=http_status)

    @action(detail=False, methods=["get"], url_path="stats/(?P<post_id>[^/.]+)")
    def stats(self, request, post_id=None):
        """Devuelve estadísticas de likes de un post."""
        from posts.models import Post

        post = get_object_or_404(Post.objects.filter(deleted_at__isnull=True), pk=post_id)
        data = PostLikeStatsSerializer(post, context={"request": request}).data
        return Response(data)
