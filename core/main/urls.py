from django.urls import path
from . import views

urlpatterns = [
    path("index/", views.IndexAPIView.as_view(), name="index"),

    path("products/", views.ProductListAPIView.as_view(), name="product_list"),
    path("products/<int:pk>/", views.ProductDetailAPIView.as_view(), name="product_detail"),

    path("basket/items/", views.BasketItemsListView.as_view(), name="basket_items_list"),
    path("basket/items/add/", views.BasketItemsCreateView.as_view(), name="basket_items_create"),
    path("basket/items/<int:pk>/", views.BasketItemDeleteView.as_view(), name="basket_item_delete"),

    path("checkout/", views.CheckoutAPIView.as_view(), name="checkout"),
    path("orders/", views.OrderListAPIView.as_view(), name="order_list"),
    path("orders/<int:id>/", views.OrderDetailAPIView.as_view(), name="order_detail"),
    path("/pay-order/<int:order_id>/", views.OrderPaymentView.as_view(), name="order_pay"),
    path("orders/<int:id>/receipt/", views.OrderReceiptAPIView.as_view(), name="order_receipt"),
]
