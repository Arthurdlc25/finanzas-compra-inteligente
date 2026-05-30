from django.db import models
from django.conf import settings

class Cliente(models.Model):
    TIPO_CLIENTE_CHOICES = [
        ('NATURAL', 'Persona Natural'),
        ('JURIDICA', 'Persona Jurídica / Entidad'),
    ]

    tipo_cliente = models.CharField(max_length=10, choices=TIPO_CLIENTE_CHOICES, default='NATURAL', verbose_name="Tipo de Cliente")
    
    # Puede almacenar un DNI (8 dígitos), CE o un RUC (11 dígitos)
    documento_identidad = models.CharField(max_length=11, unique=True, verbose_name="Número de Documento (DNI/RUC)")
    
    # Campos exclusivos para Persona Natural
    nombres = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nombres")
    apellidos = models.CharField(max_length=100, blank=True, null=True, verbose_name="Apellidos")
    
    # Campo exclusivo para Persona Jurídica / Entidad
    razon_social = models.CharField(max_length=150, blank=True, null=True, verbose_name="Razón Social / Empresa")
    
    email = models.EmailField(unique=True, verbose_name="Correo Electrónico")
    telefono = models.CharField(max_length=15, blank=True, verbose_name="Teléfono Celular / Contacto")
    
    # Capacidad financiera: Ingreso neto para personas o Facturación mensual declarada para empresas
    ingreso_mensual = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Ingreso Neto / Facturación Mensual (S/.)")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Registrado Por")

    class Meta:
        db_table = 'clientes'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        if self.tipo_cliente == 'NATURAL':
            return f"{self.apellidos}, {self.nombres} ({self.documento_identidad})"
        return f"{self.razon_social} (RUC: {self.documento_identidad})"


class Vehiculo(models.Model):
    marca = models.CharField(max_length=50, verbose_name="Marca")
    modelo = models.CharField(max_length=50, verbose_name="Modelo")
    anio = models.IntegerField(verbose_name="Año de Fabricación")
    
    # En el mercado peruano el valor comercial base suele fijarse en dólares
    precio_base = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Precio Base (USD)")
    
    # Campo para control de stock o disponibilidad en vitrina
    disponible = models.BooleanField(default=True, verbose_name="Disponible para Financiar?")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'vehiculos'
        verbose_name = 'Vehículo'
        verbose_name_plural = 'Vehículos'

    def __str__(self):
        return f"{self.marca} {self.modelo} ({self.anio}) - $ {self.precio_base:,}"