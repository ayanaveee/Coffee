from rest_framework import serializers
from .models import *

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "title"]

class ProductListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = ["id", "title", "price", "new_price", "rating", "cover", "category"]

class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = "__all__"

class BannerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ["id", "title", "image", "location"]

class CoffeeShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoffeeShop
        fields = ["id", "name", "banner", "description"]

class BasketItemsSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)

    class Meta:
        model = BasketItems
        fields = ["id", "product", "quantity"]

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

class CheckoutSerializer(serializers.Serializer):
    basket_id = serializers.IntegerField()

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)

    class Meta:
        model = OrderItems
        fields = ["id", "product", "quantity"]

class OrderPaySerializer(serializers.Serializer):
    payment_method = serializers.ChoiceField(choices=["Card", "MBank", "Cash"])

    card_number = serializers.CharField(required=False, min_length=16, max_length=16)
    card_name = serializers.CharField(required=False, max_length=100)
    card_expiry = serializers.CharField(required=False, max_length=5)  # MM/YY
    card_cvv = serializers.CharField(required=False, min_length=3, max_length=4)

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
            pass

        return data

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
