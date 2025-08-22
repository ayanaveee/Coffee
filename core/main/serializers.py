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

#
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    transaction_id = serializers.CharField(read_only=True)
    payment_method = serializers.CharField(read_only=True)
    pickup_at = serializers.DateTimeField(read_only=True)
    voucher_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "transaction_id",
            "total_price",
            "voucher_amount",
            "payment_method",
            "pickup_at",
            "status",
            "created_at",
            "items"
        ]


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
