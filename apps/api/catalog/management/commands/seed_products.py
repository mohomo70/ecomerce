"""
Management command to seed products with sample data.
"""
import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from catalog.models import Category, Product, Variant, Media


class Command(BaseCommand):
    help = 'Seed products with sample data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=100,
            help='Number of products to create'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing products before seeding'
        )
    
    def handle(self, *args, **options):
        count = options['count']
        clear = options['clear']
        
        if clear:
            self.stdout.write('Clearing existing products...')
            Product.objects.all().delete()
            Category.objects.all().delete()
        
        with transaction.atomic():
            # Create categories
            categories = self.create_categories()
            
            # Create products
            products = self.create_products(categories, count)
            
            # Create variants for each product
            self.create_variants(products)
            
            # Create media for each product
            self.create_media(products)
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {count} products')
        )
    
    def create_categories(self):
        """Create sample categories."""
        categories_data = [
            {'name': 'Electronics', 'description': 'Electronic devices and gadgets'},
            {'name': 'Clothing', 'description': 'Fashion and apparel'},
            {'name': 'Home & Garden', 'description': 'Home improvement and gardening'},
            {'name': 'Sports', 'description': 'Sports and outdoor equipment'},
            {'name': 'Books', 'description': 'Books and educational materials'},
            {'name': 'Toys', 'description': 'Toys and games for all ages'},
        ]
        
        categories = []
        for data in categories_data:
            category, created = Category.objects.get_or_create(
                name=data['name'],
                defaults={'description': data['description']}
            )
            categories.append(category)
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        return categories
    
    def create_products(self, categories, count):
        """Create sample products."""
        product_templates = [
            {
                'name_templates': [
                    'Wireless {color} Headphones',
                    'Smart {color} Watch',
                    'Portable {color} Speaker',
                    'Gaming {color} Mouse',
                    'Bluetooth {color} Earbuds',
                ],
                'descriptions': [
                    'High-quality wireless headphones with noise cancellation and long battery life.',
                    'Smart wearable device with fitness tracking and notifications.',
                    'Portable speaker with excellent sound quality and waterproof design.',
                    'Precision gaming mouse with customizable RGB lighting.',
                    'True wireless earbuds with active noise cancellation.',
                ],
                'attributes': [
                    {'brand': 'TechBrand', 'warranty': '2 years', 'connectivity': 'Bluetooth 5.0'},
                    {'brand': 'SmartWear', 'warranty': '1 year', 'connectivity': 'Bluetooth 5.2'},
                    {'brand': 'AudioPro', 'warranty': '1 year', 'connectivity': 'Bluetooth 4.2'},
                    {'brand': 'GameGear', 'warranty': '2 years', 'connectivity': 'USB'},
                    {'brand': 'SoundMax', 'warranty': '1 year', 'connectivity': 'Bluetooth 5.0'},
                ]
            },
            {
                'name_templates': [
                    '{color} Cotton T-Shirt',
                    'Denim {color} Jeans',
                    'Wool {color} Sweater',
                    'Leather {color} Jacket',
                    'Silk {color} Scarf',
                ],
                'descriptions': [
                    'Comfortable cotton t-shirt perfect for everyday wear.',
                    'Classic denim jeans with modern fit and style.',
                    'Warm wool sweater for cold weather comfort.',
                    'Genuine leather jacket with timeless design.',
                    'Luxurious silk scarf with elegant patterns.',
                ],
                'attributes': [
                    {'material': '100% Cotton', 'care': 'Machine wash', 'origin': 'Made in USA'},
                    {'material': '98% Cotton, 2% Elastane', 'care': 'Machine wash', 'origin': 'Made in USA'},
                    {'material': '100% Wool', 'care': 'Hand wash', 'origin': 'Made in Italy'},
                    {'material': '100% Leather', 'care': 'Professional clean', 'origin': 'Made in Italy'},
                    {'material': '100% Silk', 'care': 'Dry clean', 'origin': 'Made in France'},
                ]
            },
            {
                'name_templates': [
                    'Garden {color} Plant Pot',
                    'LED {color} Light Strip',
                    'Wooden {color} Table',
                    'Ceramic {color} Vase',
                    'Metal {color} Lamp',
                ],
                'descriptions': [
                    'Decorative plant pot perfect for indoor and outdoor plants.',
                    'Energy-efficient LED light strip with remote control.',
                    'Handcrafted wooden table with natural finish.',
                    'Beautiful ceramic vase for flowers and decoration.',
                    'Modern metal lamp with adjustable brightness.',
                ],
                'attributes': [
                    {'material': 'Ceramic', 'size': 'Medium', 'style': 'Modern'},
                    {'material': 'Plastic', 'power': '12W', 'style': 'Contemporary'},
                    {'material': 'Oak Wood', 'size': 'Large', 'style': 'Rustic'},
                    {'material': 'Ceramic', 'size': 'Small', 'style': 'Classic'},
                    {'material': 'Aluminum', 'power': '8W', 'style': 'Minimalist'},
                ]
            }
        ]
        
        colors = ['Black', 'White', 'Red', 'Blue', 'Green', 'Yellow', 'Purple', 'Orange']
        products = []
        
        for i in range(count):
            template = random.choice(product_templates)
            category = random.choice(categories)
            color = random.choice(colors)
            name_template = random.choice(template['name_templates'])
            description = random.choice(template['descriptions'])
            attributes = random.choice(template['attributes'])
            
            name = name_template.format(color=color)
            
            # Ensure unique slug by adding a number if needed
            base_slug = slugify(name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            product = Product.objects.create(
                name=name,
                slug=slug,
                description=description,
                category=category,
                attributes=attributes,
                is_active=random.choice([True, True, True, False])  # 75% active
            )
            products.append(product)
        
        return products
    
    def create_variants(self, products):
        """Create variants for products."""
        for product in products:
            # Create 1-3 variants per product
            variant_count = random.randint(1, 3)
            
            for i in range(variant_count):
                sku = f"{product.slug.upper()}-{i+1:02d}"
                variant_name = f"Variant {i+1}" if variant_count > 1 else ""
                
                # Price between $10 and $500
                price = Decimal(str(random.uniform(10, 500))).quantize(Decimal('0.01'))
                
                # Stock between 0 and 100
                stock = random.randint(0, 100)
                
                variant_attributes = {
                    'size': random.choice(['S', 'M', 'L', 'XL', 'XXL']),
                    'weight': f"{random.uniform(0.1, 5.0):.1f} kg",
                }
                
                Variant.objects.create(
                    product=product,
                    sku=sku,
                    name=variant_name,
                    price=price,
                    stock=stock,
                    attributes=variant_attributes,
                    is_active=random.choice([True, True, True, False])  # 75% active
                )
    
    def create_media(self, products):
        """Create media for products."""
        # Sample image URLs (using placeholder services)
        image_urls = [
            'https://picsum.photos/400/400?random=1',
            'https://picsum.photos/400/400?random=2',
            'https://picsum.photos/400/400?random=3',
            'https://picsum.photos/400/400?random=4',
            'https://picsum.photos/400/400?random=5',
        ]
        
        for product in products:
            # Create 1-3 media items per product
            media_count = random.randint(1, 3)
            
            for i in range(media_count):
                Media.objects.create(
                    product=product,
                    url=random.choice(image_urls),
                    alt_text=f"{product.name} - Image {i+1}",
                    media_type='image',
                    sort_order=i
                )