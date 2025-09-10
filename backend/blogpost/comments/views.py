from rest_framework import viewsets, status, filters
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import Comment
from .serializers import (
    CommentListSerializer,
    CommentDetailSerializer,
    CommentCreateUpdateSerializer,
    CommentReplySerializer,
)


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar comentarios con operaciones CRUD completas.
    """

    queryset = Comment.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # Filtros
    filterset_fields = {
        "is_approved": ["exact"],
        "author": ["exact"],
        "post": ["exact"],
        "parent": ["exact", "isnull"],  # parent__isnull=true para comentarios principales
        "created_at": ["gte", "lte", "exact"],
        "is_edited": ["exact"],
    }

    # Búsqueda
    search_fields = ["content", "author__username"]

    # Ordenación
    ordering_fields = ["created_at", "updated_at"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        """
        Retorna el serializer apropiado según la acción.
        """
        if self.action == "list":
            return CommentListSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return CommentCreateUpdateSerializer
        return CommentDetailSerializer

    def get_queryset(self):
        """
        Filtra comentarios según el usuario y permisos.
        El CommentManager ya filtra automáticamente los comentarios eliminados.
        """
        queryset = super().get_queryset()

        # Optimización de consultas: evitar N+1 queries
        from django.db.models import Prefetch

        queryset = queryset.select_related("author", "post", "parent").prefetch_related(
            Prefetch(
                "replies",
                queryset=Comment.objects.select_related("author", "post").order_by("created_at"),
                to_attr="ordered_replies",
            )
        )

        # Si el usuario está autenticado, puede ver sus propios comentarios no aprobados
        if self.request.user.is_authenticated:
            queryset = queryset.filter(Q(is_approved=True) | Q(author=self.request.user))
        else:
            # Usuarios no autenticados solo ven comentarios aprobados
            queryset = queryset.filter(is_approved=True)

        return queryset

    def _check_author(self, comment, user):
        """
        Verifica si el usuario es el autor del comentario.
        Retorna Response con error si no es autor, None si es autor.
        """
        if comment.author != user:
            return Response(
                {"detail": "No tienes permisos para esta acción."}, status=status.HTTP_403_FORBIDDEN
            )
        return None

    def _paginated_response(self, queryset):
        """
        Genera una respuesta paginada para un queryset.
        """
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        """
        Asigna el autor del comentario al usuario actual y valida el post.
        """
        post = serializer.validated_data["post"]
        if not post.is_published or post.deleted_at is not None:
            raise ValidationError("No se puede comentar en este post.")
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
        Soft delete: marca el comentario como eliminado en lugar de borrarlo.
        """
        instance = self.get_object()

        # Verificar permisos de autor
        error_response = self._check_author(instance, request.user)
        if error_response:
            return error_response

        instance.delete()  # Esto ejecutará el soft delete del modelo
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def approve(self, request, pk=None):
        """
        Aprueba un comentario (solo el autor del post puede hacerlo).
        """
        comment = self.get_object()
        post = comment.post

        # Solo el autor del post puede aprobar comentarios
        if post.author != request.user:
            return Response(
                {"detail": "Solo el autor del post puede aprobar comentarios."},
                status=status.HTTP_403_FORBIDDEN,
            )

        comment.is_approved = True
        comment.save()

        serializer = self.get_serializer(comment)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def disapprove(self, request, pk=None):
        """
        Desaprueba un comentario (solo el autor del post puede hacerlo).
        """
        comment = self.get_object()
        post = comment.post

        # Solo el autor del post puede desaprobar comentarios
        if post.author != request.user:
            return Response(
                {"detail": "Solo el autor del post puede desaprobar comentarios."},
                status=status.HTTP_403_FORBIDDEN,
            )

        comment.is_approved = False
        comment.save()

        serializer = self.get_serializer(comment)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def reply(self, request, pk=None):
        """
        Crea una respuesta a un comentario.
        """
        parent_comment = self.get_object()

        # Verificar que el comentario padre esté aprobado
        if not parent_comment.is_approved:
            return Response(
                {"detail": "No puedes responder a un comentario no aprobado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = CommentReplySerializer(
            data=request.data,
            context={
                "request": request,
                "parent_comment": parent_comment,
            },
        )

        if serializer.is_valid():
            reply = serializer.save()
            response_serializer = CommentDetailSerializer(reply)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def my_comments(self, request):
        """
        Lista los comentarios del usuario actual.
        """
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Debes estar autenticado para ver tus comentarios."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        queryset = self.get_queryset().filter(author=request.user)
        return self._paginated_response(queryset)

    @action(detail=False, methods=["get"])
    def pending_approval(self, request):
        """
        Lista comentarios pendientes de aprobación (solo para autores de posts).
        """
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Debes estar autenticado."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Solo comentarios de posts del usuario actual que no están aprobados
        queryset = self.get_queryset().filter(post__author=request.user, is_approved=False)
        return self._paginated_response(queryset)
