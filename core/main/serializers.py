from rest_framework import serializers
from .models import Product, Category, Banner, Basket, BasketItems, Order, OrderItems


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



class BasketItemsSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)

    class Meta:
        model = BasketItems
        fields = ["id", "product", "quantity"]


class BasketItemsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BasketItems
        fields = ["product", "quantity"]

    def create(self, validated_data):
        request = self.context.get("request")
        basket, created = Basket.objects.get_or_create(user=request.user)

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


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "total_price", "status", "created_at", "items"]
