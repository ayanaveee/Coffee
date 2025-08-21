from django.urls import path
from .views import (
    BasketItemsCreateView,
    CheckoutAPIView,
    OrderListAPIView,
    OrderDetailAPIView,
)

urlpatterns = [
    path("basket/add/", BasketItemsCreateView.as_view(), name="basket-add"),
    path("checkout/", CheckoutAPIView.as_view(), name="checkout"),
    path("orders/", OrderListAPIView.as_view(), name="order-list"),
    path("orders/<int:id>/", OrderDetailAPIView.as_view(), name="order-detail"),
]
