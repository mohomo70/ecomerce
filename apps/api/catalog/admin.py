from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Category, Product, Variant, Media


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent', 'created_at']
    list_filter = ['parent', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']


class MediaInline(admin.TabularInline):
    model = Media
    extra = 1
    fields = ['url', 'alt_text', 'media_type', 'sort_order']


class VariantInline(admin.TabularInline):
    model = Variant
    extra = 1
    fields = ['sku', 'name', 'price', 'stock', 'is_active']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'category', 'is_active', 'created_at', 'image_preview']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'variants__sku']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [VariantInline, MediaInline]
    ordering = ['-created_at']
    
    def image_preview(self, obj):
        """Show first product image as thumbnail."""
        first_media = obj.media.first()
        if first_media:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover;" />',
                first_media.url
            )
        return "No image"
    image_preview.short_description = "Image"


@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    list_display = ['sku', 'product', 'name', 'price', 'stock', 'is_in_stock', 'is_active']
    list_filter = ['is_active', 'product__category', 'created_at']
    search_fields = ['sku', 'name', 'product__name']
    ordering = ['sku']
    
    def is_in_stock(self, obj):
        """Show stock status with color coding."""
        if obj.stock > 0:
            return format_html('<span style="color: green;">✓ In Stock</span>')
        else:
            return format_html('<span style="color: red;">✗ Out of Stock</span>')
    is_in_stock.short_description = "Stock Status"


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ['product', 'alt_text', 'media_type', 'sort_order', 'image_preview']
    list_filter = ['media_type', 'created_at']
    search_fields = ['product__name', 'alt_text']
    ordering = ['product', 'sort_order']
    
    def image_preview(self, obj):
        """Show media as thumbnail."""
        if obj.media_type == 'image':
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover;" />',
                obj.url
            )
        return obj.media_type
    image_preview.short_description = "Preview"
