from django.db import models
#from django.contrib.auth import get_user_model

#User = get_user_model()


class Category(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    cover = models.ImageField(upload_to="product_cover/", blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    new_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # скидка
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)

    def __str__(self):
        return self.title


class Banner(models.Model):
    LOCATION_CHOICES = [
        ("index_head", "Index Head"),
        ("index_middle", "Index Middle"),
    ]
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to="banners/")
    location = models.CharField(max_length=50, choices=LOCATION_CHOICES)

    def __str__(self):
        return f"{self.title} ({self.location})"


class Basket(models.Model):
    #user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="basket")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def update_total(self):
        total = sum(item.get_subtotal() for item in self.items.all())
        self.total_price = total
        self.save()


class BasketItems(models.Model):
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def get_subtotal(self):
        return (self.product.new_price or self.product.price) * self.quantity


class Order(models.Model):
    STATUS_CHOICES = [
        ("Создан", "Создан"),
        ("Оплачен", "Оплачен"),
        ("В обработке", "В обработке"),
        ("Доставлен", "Доставлен"),
    ]
    #user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Создан")
    created_at = models.DateTimeField(auto_now_add=True)


class OrderItems(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def get_subtotal(self):
        return (self.product.new_price or self.product.price) * self.quantity
