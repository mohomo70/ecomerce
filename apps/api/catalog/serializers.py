"""
Serializers for catalog models.
"""
from rest_framework import serializers
from .models import Category, Product, Variant, Media


class MediaSerializer(serializers.ModelSerializer):
    """Serializer for Media model."""
    
    class Meta:
        model = Media
        fields = ['id', 'url', 'alt_text', 'media_type', 'sort_order']


class VariantSerializer(serializers.ModelSerializer):
    """Serializer for Variant model."""
    is_in_stock = serializers.ReadOnlyField()
    
    class Meta:
        model = Variant
        fields = ['id', 'sku', 'name', 'attributes', 'price', 'stock', 'is_in_stock', 'is_active']


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model."""
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'parent', 'description', 'children', 'created_at']
    
    def get_children(self, obj):
        """Get child categories."""
        children = obj.children.all()
        return CategorySerializer(children, many=True).data


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer for Product list view."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    price_range = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()
    primary_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'category', 'category_name',
            'attributes', 'is_active', 'price_range', 'in_stock', 'primary_image',
            'created_at'
        ]
    
    def get_price_range(self, obj):
        """Get price range from variants."""
        variants = obj.variants.filter(is_active=True)
        if not variants.exists():
            return None
        
        prices = [v.price for v in variants]
        min_price = min(prices)
        max_price = max(prices)
        
        if min_price == max_price:
            return f"${min_price}"
        return f"${min_price} - ${max_price}"
    
    def get_in_stock(self, obj):
        """Check if any variant is in stock."""
        return obj.variants.filter(is_active=True, stock__gt=0).exists()
    
    def get_primary_image(self, obj):
        """Get primary image URL."""
        primary_media = obj.media.filter(media_type='image').first()
        return primary_media.url if primary_media else None


class ProductDetailSerializer(serializers.ModelSerializer):
    """Serializer for Product detail view."""
    category = CategorySerializer(read_only=True)
    variants = VariantSerializer(many=True, read_only=True)
    media = MediaSerializer(many=True, read_only=True)
    price_range = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'category', 'attributes',
            'is_active', 'variants', 'media', 'price_range', 'in_stock',
            'created_at', 'updated_at'
        ]
    
    def get_price_range(self, obj):
        """Get price range from variants."""
        variants = obj.variants.filter(is_active=True)
        if not variants.exists():
            return None
        
        prices = [v.price for v in variants]
        min_price = min(prices)
        max_price = max(prices)
        
        if min_price == max_price:
            return f"${min_price}"
        return f"${min_price} - ${max_price}"
    
    def get_in_stock(self, obj):
        """Check if any variant is in stock."""
        return obj.variants.filter(is_active=True, stock__gt=0).exists()