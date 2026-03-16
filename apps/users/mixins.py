from django.conf import settings
from rest_framework import status
from rest_framework.response import Response

from .models import UserSession


class SessionCookieMixin:
    """Работает с кастомной session cookie."""

    session_cookie_name: str = getattr(
        settings,
        "AUTH_SESSION_COOKIE_NAME",
        "sessionid",
    )
    session_cookie_max_age: int = getattr(
        settings,
        "AUTH_SESSION_COOKIE_MAX_AGE",
        60 * 60 * 24 * 7,
    )
    session_cookie_secure: bool = getattr(
        settings,
        "AUTH_SESSION_COOKIE_SECURE",
        False,
    )
    session_cookie_httponly: bool = True
    session_cookie_samesite: str = "Lax"

    def set_session_cookie(
        self,
        response: Response,
        session: UserSession,
    ) -> None:
        """Устанавливает cookie с ключом пользовательской сессии."""
        response.set_cookie(
            key=self.session_cookie_name,
            value=session.session_key,
            max_age=self.session_cookie_max_age,
            httponly=self.session_cookie_httponly,
            secure=self.session_cookie_secure,
            samesite=self.session_cookie_samesite,
        )

    def delete_session_cookie(self, response: Response) -> None:
        """Удаляет session cookie."""
        response.delete_cookie(
            key=self.session_cookie_name,
            samesite=self.session_cookie_samesite,
        )

    def unauthorized_response(self) -> Response:
        """Возвращает ответ 401."""
        return Response(
            {"detail": "Требуется авторизация."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    def invalid_credentials_response(self) -> Response:
        """Возвращает ответ 401 при неверных учётных данных."""
        return Response(
            {"detail": "Неверный email или пароль."},
            status=status.HTTP_401_UNAUTHORIZED,
        )
