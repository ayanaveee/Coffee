from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class MyUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'username', 'phone_number', 'role', 'is_admin')
    list_filter = ('is_admin', 'role')
    search_fields = ('email', 'username', 'phone_number')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal info', {'fields': ('phone_number', 'avatar', 'address', 'role')}),
        ('Permissions', {'fields': ('is_admin',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'phone_number', 'avatar', 'address', 'role', 'is_admin'),
        }),
    )

    filter_horizontal = ()

admin.site.register(User, MyUserAdmin)