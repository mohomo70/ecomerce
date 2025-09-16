"""
Management command to create a superuser with roles.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a superuser with admin role'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Email address')
        parser.add_argument('--username', type=str, help='Username')
        parser.add_argument('--password', type=str, help='Password')

    def handle(self, *args, **options):
        email = options['email'] or 'admin@example.com'
        username = options['username'] or 'admin'
        password = options['password'] or 'admin123'

        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING(f'User with email {email} already exists')
            )
            return

        user = User.objects.create_superuser(
            email=email,
            username=username,
            password=password,
            roles=['admin']
        )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created superuser: {email}')
        )