from django.db import models
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVector
from django.utils.text import slugify


class Category(models.Model):
    """
    Product category model with hierarchical structure.
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    """
    Product model with search capabilities.
    """
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    attributes = models.JSONField(default=dict, help_text="Product attributes as JSON")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['created_at']),
            GinIndex(fields=['attributes']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    @property
    def search_vector(self):
        """Create search vector for full-text search."""
        return SearchVector('name', weight='A') + SearchVector('description', weight='B')


class Variant(models.Model):
    """
    Product variant model with SKU, price, and stock.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    sku = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200, blank=True)
    attributes = models.JSONField(default=dict, help_text="Variant attributes as JSON")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['sku']
        indexes = [
            models.Index(fields=['product', 'is_active']),
            models.Index(fields=['price']),
            models.Index(fields=['stock']),
            GinIndex(fields=['attributes']),
        ]
    
    def __str__(self):
        return f"{self.product.name} - {self.name or self.sku}"
    
    @property
    def is_in_stock(self):
        """Check if variant is in stock."""
        return self.stock > 0


class Media(models.Model):
    """
    Product media model for images and other files.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='media')
    url = models.URLField()
    alt_text = models.CharField(max_length=200, blank=True)
    media_type = models.CharField(max_length=50, default='image')
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['sort_order', 'created_at']
    
    def __str__(self):
        return f"{self.product.name} - {self.alt_text or 'Media'}"
