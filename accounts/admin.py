from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_learner', 'is_admin', 'is_active', 'azure_ad_user_id')
    list_filter = ('is_active', 'is_staff', 'is_learner', 'is_admin', 'is_superuser')
    search_fields = ('email', 'first_name', 'last_name', 'azure_ad_user_id')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'avatar')}),
        ('Roles', {'fields': ('is_learner', 'is_admin')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Azure AD', {'fields': ('azure_ad_user_id',)}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
        ('Roles', {'fields': ('is_learner', 'is_admin')}),
        ('Azure AD', {
            'fields': ('azure_ad_user_id',),
            'description': 'Leave blank; will be populated on first login.'
        }),
    )

    readonly_fields = ('last_login', 'date_joined')
