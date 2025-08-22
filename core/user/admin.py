from django.contrib import admin
from django.contrib.auth.admin import UserAdmin  as BaseUserAdmin
from .models import User, OTP, UserProfile

class MyUserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'is_admin')
    search_fields = ('email', 'username')
    ordering = ('email',)
    filter_horizontal = ()
    list_filter = ()
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Permissions', {'fields': ('is_admin', 'role')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'phone_number', 'avatar', 'address', 'role', 'is_admin'),
        }),
    )

    filter_horizontal = ()

class OTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at')
    search_fields = ('user__email', 'code')
    ordering = ('-created_at',)

admin.site.register(OTP, OTPAdmin)
admin.site.register(User, MyUserAdmin)
admin.site.register(UserProfile)