from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'user_type', 'phone_number']
    fieldsets = UserAdmin.fieldsets + (
        ('Additional', {'fields': ('user_type', 'phone_number', 'age', 'gender')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
