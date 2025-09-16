from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model with roles.
    """
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('seller', 'Seller'),
        ('admin', 'Admin'),
    ]
    
    email = models.EmailField(unique=True)
    roles = models.JSONField(default=list, help_text="List of user roles")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email
    
    def has_role(self, role):
        """Check if user has a specific role."""
        return role in self.roles
    
    def add_role(self, role):
        """Add a role to the user."""
        if role not in self.roles:
            self.roles.append(role)
            self.save()
    
    def remove_role(self, role):
        """Remove a role from the user."""
        if role in self.roles:
            self.roles.remove(role)
            self.save()
