from rest_framework.authentication import BaseAuthentication
from rest_framework.request import Request

from .models import User, UserSession


class CustomSessionAuthentication(BaseAuthentication):
    """Передаёт пользователя из кастомной cookie-сессии в DRF."""

    def authenticate(
        self,
        request: Request,
    ) -> tuple[User, UserSession] | None:
        """Возвращает пользователя и активную сессию."""
        user = getattr(request._request, "user", None)
        session = getattr(request._request, "auth_session", None)

        if user is None or not user.is_authenticated or session is None:
            return None

        return user, session
