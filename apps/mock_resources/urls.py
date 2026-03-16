from django.urls import path

from .views import MockOrderDetailView, MockOrderListCreateView

urlpatterns = [
    path("orders/", MockOrderListCreateView.as_view(), name="mock-order-list-create"),
    path("orders/<int:order_id>/", MockOrderDetailView.as_view(), name="mock-order-detail"),
]
