"""
Views for catalog models.
"""
import time
import logging
from django.db import connections
from django.db.models import Q, Prefetch
from django.contrib.postgres.search import SearchVector
from rest_framework import generics, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product, Variant, Media
from .serializers import (
    CategorySerializer, ProductListSerializer, ProductDetailSerializer
)
from .filters import ProductFilter

logger = logging.getLogger(__name__)


class CategoryListView(generics.ListAPIView):
    """List all categories."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    permission_classes = []  # Allow public access


class ProductListView(generics.ListAPIView):
    """List products with filtering, searching, and pagination."""
    queryset = Product.objects.select_related('category').prefetch_related(
        'variants', 'media'
    ).filter(is_active=True)
    serializer_class = ProductListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'variants__sku']
    ordering_fields = ['name', 'created_at', 'variants__price']
    ordering = ['-created_at']
    permission_classes = []  # Allow public access
    
    def get_queryset(self):
        """Optimize queryset for list view."""
        start_time = time.time()
        
        queryset = super().get_queryset()
        
        # Apply search if provided
        search = self.request.query_params.get('search')
        if search:
            # Use database-appropriate search
            if connections['default'].vendor == 'postgresql':
                # PostgreSQL full-text search
                queryset = queryset.annotate(
                    search=SearchVector('name', weight='A') + 
                           SearchVector('description', weight='B')
                ).filter(search=search)
            else:
                # SQLite fallback - use icontains for basic search
                queryset = queryset.filter(
                    Q(name__icontains=search) |
                    Q(description__icontains=search) |
                    Q(variants__sku__icontains=search)
                )
        
        # Apply category filter
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Apply price range filter
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price or max_price:
            price_filter = Q()
            if min_price:
                price_filter &= Q(variants__price__gte=min_price)
            if max_price:
                price_filter &= Q(variants__price__lte=max_price)
            queryset = queryset.filter(price_filter)
        
        # Apply in-stock filter
        in_stock = self.request.query_params.get('in_stock')
        if in_stock and in_stock.lower() == 'true':
            queryset = queryset.filter(variants__stock__gt=0)
        
        # Log query time
        db_time = time.time() - start_time
        logger.info(f"Product list query time: {db_time:.3f}s")
        
        return queryset.distinct()


class ProductDetailView(generics.RetrieveAPIView):
    """Retrieve a single product with all details."""
    queryset = Product.objects.select_related('category').prefetch_related(
        'variants', 'media'
    ).filter(is_active=True)
    serializer_class = ProductDetailSerializer
    lookup_field = 'slug'
    permission_classes = []  # Allow public access
    
    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to log query time."""
        start_time = time.time()
        response = super().retrieve(request, *args, **kwargs)
        db_time = time.time() - start_time
        logger.info(f"Product detail query time: {db_time:.3f}s")
        return response


@api_view(['GET'])
@permission_classes([])  # Allow public access
def product_stats(request):
    """Get product statistics."""
    start_time = time.time()
    
    stats = {
        'total_products': Product.objects.filter(is_active=True).count(),
        'total_categories': Category.objects.count(),
        'total_variants': Variant.objects.filter(is_active=True).count(),
        'in_stock_products': Product.objects.filter(
            is_active=True,
            variants__stock__gt=0
        ).distinct().count(),
    }
    
    db_time = time.time() - start_time
    logger.info(f"Product stats query time: {db_time:.3f}s")
    
    return Response(stats)