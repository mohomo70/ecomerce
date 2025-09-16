"""
Filters for catalog models.
"""
import django_filters
from django.db.models import Q
from .models import Product, Category


class ProductFilter(django_filters.FilterSet):
    """Filter for Product model."""
    category = django_filters.CharFilter(field_name='category__slug')
    min_price = django_filters.NumberFilter(method='filter_min_price')
    max_price = django_filters.NumberFilter(method='filter_max_price')
    in_stock = django_filters.BooleanFilter(method='filter_in_stock')
    rating = django_filters.NumberFilter(method='filter_rating')
    
    class Meta:
        model = Product
        fields = ['category', 'min_price', 'max_price', 'in_stock', 'rating']
    
    def filter_min_price(self, queryset, name, value):
        """Filter by minimum price."""
        return queryset.filter(variants__price__gte=value)
    
    def filter_max_price(self, queryset, name, value):
        """Filter by maximum price."""
        return queryset.filter(variants__price__lte=value)
    
    def filter_in_stock(self, queryset, name, value):
        """Filter by stock availability."""
        if value:
            return queryset.filter(variants__stock__gt=0)
        return queryset
    
    def filter_rating(self, queryset, name, value):
        """Filter by minimum rating (placeholder for future reviews)."""
        # This is a placeholder for when reviews are implemented
        # For now, just return the queryset unchanged
        return queryset