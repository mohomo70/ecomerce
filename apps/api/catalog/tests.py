from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from .models import Category, Product, Variant, Media


class CategoryModelTest(TestCase):
    """Test Category model."""
    
    def test_category_creation(self):
        """Test creating a category."""
        category = Category.objects.create(
            name='Electronics',
            description='Electronic devices'
        )
        self.assertEqual(category.name, 'Electronics')
        self.assertEqual(category.slug, 'electronics')
        self.assertTrue(category.slug)
    
    def test_category_slug_generation(self):
        """Test automatic slug generation."""
        category = Category.objects.create(name='Test Category')
        self.assertEqual(category.slug, 'test-category')


class ProductModelTest(TestCase):
    """Test Product model."""
    
    def setUp(self):
        """Set up test data."""
        self.category = Category.objects.create(
            name='Electronics',
            description='Electronic devices'
        )
    
    def test_product_creation(self):
        """Test creating a product."""
        product = Product.objects.create(
            name='Test Product',
            description='Test description',
            category=self.category,
            attributes={'brand': 'TestBrand'}
        )
        self.assertEqual(product.name, 'Test Product')
        self.assertEqual(product.slug, 'test-product')
        self.assertEqual(product.category, self.category)
    
    def test_product_slug_generation(self):
        """Test automatic slug generation."""
        product = Product.objects.create(
            name='Test Product',
            description='Test description',
            category=self.category
        )
        self.assertEqual(product.slug, 'test-product')


class VariantModelTest(TestCase):
    """Test Variant model."""
    
    def setUp(self):
        """Set up test data."""
        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            name='Test Product',
            description='Test description',
            category=self.category
        )
    
    def test_variant_creation(self):
        """Test creating a variant."""
        variant = Variant.objects.create(
            product=self.product,
            sku='TEST-001',
            name='Test Variant',
            price=Decimal('99.99'),
            stock=10
        )
        self.assertEqual(variant.sku, 'TEST-001')
        self.assertEqual(variant.price, Decimal('99.99'))
        self.assertEqual(variant.stock, 10)
        self.assertTrue(variant.is_in_stock)
    
    def test_variant_stock_status(self):
        """Test stock status methods."""
        variant = Variant.objects.create(
            product=self.product,
            sku='TEST-002',
            price=Decimal('50.00'),
            stock=0
        )
        self.assertFalse(variant.is_in_stock)


class ProductAPITest(APITestCase):
    """Test Product API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        # Clean up any existing data first
        Variant.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        
        self.category = Category.objects.create(
            name='Electronics',
            description='Electronic devices'
        )
        self.product = Product.objects.create(
            name='Test Product',
            description='Test description',
            category=self.category,
            is_active=True
        )
        self.variant = Variant.objects.create(
            product=self.product,
            sku='TEST-001',
            price=Decimal('99.99'),
            stock=10,
            is_active=True
        )
    
    def test_product_list(self):
        """Test product list endpoint."""
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_product_detail(self):
        """Test product detail endpoint."""
        url = reverse('product-detail', kwargs={'slug': self.product.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Product')
    
    def test_product_search(self):
        """Test product search functionality."""
        url = reverse('product-list')
        response = self.client.get(url, {'search': 'Test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_product_filter_by_category(self):
        """Test filtering products by category."""
        url = reverse('product-list')
        response = self.client.get(url, {'category': self.category.slug})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_product_filter_by_price(self):
        """Test filtering products by price range."""
        url = reverse('product-list')
        response = self.client.get(url, {'min_price': 50, 'max_price': 150})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_product_filter_in_stock(self):
        """Test filtering products by stock availability."""
        url = reverse('product-list')
        response = self.client.get(url, {'in_stock': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class CategoryAPITest(APITestCase):
    """Test Category API endpoints."""

    def setUp(self):
        """Set up test data."""
        # Clean up any existing categories first
        Category.objects.all().delete()
        self.category = Category.objects.create(
            name='Electronics',
            description='Electronic devices'
        )
    
    def test_category_list(self):
        """Test category list endpoint."""
        url = reverse('category-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # The response is paginated, so we need to check the results
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Electronics')
