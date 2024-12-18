from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import CustomUser, Address, Profile


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Specify the ordering if `username` does not exist
    ordering = ['email']  # Use your unique identifier field, e.g., 'email'

    # Add custom fields to UserAdmin if `username` is replaced by `email`
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )

    # Define the displayed list fields
    list_display = ('email', 'first_name', 'last_name', 'is_staff')

    # Define the fields for searching
    search_fields = ('email', 'first_name', 'last_name')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    pass


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass
