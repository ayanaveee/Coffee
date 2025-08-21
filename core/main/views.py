from rest_framework import generics, permissions, serializers
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ProductFilter
from .models import (
    Basket, BasketItems, Product, Order, OrderItems, Category, Banner
)
from .serializers import (
    BasketItemsCreateSerializer,
    BasketItemsSerializer,
    OrderSerializer,
    CheckoutSerializer,
    ProductListSerializer,
    CategorySerializer,
    OrderNestedSerializer,
    BannerListSerializer,
)

# -------------------- Pagination --------------------
class ProductPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50

# -------------------- Index API --------------------
class IndexAPIView(generics.GenericAPIView):
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter
    pagination_class = ProductPagination

    def get(self, request):
        top_banner = Banner.objects.filter(location="index_head")
        middle_banner = Banner.objects.filter(location="index_middle")

        categories = Category.objects.all()[:3]
        categories_data = CategorySerializer(categories, many=True).data

        products_qs = Product.objects.all()
        filtered_products = self.filter_queryset(products_qs)
        paginated_products = self.paginate_queryset(filtered_products)
        products_data = ProductListSerializer(paginated_products, many=True).data

        return Response({
            "top_banner": BannerListSerializer(top_banner, many=True).data if top_banner else None,
            "middle_banner": BannerListSerializer(middle_banner, many=True).data if middle_banner else None,
            "categories": categories_data,
            "products": products_data,
            "pagination": self.get_paginated_response(products_data).data if paginated_products else None
        })


# -------------------- Basket Items --------------------
class BasketItemsCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BasketItemsCreateSerializer

    def get_serializer_context(self):
        return {"request": self.request}

    def perform_create(self, serializer):
        basket, _ = Basket.objects.get_or_create(user=self.request.user)
        product = serializer.validated_data["product"]
        quantity = serializer.validated_data["quantity"]

        basket_item, created = BasketItems.objects.get_or_create(
            basket=basket, product=product,
            defaults={"quantity": quantity}
        )
        if not created:
            basket_item.quantity += quantity
            basket_item.save()

        basket.update_total()

class BasketItemsListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BasketItemsSerializer

    def get_queryset(self):
        basket, _ = Basket.objects.get_or_create(user=self.request.user)
        return basket.items.all()

# -------------------- Checkout --------------------
class CheckoutAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CheckoutSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        basket_id = serializer.validated_data["basket_id"]
        basket = get_object_or_404(Basket, id=basket_id, user=request.user)

        if not basket.items.exists():
            return Response({"detail": "Корзина пуста."}, status=400)

        total = sum((item.product.new_price or item.product.price) * item.quantity for item in basket.items.all())
        order = Order.objects.create(user=request.user, total_price=total, status="Создан")

        for item in basket.items.all():
            OrderItems.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity
            )

        basket.items.all().delete()
        basket.update_total()

        return Response({"detail": f"Заказ #{order.id} создан успешно."}, status=201)


# -------------------- Orders --------------------
class OrderListAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderNestedSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by("-created_at")

class OrderDetailAPIView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderNestedSerializer
    lookup_field = "id"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
