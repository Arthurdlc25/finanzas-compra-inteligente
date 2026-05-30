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

class Banco(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre de la Entidad Financiera")
    
    tea = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Tasa Efectiva Anual (TEA %)")
    tasa_desgravamen = models.DecimalField(max_digits=5, decimal_places=4, verbose_name="Seguro de Desgravamen Mensual (%)")
    tasa_seguro_vehicular = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Seguro Vehicular Anual (%)")
    comision_portes = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Comisión por Portes / Envío de Estado de Cuenta")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bancos'
        verbose_name = 'Banco'
        verbose_name_plural = 'Bancos'

    def __str__(self):
        return f"{self.nombre} (TEA: {self.tea}%)"
    
class Simulacion(models.Model):
    MONEDA_CHOICES = [
        ('PEN', 'Soles (S/.)'),
        ('USD', 'Dólares ($)'),
    ]
    TIPO_GRACIA_CHOICES = [
        ('SIN_GRACIA', 'Sin Periodo de Gracia'),
        ('PARCIAL', 'Gracia Parcial (Pago de Interés Puro)'),
        ('TOTAL', 'Gracia Total (Capitalización de Interés)'),
    ]
    PLAZO_CHOICES = [
        (24, '24 Meses'),
        (36, '36 Meses'),
    ]

    # Relaciones principales del negocio
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, verbose_name="Cliente Evaluado")
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, verbose_name="Vehículo de Interés")
    banco = models.ForeignKey(Banco, on_delete=models.CASCADE, verbose_name="Banco Financiador")
    
    # Parámetros del Crédito
    moneda = models.CharField(max_length=3, choices=MONEDA_CHOICES, default='PEN', verbose_name="Moneda del Préstamo")
    tipo_cambio = models.DecimalField(max_digits=4, decimal_places=2, default=3.75, verbose_name="Tipo de Cambio Aplicado")
    
    cuota_inicial_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Cuota Inicial (%)")
    cuota_balon_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=40.00, verbose_name="Cuota Balón / Valor Residual (%)")
    
    plazo_meses = models.IntegerField(choices=PLAZO_CHOICES, default=36, verbose_name="Plazo del Crédito")
    meses_gracia = models.IntegerField(default=0, verbose_name="Meses de Gracia (0 a 3)")
    tipo_gracia = models.CharField(max_length=15, choices=TIPO_GRACIA_CHOICES, default='SIN_GRACIA', verbose_name="Modalidad de Gracia")

    # Resultados resumidos para almacenamiento rápido
    tcea_calculada = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="TCEA Real (%)")
    van_calculado = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="VAN Generado")
    tir_calculada = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="TIR (%)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'simulaciones'
        verbose_name = 'Simulación'
        verbose_name_plural = 'Simulaciones'

    def __str__(self):
        return f"Simulación #{self.id} - Cliente: {self.cliente.documento_identidad}"