"""
Admin configuration for User model.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin configuration for custom User model.
    """
    
    list_display = ('email', 'username', 'first_name', 'last_name', 'roles_display', 'is_active', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'roles', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Roles', {'fields': ('roles',)}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'roles'),
        }),
    )
    
    def roles_display(self, obj):
        """Display roles as colored badges."""
        if not obj.roles:
            return format_html('<span style="color: #999;">No roles</span>')
        
        badges = []
        for role in obj.roles:
            color = {
                'customer': '#28a745',
                'seller': '#007bff',
                'admin': '#dc3545'
            }.get(role, '#6c757d')
            
            badges.append(
                f'<span style="background-color: {color}; color: white; padding: 2px 6px; '
                f'border-radius: 3px; font-size: 11px; margin-right: 2px;">{role}</span>'
            )
        
        return format_html(''.join(badges))
    
    roles_display.short_description = 'Roles'