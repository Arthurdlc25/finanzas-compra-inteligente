from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Rol, UserRole

class CustomUserAdmin(UserAdmin):
    model = Usuario
    fieldsets = UserAdmin.fieldsets + (
        ('Datos Administrativos', {'fields': ('dni', 'telefono', 'must_change_password', 'created_by')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Datos Administrativos', {'fields': ('dni', 'telefono', 'must_change_password')}),
    )

admin.site.register(Usuario, CustomUserAdmin)
admin.site.register(Rol)
admin.site.register(UserRole)