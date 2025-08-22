from rest_framework import generics, permissions, status
from rest_framework.views import APIView
import random
import uuid
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ProductFilter
from .models import *
from .serializers import *

#Главная страница
class IndexAPIView(generics.GenericAPIView):
    filter_backends = [DjangoFilterBackend]

    def get(self, request):
        # Топ-баннеры
        top_banner = Banner.objects.filter(location="index_head")
        top_banner_data = BannerListSerializer(top_banner, many=True).data

        # Бестселлеры (топ-5 продуктов)
        best_sellers = Product.objects.filter(is_best_seller=True)[:5]
        best_sellers_data = ProductListSerializer(best_sellers, many=True).data

        # Информация о кофейне
        about_coffee = {
            "image": "/media/about_coffee.jpg",
            "text": "Добро пожаловать в нашу кофейню! Здесь варят лучший кофе."
        }

        # Цитата
        quote = "Жизнь слишком коротка, чтобы пить плохой кофе ☕️"

        # Категории товаров
        categories = Category.objects.all()
        categories_data = CategorySerializer(categories, many=True).data

        # Футер
        footer = {
            "address": "ул. Примерная, 12",
            "email": "mochamuse@gmail.com",
            "phone": "+996 555 123456",
            "social": {
                "instagram": "https://instagram.com",
                "facebook": "https://facebook.com"
            }
        }

        return Response({
            "top_banner": top_banner_data,
            "best_sellers": best_sellers_data,
            "about_coffee": about_coffee,
            "quote": quote,
            "categories": categories_data,
            "footer": footer
        })



class ProductListAPIView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]
    filterset_class = ProductFilter
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'title', 'id']

#Детальная страница
class ProductDetailAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer
    permission_classes = [permissions.AllowAny]


class BasketItemsCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BasketItemsCreateSerializer

    def get_serializer_context(self):
        return {"request": self.request}

    def perform_create(self, serializer):
        basket, _ = Basket.objects.get_or_create(user=self.request.user)
        product = serializer.validated_data["product"]
        quantity = serializer.validated_data["quantity"]

        item, created = BasketItems.objects.get_or_create(
            basket=basket, product=product,
            defaults={"quantity": quantity}
        )
        if not created:
            item.quantity += quantity
            item.save()

        basket.update_total()


class BasketItemsListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BasketItemsSerializer

    def get_queryset(self):
        basket, _ = Basket.objects.get_or_create(user=self.request.user)
        return basket.items.all()


class BasketItemDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BasketItemsSerializer

    def get_queryset(self):
        basket, _ = Basket.objects.get_or_create(user=self.request.user)
        return basket.items.all()


class CheckoutAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CheckoutSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        basket = get_object_or_404(Basket, id=serializer.validated_data["basket_id"], user=request.user)
        if not basket.items.exists():
            return Response({"detail": "Корзина пуста."}, status=400)

        total = sum((item.product.new_price or item.product.price) * item.quantity for item in basket.items.all())
        order = Order.objects.create(user=request.user, total_price=total, status="Создан")

        for item in basket.items.all():
            OrderItems.objects.create(order=order, product=item.product, quantity=item.quantity)

        basket.items.all().delete()
        basket.update_total()

        return Response({"detail": f"Заказ #{order.id} создан успешно."}, status=201)


class OrderListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderNestedSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by("-created_at")


class OrderDetailAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderNestedSerializer
    lookup_field = "id"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderPaymentView(APIView):
    """
    Имитация оплаты (карта или MBank).
    """

    def post(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({"error": "Заказ не найден"}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderPaySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payment_method = serializer.validated_data["payment_method"]

        # --- ОПЛАТА КАРТОЙ ---
        if payment_method == "Card":
            card_number = serializer.validated_data["card_number"]

            # Фейковая проверка карты (например, VISA = 4****)
            if card_number.startswith("4"):
                order.transaction_id = str(uuid.uuid4())[:12]  # генерим ID транзакции
                order.status = "Оплачен"
                order.payment_method = "Card"
                order.save()
                return Response(
                    {
                        "message": "Оплата картой прошла успешно ✅",
                        "transaction_id": order.transaction_id
                    },
                    status=200
                )
            else:
                return Response({"error": "Оплата отклонена банком ❌"}, status=400)
        elif payment_method == "Cash":
            order.status = "Ожидает оплаты"
            order.payment_method = "Cash"
            order.save()
            return Response({"message": "Заказ создан. Оплата наличными при получении 💵"}, status=200)


        # --- ОПЛАТА ЧЕРЕЗ MBANK ---
        elif payment_method == "MBank":
            phone = serializer.validated_data["phone_number"]
            otp = serializer.validated_data.get("otp")

            if not otp:
                # Генерация OTP (фейковая отправка)
                generated_otp = str(random.randint(1000, 9999))
                order.confirm_code = generated_otp
                order.status = "Ожидает подтверждения"
                order.payment_method = "MBank"
                order.save()

                return Response(
                    {
                        "message": f"OTP отправлен на {phone}",
                        "test_otp": generated_otp  # ⚠️ в реале бы не отдавали клиенту
                    },
                    status=200
                )

            # Проверка OTP
            if otp == order.confirm_code:
                order.transaction_id = str(uuid.uuid4())[:12]
                order.status = "Оплачен"
                order.save()
                return Response(
                    {
                        "message": "Оплата через MBank подтверждена ✅",
                        "transaction_id": order.transaction_id
                    },
                    status=200
                )
            else:
                return Response({"error": "Неверный OTP ❌"}, status=400)

        return Response({"error": "Неверный метод оплаты"}, status=400)

class OrderReceiptAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        order = get_object_or_404(Order, id=id, user=request.user)

        created = timezone.localtime(order.created_at)
        items = []
        subtotal = 0

        for item in order.items.select_related("product"):
            price = item.product.new_price or item.product.price
            total = float(price) * item.quantity
            subtotal += total
            items.append({
                "title": item.product.title,
                "quantity": item.quantity,
                "price": float(price),
                "line_total": total,
                "options": []
            })

        receipt = {
            "success": order.status == "paid",
            "title": "Thank you!",
            "message": "Your transaction was successful" if order.status == "paid" else "Waiting for payment",
            "transaction_id": order.transaction_id,
            "date": created.strftime("%d %B %y"),
            "time": created.strftime("%I:%M %p"),
            "items": items,
            "payment_summary": {
                "price": round(subtotal, 2),
                "voucher": float(order.voucher_amount or 0),
                "total": float(order.total_price)
            },
            "payment_method": order.payment_method or "Card",
            "schedule_pickup": order.pickup_at.strftime("%I.%M %p") if order.pickup_at else None
        }

        return Response(receipt)
