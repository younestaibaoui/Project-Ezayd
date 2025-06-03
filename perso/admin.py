from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserAccount, EmailVerificationToken

class UserAccountAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'is_admin', 'is_active', 'email_verified_display')
    search_fields = ('email', 'username')
    readonly_fields = ('date_joined', 'last_login')
    list_filter = ('is_admin', 'is_active', 'email_verified')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informations personnelles', {'fields': ('username', 'first_name', 'last_name', 'bio', 'pfp')}),
        ('Permissions', {'fields': ('is_admin', 'is_active', 'email_verified')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )

    ordering = ('email',)
    filter_horizontal = ()

    def email_verified_display(self, obj):
        return "✅" if obj.email_verified else "❌"
    email_verified_display.short_description = "Email vérifié"
    email_verified_display.admin_order_field = 'email_verified'

admin.site.register(UserAccount, UserAccountAdmin)
admin.site.register(EmailVerificationToken)
