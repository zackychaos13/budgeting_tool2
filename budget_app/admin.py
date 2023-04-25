from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, Category, Budget, FundsAllocation, Transaction


class CustomUserAdmin(UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    list_display = ('username', 'email', 'is_staff', 'is_active',)
    list_filter = ('username', 'email', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'username', 'password1', 'password2', 'is_staff'
            )
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)


# Register your models here.
# Registering models allows them to show up in the django /admin panel
admin.site.register(User, UserAdmin)
admin.site.register(Category)
admin.site.register(Budget)
admin.site.register(FundsAllocation)
admin.site.register(Transaction)
