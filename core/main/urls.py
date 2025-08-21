from django.urls import path
from .views import (
    IndexAPIView,
    BasketItemsCreateView,
    BasketItemsListView,
    CheckoutAPIView,
    OrderListAPIView,
    OrderDetailAPIView,
)

urlpatterns = [
    path("index/", IndexAPIView.as_view(), name="index"),
    path("basket/items/", BasketItemsListView.as_view(), name="basket-items_list"),
    path("basket/items/add/", BasketItemsCreateView.as_view(), name="basket_items_create"),
    path("checkout/", CheckoutAPIView.as_view(), name="checkout"),
    path("orders/", OrderListAPIView.as_view(), name="order_list"),
    path("orders/<int:id>/", OrderDetailAPIView.as_view(), name="order_detail"),
]
