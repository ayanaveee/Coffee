from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Basket, BasketItems, Product, Order, OrderItems
from .serializers import (
    BasketItemsCreateSerializer,
    BasketItemsSerializer,
    OrderSerializer,
    CheckoutSerializer,
)


class BasketItemsCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = BasketItemsCreateSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            basket_item = serializer.save()
            return Response(BasketItemsSerializer(basket_item).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        basket_id = serializer.validated_data["basket_id"]
        basket = get_object_or_404(Basket, id=basket_id, user=request.user)

        order = Order.objects.create(
            user=request.user,
            total_price=basket.total_price,
            status="Создан"
        )

        for item in basket.items.all():
            OrderItems.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity
            )

        basket.items.all().delete()
        basket.update_total()

        return Response({"detail": f"Заказ #{order.id} создан успешно."}, status=status.HTTP_201_CREATED)


class OrderListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by("-created_at")
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


class OrderDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id):
        order = get_object_or_404(Order, id=id, user=request.user)
        serializer = OrderSerializer(order)
        return Response(serializer.data)
