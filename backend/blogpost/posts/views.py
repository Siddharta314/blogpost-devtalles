from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import Post, Tag, Category
from .serializers import (
    PostListSerializer,
    PostDetailSerializer,
    PostCreateUpdateSerializer,
    TagSerializer,
    CategorySerializer,
)


class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar posts con operaciones CRUD completas.
    """

    queryset = Post.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # Filtros
    filterset_fields = {
        "is_published": ["exact"],
        "author": ["exact"],
        "category": ["exact"],
        "tags": ["exact"],
        "created_at": ["gte", "lte", "exact"],
    }

    # Búsqueda
    search_fields = ["title", "content", "author__username"]

    # Ordenación
    ordering_fields = ["created_at", "updated_at", "title"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        """
        Retorna el serializer apropiado según la acción.
        """
        if self.action == "list":
            return PostListSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return PostCreateUpdateSerializer
        return PostDetailSerializer

    def get_queryset(self):
        """
        Filtra posts según el usuario y permisos.
        El PostManager ya filtra automáticamente los posts eliminados.
        """
        queryset = super().get_queryset()

        # Optimización de consultas: evitar N+1 queries
        queryset = queryset.select_related("author", "category").prefetch_related("tags")

        # Si el usuario está autenticado, puede ver sus propios posts no publicados
        if self.request.user.is_authenticated:
            queryset = queryset.filter(Q(is_published=True) | Q(author=self.request.user))
        else:
            # Usuarios no autenticados solo ven posts publicados
            queryset = queryset.filter(is_published=True)

        return queryset

    def _check_author(self, post, user):
        """
        Verifica si el usuario es el autor del post.
        Retorna Response con error si no es autor, None si es autor.
        """
        if post.author != user:
            return Response(
                {"detail": "No tienes permisos para esta acción."}, status=status.HTTP_403_FORBIDDEN
            )
        return None

    def perform_create(self, serializer):
        """
        Asigna el autor del post al usuario actual.
        """
        serializer.save(author=self.request.user)

    def get_permissions(self):
        """
        Asigna permisos específicos según la acción.
        """
        perms = {
            "create": [IsAuthenticated],
            "update": [IsAuthenticated],
            "partial_update": [IsAuthenticated],
            "destroy": [IsAuthenticated],
        }
        permission_classes = perms.get(self.action, [IsAuthenticatedOrReadOnly])
        return [p() for p in permission_classes]

    def destroy(self, request, *args, **kwargs):
        """
        Soft delete: marca el post como eliminado en lugar de borrarlo.
        """
        instance = self.get_object()

        # Verificar permisos de autor
        error_response = self._check_author(instance, request.user)
        if error_response:
            return error_response

        instance.delete()  # Esto ejecutará el soft delete del modelo
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def publish(self, request, pk=None):
        """
        Publica un post (solo el autor puede hacerlo).
        """
        post = self.get_object()

        # Verificar permisos de autor
        error_response = self._check_author(post, request.user)
        if error_response:
            return error_response

        post.is_published = True
        post.save()

        serializer = self.get_serializer(post)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def unpublish(self, request, pk=None):
        """
        Despublica un post (solo el autor puede hacerlo).
        """
        post = self.get_object()

        # Verificar permisos de autor
        error_response = self._check_author(post, request.user)
        if error_response:
            return error_response

        post.is_published = False
        post.save()

        serializer = self.get_serializer(post)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def my_posts(self, request):
        """
        Lista los posts del usuario actual.
        """
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Debes estar autenticado para ver tus posts."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        queryset = self.get_queryset().filter(author=request.user)
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para tags.
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["name", "slug"]
    search_fields = ["name"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para categorías.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["name", "slug"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]
