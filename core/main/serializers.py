from rest_framework import serializers
from .models import *


#Категория
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "title"]


#Товары
class ProductListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = ["id", "title", "price", "new_price", "rating", "cover", "category"]

#Детальная страница товаров
class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = "__all__"


#Баннеры
class BannerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ["id", "title", "image", "location"]


#Корзина
class BasketItemsSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)

    class Meta:
        model = BasketItems
        fields = ["id", "product", "quantity"]

#Создание корзины
class BasketItemsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BasketItems
        fields = ["product", "quantity"]

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Количество должно быть больше 0")
        return value

    def create(self, validated_data):
        request = self.context.get("request")
        basket, _ = Basket.objects.get_or_create(user=request.user)

        basket_item, created = BasketItems.objects.get_or_create(
            basket=basket,
            product=validated_data["product"],
            defaults={"quantity": validated_data["quantity"]}
        )
        if not created:
            basket_item.quantity += validated_data["quantity"]
            basket_item.save()

        basket.update_total()
        return basket_item


#Оформление заказа
class CheckoutSerializer(serializers.Serializer):
    basket_id = serializers.IntegerField()


#Детали заказа
class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)

    class Meta:
        model = OrderItems
        fields = ["id", "product", "quantity"]

class OrderPaySerializer(serializers.Serializer):
    payment_method = serializers.ChoiceField(choices=["Card", "MBank", "Cash"])

    # --- для карты ---
    card_number = serializers.CharField(required=False, min_length=16, max_length=16)
    card_name = serializers.CharField(required=False, max_length=100)
    card_expiry = serializers.CharField(required=False, max_length=5)  # MM/YY
    card_cvv = serializers.CharField(required=False, min_length=3, max_length=4)

    # --- для MBank ---
    phone_number = serializers.CharField(required=False, max_length=15)
    otp = serializers.CharField(required=False, max_length=6)

    def validate(self, data):
        method = data.get("payment_method")

        if method == "Card":
            required_fields = ["card_number", "card_name", "card_expiry", "card_cvv"]
            for field in required_fields:
                if not data.get(field):
                    raise serializers.ValidationError({field: "Это поле обязательно для оплаты картой"})

        elif method == "MBank":
            if not data.get("phone_number"):
                raise serializers.ValidationError({"phone_number": "Укажите номер телефона для MBank"})

        elif method == "Cash":
            # никаких доп.полей не нужно
            pass

        return data

#Заказ (вложенные позиции с суммой)
class OrderItemsNestedSerializer(serializers.ModelSerializer):
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItems
        fields = ("product", "quantity", "subtotal")

    def get_subtotal(self, obj):
        return (obj.product.new_price or obj.product.price) * obj.quantity


class OrderNestedSerializer(serializers.ModelSerializer):
    items = OrderItemsNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ("id", "total_price", "status", "created_at", "items")
