from django.db import models
from django.contrib.auth import get_user_model
import secrets
import string

User = get_user_model()

# ---------------- КАТЕГОРИЯ ----------------
class Category(models.Model):
    title = models.CharField("Название категории", max_length=100)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["title"]

    def __str__(self):
        return self.title


# ---------------- ТОВАР ----------------
class Product(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products", verbose_name="Категория"
    )
    title = models.CharField("Название", max_length=200)
    description = models.TextField("Описание", blank=True)
    cover = models.ImageField("Обложка", upload_to="product_cover/", blank=True, null=True)
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    new_price = models.DecimalField("Цена со скидкой", max_digits=10, decimal_places=2, null=True, blank=True)
    rating = models.DecimalField("Рейтинг", max_digits=3, decimal_places=1, default=0.0)
    is_best_seller = models.BooleanField("Бестселлер", default=False)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ["title"]

    def __str__(self):
        return self.title

    def get_price(self):
        return self.new_price or self.price


# ---------------- БАННЕР ----------------
class Banner(models.Model):
    LOCATION_CHOICES = [
        ("index_head", "Баннер сверху"),
        ("index_middle", "Дополнительный баннер"),
    ]
    title = models.CharField("Заголовок", max_length=255)
    image = models.ImageField("Изображение", upload_to="banners/")
    location = models.CharField("Расположение", max_length=50, choices=LOCATION_CHOICES)

    class Meta:
        verbose_name = "Баннер"
        verbose_name_plural = "Баннеры"
        ordering = ["location"]

    def __str__(self):
        return f"{self.title} ({self.location})"

class CoffeeShop(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название кофейни")
    banner = models.ImageField(upload_to="coffee_banners/", verbose_name="Баннер")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "О кофейне"
        verbose_name_plural = "О кофейнях"

# ---------------- КОРЗИНА ----------------
class Basket(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="basket")
    total_price = models.DecimalField("Общая сумма", max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    def update_total(self):
        total = sum(item.get_subtotal() for item in self.items.all())
        self.total_price = total
        self.save()

    def __str__(self):
        return f"Корзина #{self.pk} - {self.total_price} сом"


class BasketItems(models.Model):
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE, related_name="items", verbose_name="Корзина")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.PositiveIntegerField("Количество", default=1)

    class Meta:
        verbose_name = "Товар в корзине"
        verbose_name_plural = "Товары в корзине"

    def get_subtotal(self):
        return self.product.get_price() * self.quantity

    def __str__(self):
        return f"{self.product.title} × {self.quantity}"


# ---------------- ЗАКАЗ ----------------
class Order(models.Model):
    STATUS_CHOICES = [
        ("Создан", "Создан"),
        ("Оплачен", "Оплачен"),
        ("В обработке", "В обработке"),
        ("Доставлен", "Доставлен"),
    ]
    PAYMENT_METHODS = [
        ("Card", "Карта"),
        ("Cash", "Наличные"),
        ("Online", "Онлайн-платёж"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    total_price = models.DecimalField("Общая сумма", max_digits=10, decimal_places=2)
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default="Создан")
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    transaction_id = models.CharField("ID транзакции", max_length=50, unique=True, null=True, blank=True)
    payment_method = models.CharField("Метод оплаты", max_length=20, choices=PAYMENT_METHODS, null=True, blank=True)

    # --- поля для имитации оплаты ---
    card_number = models.CharField("Номер карты", max_length=16, null=True, blank=True)
    card_name = models.CharField("Имя на карте", max_length=100, null=True, blank=True)
    card_expiry = models.CharField("Срок действия (MM/YY)", max_length=5, null=True, blank=True)
    card_cvv = models.CharField("CVV", max_length=4, null=True, blank=True)

    phone_number = models.CharField("Телефон (для MBank)", max_length=15, null=True, blank=True)

    confirm_code = models.CharField("Код подтверждения", max_length=6, null=True, blank=True)
    is_confirmed = models.BooleanField("Оплата подтверждена", default=False)

    def ensure_transaction_id(self):
        if not self.transaction_id:
            alphabet = string.ascii_uppercase + string.digits
            self.transaction_id = "T" + ''.join(secrets.choice(alphabet) for _ in range(12))

    def save(self, *args, **kwargs):
        self.ensure_transaction_id()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Заказ #{self.pk} - {self.status}"

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ["-created_at"]



class OrderItems(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", verbose_name="Заказ")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.PositiveIntegerField("Количество", default=1)

    class Meta:
        verbose_name = "Товар в заказе"
        verbose_name_plural = "Товары в заказе"

    def get_subtotal(self):
        return self.product.get_price() * self.quantity

    def __str__(self):
        return f"{self.product.title} × {self.quantity}"


# ---------------- АКЦИИ ----------------
class Promotion(models.Model):
    title = models.CharField("Название акции", max_length=200)
    description = models.TextField("Описание", blank=True)
    discount_percent = models.PositiveIntegerField("Скидка %")
    start_date = models.DateField("Начало")
    end_date = models.DateField("Конец")
    products = models.ManyToManyField(Product, verbose_name="Товары в акции", blank=True)

    class Meta:
        verbose_name = "Акция"
        verbose_name_plural = "Акции"

    def __str__(self):
        return f"{self.title} ({self.discount_percent}%)"


# ---------------- ОТЗЫВЫ ----------------
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviews")
    rating = models.PositiveSmallIntegerField("Оценка (1-5)", default=5)
    comment = models.TextField("Комментарий", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.product.title} - {self.rating}⭐"


# ---------------- ИНГРЕДИЕНТЫ ----------------
class Ingredient(models.Model):
    title = models.CharField("Название", max_length=100)
    is_allergen = models.BooleanField("Аллерген", default=False)

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return self.title


class ProductIngredient(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="ingredients")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.CharField("Количество", max_length=50, blank=True)

    class Meta:
        verbose_name = "Ингредиент в продукте"
        verbose_name_plural = "Ингредиенты в продуктах"

    def __str__(self):
        return f"{self.ingredient.title} для {self.product.title}"


# ---------------- СКЛАД ----------------
class Stock(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="stock")
    quantity = models.PositiveIntegerField("Количество на складе", default=0)

    class Meta:
        verbose_name = "Склад"
        verbose_name_plural = "Складские остатки"

    def __str__(self):
        return f"{self.product.title} - {self.quantity} шт."


# ---------------- ТОЧКИ САМОВЫВОЗА ----------------
class PickupPoint(models.Model):
    title = models.CharField("Название точки", max_length=200)
    address = models.CharField("Адрес", max_length=255)
    phone = models.CharField("Телефон", max_length=20, blank=True)

    class Meta:
        verbose_name = "Точка самовывоза"
        verbose_name_plural = "Точки самовывоза"

    def __str__(self):
        return self.title

# ---------------- ТОЧКИ САМОВЫВОЗА ----------------
class PickupPoint(models.Model):
    title = models.CharField("Название точки", max_length=200)
    address = models.CharField("Адрес", max_length=255)
    phone = models.CharField("Телефон", max_length=20, blank=True)

    class Meta:
        verbose_name = "Точка самовывоза"
        verbose_name_plural = "Точки самовывоза"

    def __str__(self):
        return self.title

