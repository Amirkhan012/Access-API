from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.access.services import has_permission

from .models import MockOrder

MOCK_RESOURCE_CODE = "mock_orders"


def require_mock_access(request: Request, action_code: str) -> Response | None:
    """Проверяет доступ к mock-ресурсу."""
    if not request.user.is_authenticated:
        return Response(
            {"detail": "Требуется авторизация."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if not has_permission(
        user=request.user,
        resource_code=MOCK_RESOURCE_CODE,
        action_code=action_code,
    ):
        return Response(
            {"detail": f"Нет права {action_code} для ресурса {MOCK_RESOURCE_CODE}."},
            status=status.HTTP_403_FORBIDDEN,
        )

    return None


def serialize_order(order: MockOrder) -> dict[str, int | str]:
    """Собирает данные заказа для ответа."""
    return {
        "id": order.id,
        "title": order.title,
        "status": order.status,
        "amount": order.amount,
    }


class MockOrderListCreateView(APIView):
    """Показывает список mock-заказов и создаёт новый."""

    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        """Возвращает список mock-заказов."""
        error_response = require_mock_access(request, "read")
        if error_response is not None:
            return error_response

        orders = MockOrder.objects.all()
        data = [serialize_order(order) for order in orders]
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        """Создаёт новый mock-заказ."""
        error_response = require_mock_access(request, "create")
        if error_response is not None:
            return error_response

        title = request.data.get("title")
        amount = request.data.get("amount")
        order_status = request.data.get("status", "new")

        if not title or amount is None:
            return Response(
                {"detail": "Поля title и amount обязательны."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order = MockOrder.objects.create(
            title=str(title).strip(),
            status=str(order_status).strip() or "new",
            amount=amount,
        )
        return Response(serialize_order(order), status=status.HTTP_201_CREATED)


class MockOrderDetailView(APIView):
    """Возвращает, обновляет и удаляет один mock-заказ."""

    permission_classes = [AllowAny]

    def get(self, request: Request, order_id: int) -> Response:
        """Возвращает один mock-заказ."""
        error_response = require_mock_access(request, "read")
        if error_response is not None:
            return error_response

        order = MockOrder.objects.filter(id=order_id).first()
        if order is None:
            return Response(
                {"detail": "Mock-заказ не найден."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(serialize_order(order), status=status.HTTP_200_OK)

    def patch(self, request: Request, order_id: int) -> Response:
        """Обновляет mock-заказ."""
        error_response = require_mock_access(request, "update")
        if error_response is not None:
            return error_response

        order = MockOrder.objects.filter(id=order_id).first()
        if order is None:
            return Response(
                {"detail": "Mock-заказ не найден."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if "title" in request.data:
            order.title = str(request.data["title"]).strip()
        if "status" in request.data:
            order.status = str(request.data["status"]).strip()
        if "amount" in request.data:
            order.amount = request.data["amount"]

        order.save()
        return Response(serialize_order(order), status=status.HTTP_200_OK)

    def delete(self, request: Request, order_id: int) -> Response:
        """Удаляет mock-заказ."""
        error_response = require_mock_access(request, "delete")
        if error_response is not None:
            return error_response

        order = MockOrder.objects.filter(id=order_id).first()
        if order is None:
            return Response(
                {"detail": "Mock-заказ не найден."},
                status=status.HTTP_404_NOT_FOUND,
            )

        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
