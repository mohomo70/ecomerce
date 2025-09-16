"""
User models for the ecommerce application.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
import json


class User(AbstractUser):
    """
    Custom User model with role-based permissions.
    """
    
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('seller', 'Seller'),
        ('admin', 'Admin'),
    ]
    
    email = models.EmailField(unique=True)
    roles = models.JSONField(
        default=list,
        blank=True,
        help_text="List of roles assigned to this user"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'users_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.email
    
    def has_role(self, role):
        """Check if user has a specific role."""
        return role in self.roles
    
    def is_customer(self):
        """Check if user is a customer."""
        return self.has_role('customer')
    
    def is_seller(self):
        """Check if user is a seller."""
        return self.has_role('seller')
    
    def is_admin(self):
        """Check if user is an admin."""
        return self.has_role('admin')
    
    def add_role(self, role):
        """Add a role to the user if not already present."""
        if role not in self.roles:
            self.roles.append(role)
            self.save(update_fields=['roles'])
    
    def remove_role(self, role):
        """Remove a role from the user."""
        if role in self.roles:
            self.roles.remove(role)
            self.save(update_fields=['roles'])