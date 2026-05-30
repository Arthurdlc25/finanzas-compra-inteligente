from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class Rol(models.Model):
    PERMISO_CHOICES = [
        (0, 'Sin Acceso'),
        (1, 'Solo Lectura (Read)'),
        (2, 'Lectura y Escritura (Read & Write)'),
        (3, 'Acceso Total'),
    ]

    role_name = models.CharField(max_length=50, blank=False, null=False, verbose_name='Nombre del Rol')
    is_admin = models.BooleanField(default=False, verbose_name='Es Administrador?')

    p_clientes = models.IntegerField(choices=PERMISO_CHOICES, default=0, verbose_name='Permiso Clientes')
    p_vehiculos = models.IntegerField(choices=PERMISO_CHOICES, default=0, verbose_name='Permiso Vehículos')
    p_simulaciones = models.IntegerField(choices=PERMISO_CHOICES, default=0, verbose_name='Permiso Simulaciones (Préstamos)')
    p_configuraciones = models.IntegerField(choices=PERMISO_CHOICES, default=0, verbose_name='Permiso Configuración Global')
    p_usuarios = models.IntegerField(choices=PERMISO_CHOICES, default=0, verbose_name='Permiso Gestión de Usuarios')

    class Meta:
        db_table = 'roles'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.role_name


class Usuario(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='Correo Electrónico')
    dni = models.CharField(max_length=8, unique=True, null=False, verbose_name='DNI')
    telefono = models.CharField(max_length=15, unique=True, blank=True, verbose_name='Teléfono')

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    must_change_password = models.BooleanField(default=True, verbose_name='Debe cambiar contraseña?')

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["first_name", "last_name", "email", "dni"]

    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'


class UserRole(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, verbose_name='Usuario')
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE, verbose_name='Rol')

    class Meta:
        db_table = 'usuario_roles'
        verbose_name = 'Usuario Rol'
        verbose_name_plural = 'Usuario Roles'
        unique_together = ('usuario', 'rol')

    def __str__(self):
        return f"{self.usuario.username} - {self.rol.role_name}"