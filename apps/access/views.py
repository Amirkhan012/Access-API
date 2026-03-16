from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Action, Resource, Role, RolePermission, UserRole
from .services import can_manage_access
from .serializers import (
    ActionSerializer,
    ResourceSerializer,
    RolePermissionReadSerializer,
    RolePermissionWriteSerializer,
    RoleSerializer,
    UserRoleReadSerializer,
    UserRoleWriteSerializer,
)


def unauthorized_response() -> Response:
    """Возвращает ответ 401 для неавторизованного пользователя."""
    return Response(
        {"detail": "Требуется авторизация."},
        status=status.HTTP_401_UNAUTHORIZED,
    )


def forbidden_response() -> Response:
    """Возвращает ответ 403 при нехватке прав."""
    return Response(
        {"detail": "Недостаточно прав для управления доступом."},
        status=status.HTTP_403_FORBIDDEN,
    )


def require_access_management(request: Request) -> Response | None:
    """Проверяет доступ к API управления правами."""
    if not request.user.is_authenticated:
        return unauthorized_response()

    if not can_manage_access(user=request.user):
        return forbidden_response()

    return None


class RoleListView(APIView):
    """Возвращает список ролей."""

    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        """Возвращает список ролей."""
        error_response = require_access_management(request)
        if error_response is not None:
            return error_response

        roles = Role.objects.all()
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ResourceListView(APIView):
    """Возвращает список ресурсов."""

    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        """Возвращает список ресурсов."""
        error_response = require_access_management(request)
        if error_response is not None:
            return error_response

        resources = Resource.objects.all()
        serializer = ResourceSerializer(resources, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ActionListView(APIView):
    """Возвращает список действий."""

    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        """Возвращает список действий."""
        error_response = require_access_management(request)
        if error_response is not None:
            return error_response

        actions = Action.objects.all()
        serializer = ActionSerializer(actions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserRoleListCreateView(APIView):
    """Показывает и создаёт назначения ролей пользователям."""

    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        """Возвращает список назначений ролей пользователям."""
        error_response = require_access_management(request)
        if error_response is not None:
            return error_response

        user_roles = UserRole.objects.select_related("user", "role").all()
        serializer = UserRoleReadSerializer(user_roles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        """Создаёт новое назначение роли пользователю."""
        error_response = require_access_management(request)
        if error_response is not None:
            return error_response

        serializer = UserRoleWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_role = serializer.save()

        response_serializer = UserRoleReadSerializer(user_role)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )


class UserRoleDeleteView(APIView):
    """Удаляет назначение роли пользователю."""

    permission_classes = [AllowAny]

    def delete(self, request: Request, user_role_id: int) -> Response:
        """Удаляет назначение роли пользователю по идентификатору."""
        error_response = require_access_management(request)
        if error_response is not None:
            return error_response

        try:
            user_role = UserRole.objects.get(id=user_role_id)
        except UserRole.DoesNotExist:
            return Response(
                {"detail": "Назначение роли не найдено."},
                status=status.HTTP_404_NOT_FOUND,
            )

        user_role.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RolePermissionListCreateView(APIView):
    """Показывает и создаёт правила доступа ролей."""

    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        """Возвращает список правил доступа ролей."""
        error_response = require_access_management(request)
        if error_response is not None:
            return error_response

        role_permissions = RolePermission.objects.select_related(
            "role",
            "resource",
            "action",
        ).all()
        serializer = RolePermissionReadSerializer(role_permissions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        """Создаёт новое правило доступа роли."""
        error_response = require_access_management(request)
        if error_response is not None:
            return error_response

        serializer = RolePermissionWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        role_permission = serializer.save()

        response_serializer = RolePermissionReadSerializer(role_permission)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )


class RolePermissionDeleteView(APIView):
    """Удаляет правило доступа роли."""

    permission_classes = [AllowAny]

    def delete(self, request: Request, role_permission_id: int) -> Response:
        """Удаляет правило доступа по идентификатору."""
        error_response = require_access_management(request)
        if error_response is not None:
            return error_response

        try:
            role_permission = RolePermission.objects.get(id=role_permission_id)
        except RolePermission.DoesNotExist:
            return Response(
                {"detail": "Правило доступа не найдено."},
                status=status.HTTP_404_NOT_FOUND,
            )

        role_permission.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
