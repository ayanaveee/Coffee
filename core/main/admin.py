from django.contrib import admin
from .models import *

# ---------------- CATEGORY ----------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "title")
    search_fields = ("title",)
    ordering = ("id",)


# ---------------- COFFEE SHOP ----------------
@admin.register(CoffeeShop)
class CoffeeShopAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "banner")
    search_fields = ("name",)
    ordering = ("id",)


# ---------------- PRODUCT ----------------
class ProductIngredientInline(admin.TabularInline):
    model = ProductIngredient
    extra = 1
    autocomplete_fields = ("ingredient",)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "price", "new_price", "category")
    search_fields = ("title",)
    list_filter = ("category",)
    inlines = [ProductIngredientInline]

# ---------------- BANNER ----------------
@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "location", "image")
    search_fields = ("title",)
    list_filter = ("location",)
    ordering = ("id",)

# ---------------- BASKET ----------------
@admin.register(Basket)
class BasketAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "total_amount")
    search_fields = ("user__username",)
    ordering = ("id",)

    def total_amount(self, obj):
        return sum(item.product.price * item.quantity for item in obj.items.all())

    total_amount.short_description = "Total"


@admin.register(BasketItems)
class BasketItemsAdmin(admin.ModelAdmin):
    list_display = ("id", "basket", "product", "quantity")
    search_fields = ("basket__user__username", "product__title")
    ordering = ("id",)

# ---------------- ORDER ----------------
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "total_price", "status", "created_at")
    search_fields = ("user__username",)
    list_filter = ("status", "created_at")
    ordering = ("-created_at",)

@admin.register(OrderItems)
class OrderItemsAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "product", "quantity")
    search_fields = ("order__id", "product__title")
    ordering = ("id",)

# ---------------- PROMOTION ----------------
@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "discount_percent", "start_date", "end_date")
    search_fields = ("title",)
    list_filter = ("start_date", "end_date")
    filter_horizontal = ("products",)
    ordering = ("-start_date",)

# ---------------- REVIEW ----------------
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "user", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("product__title", "user__username", "comment")
    ordering = ("-created_at",)

# ---------------- INGREDIENTS ----------------
@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "is_allergen")
    list_filter = ("is_allergen",)
    search_fields = ("title",)
    ordering = ("id",)

@admin.register(ProductIngredient)
class ProductIngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "ingredient", "amount")
    autocomplete_fields = ("product", "ingredient")
    ordering = ("id",)

# ---------------- STOCK ----------------
@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "quantity")
    search_fields = ("product__title",)
    ordering = ("id",)

# ---------------- PICKUP POINTS ----------------
@admin.register(PickupPoint)
class PickupPointAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "address", "phone")
    search_fields = ("title", "address")
    ordering = ("id",)
