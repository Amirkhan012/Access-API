from typing import Callable

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest, HttpResponse

from .services import get_active_session, touch_session


class CustomSessionAuthMiddleware:
    """Подставляет пользователя в request по кастомной session cookie."""

    def __init__(
        self,
        get_response: Callable[[HttpRequest], HttpResponse],
    ) -> None:
        """Сохраняет следующий обработчик цепочки middleware."""
        self.get_response = get_response
        self.session_cookie_name: str = getattr(
            settings,
            "AUTH_SESSION_COOKIE_NAME",
            "auth_session",
        )

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Добавляет в request пользователя и сессию, если cookie валидна."""
        request.user = AnonymousUser()
        request.auth_session = None

        session_key = request.COOKIES.get(self.session_cookie_name)
        if session_key:
            session = get_active_session(session_key=session_key)
            if session is not None:
                touch_session(session=session)
                request.user = session.user
                request.auth_session = session

        response = self.get_response(request)
        return response
