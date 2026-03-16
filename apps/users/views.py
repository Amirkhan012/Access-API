from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .mixins import SessionCookieMixin
from .serializers import LoginSerializer, RegisterSerializer, UserProfileSerializer
from .services import (
    authenticate_user,
    create_user_session,
    deactivate_session,
    get_client_ip,
    register_user,
    soft_delete_user,
)


class RegisterView(APIView):
    """Регистрирует нового пользователя."""

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        """Создаёт нового пользователя."""
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = register_user(validated_data=dict(serializer.validated_data))
        response_data = UserProfileSerializer(user).data
        return Response(response_data, status=status.HTTP_201_CREATED)


class LoginView(SessionCookieMixin, APIView):
    """Авторизует пользователя и создаёт кастомную сессию."""

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        """Проверяет email и пароль, затем ставит cookie сессии."""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate_user(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )
        if user is None:
            return self.invalid_credentials_response()

        session = create_user_session(
            user=user,
            ip_address=get_client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )

        response = Response(
            UserProfileSerializer(user).data,
            status=status.HTTP_200_OK,
        )
        self.set_session_cookie(response, session)
        return response


class LogoutView(SessionCookieMixin, APIView):
    """Выход из текущей пользовательской сессии."""

    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        """Деактивирует текущую сессию и очищает cookie."""
        if not request.user.is_authenticated:
            return self.unauthorized_response()

        session = getattr(request, "auth_session", None)
        if session is None:
            return self.unauthorized_response()

        deactivate_session(session=session)

        response = Response(status=status.HTTP_204_NO_CONTENT)
        self.delete_session_cookie(response)
        return response


class MeView(SessionCookieMixin, APIView):
    """Возвращает и обновляет профиль текущего пользователя."""

    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        """Возвращает профиль текущего пользователя."""
        if not request.user.is_authenticated:
            return self.unauthorized_response()

        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request: Request) -> Response:
        """Обновляет профиль текущего пользователя."""
        if not request.user.is_authenticated:
            return self.unauthorized_response()

        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class DeleteAccountView(SessionCookieMixin, APIView):
    """Мягко деактивирует аккаунт текущего пользователя."""

    permission_classes = [AllowAny]

    def delete(self, request: Request) -> Response:
        """Деактивирует пользователя, его сессии и очищает cookie."""
        if not request.user.is_authenticated:
            return self.unauthorized_response()

        soft_delete_user(user=request.user)

        response = Response(status=status.HTTP_204_NO_CONTENT)
        self.delete_session_cookie(response)
        return response
