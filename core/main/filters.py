import django_filters
from .models import Product

class ProductFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(field_name="title", lookup_expr="icontains")

    class Meta:
        model = Product
        fields = ["category", "search"]
