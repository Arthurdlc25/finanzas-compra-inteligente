from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Cliente, Banco, Vehiculo, Simulacion
from .forms import ClienteForm, BancoForm, VehiculoForm, SimulacionForm
from .utils import calcular_cronograma_compra_inteligente
from usuarios.models import UserRole
from django.db.models import Max

# 1. LISTADO DE CLIENTES
@login_required
def clientes_list(request):
    max_permission = UserRole.objects.filter(usuario=request.user).aggregate(max=Max('rol__p_clientes'))['max'] or 0
    if max_permission == 0:
        messages.error(request, "No tienes acceso al módulo de Clientes.")
        return redirect('dashboard')

    clientes_queryset = Cliente.objects.all().order_by('-created_at')

    # Filtro de búsqueda por Documento (DNI/RUC), Nombres o Razón Social
    buscar = request.GET.get('buscar', '').strip()
    if buscar:
        clientes_queryset = clientes_queryset.filter(
            Q(documento_identidad__icontains=buscar) |
            Q(nombres__icontains=buscar) |
            Q(apellidos__icontains=buscar) |
            Q(razon_social__icontains=buscar)
        )

    return render(request, 'finanzas/clientes_list.html', {
        'clientes': clientes_queryset,
        'buscar': buscar,
        'max_permission': max_permission
    })

# 2. REGISTRAR CLIENTE
@login_required
def cliente_create(request):
    max_permission = UserRole.objects.filter(usuario=request.user).aggregate(max=Max('rol__p_clientes'))['max'] or 0
    if max_permission < 2:
        messages.error(request, "No tienes permisos de escritura para registrar clientes.")
        return redirect('clientes_list')

    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save(commit=False)
            cliente.created_by = request.user
            cliente.save()
            messages.success(request, f"Cliente {cliente} registrado correctamente.")
            return redirect('clientes_list')
    else:
        form = ClienteForm()

    return render(request, 'finanzas/cliente_form.html', {'form': form, 'titulo': 'Registrar Cliente'})

# 3. EDITAR CLIENTE
@login_required
def cliente_edit(request, pk):
    max_permission = UserRole.objects.filter(usuario=request.user).aggregate(max=Max('rol__p_clientes'))['max'] or 0
    if max_permission < 2:
        messages.error(request, "No tienes permisos para modificar datos de clientes.")
        return redirect('clientes_list')

    cliente_obj = get_object_or_404(Cliente, pk=pk)

    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente_obj)
        if form.is_valid():
            form.save()
            messages.success(request, f"Datos del cliente actualizados correctamente.")
            return redirect('clientes_list')
    else:
        form = ClienteForm(instance=cliente_obj)

    return render(request, 'finanzas/cliente_form.html', {'form': form, 'titulo': 'Editar Cliente'})

# 1. LISTADO DE BANCOS Y TARIFARIOS
@login_required
def bancos_list(request):
    max_permission = UserRole.objects.filter(usuario=request.user).aggregate(max=Max('rol__p_configuraciones'))['max'] or 0
    if max_permission == 0:
        messages.error(request, "No tienes acceso a las configuraciones globales del sistema.")
        return redirect('dashboard')

    bancos_queryset = Banco.objects.all().order_by('nombre')
    return render(request, 'finanzas/bancos_list.html', {
        'bancos': bancos_queryset,
        'max_permission': max_permission
    })

# 2. AGREGAR BANCO
@login_required
def banco_create(request):
    max_permission = UserRole.objects.filter(usuario=request.user).aggregate(max=Max('rol__p_configuraciones'))['max'] or 0
    if max_permission < 2:
        messages.error(request, "No cuentas con permisos de escritura para modificar configuraciones.")
        return redirect('bancos_list')

    if request.method == 'POST':
        form = BancoForm(request.POST)
        if form.is_valid():
            banco = form.save()
            messages.success(request, f"Entidad financiera {banco.nombre} incorporada con éxito al sistema.")
            return redirect('bancos_list')
    else:
        form = BancoForm()

    return render(request, 'finanzas/banco_form.html', {'form': form, 'titulo': 'Configurar Nueva Entidad Financiera'})

# 3. EDITAR BANCO / ACTUALIZAR TASAS SBS
@login_required
def banco_edit(request, pk):
    max_permission = UserRole.objects.filter(usuario=request.user).aggregate(max=Max('rol__p_configuraciones'))['max'] or 0
    if max_permission < 2:
        messages.error(request, "No cuentas con permisos para modificar el tarifario interbancario.")
        return redirect('bancos_list')

    banco_obj = get_object_or_404(Banco, pk=pk)

    if request.method == 'POST':
        form = BancoForm(request.POST, instance=banco_obj)
        if form.is_valid():
            form.save()
            messages.success(request, f"Tarifario de {banco_obj.nombre} actualizado correctamente.")
            return redirect('bancos_list')
    else:
        form = BancoForm(instance=banco_obj)

    return render(request, 'finanzas/banco_form.html', {'form': form, 'titulo': f'Actualizar Tarifario - {banco_obj.nombre}'})

# 1. LISTADO DE VEHÍCULOS
@login_required
def vehiculos_list(request):
    max_permission = UserRole.objects.filter(usuario=request.user).aggregate(max=Max('rol__p_vehiculos'))['max'] or 0
    if max_permission == 0:
        messages.error(request, "No tienes acceso al módulo de Vehículos.")
        return redirect('dashboard')

    vehiculos_queryset = Vehiculo.objects.all().order_by('-created_at')

    # Filtro opcional por marca o modelo
    buscar = request.GET.get('buscar', '').strip()
    if buscar:
        vehiculos_queryset = vehiculos_queryset.filter(
            Q(marca__icontains=buscar) | Q(modelo__icontains=buscar)
        )

    return render(request, 'finanzas/vehiculos_list.html', {
        'vehiculos': vehiculos_queryset,
        'buscar': buscar,
        'max_permission': max_permission
    })

# 2. REGISTRAR VEHÍCULO
@login_required
def vehiculo_create(request):
    max_permission = UserRole.objects.filter(usuario=request.user).aggregate(max=Max('rol__p_vehiculos'))['max'] or 0
    if max_permission < 2:
        messages.error(request, "No cuentas con permisos para añadir vehículos al catálogo.")
        return redirect('vehiculos_list')

    if request.method == 'POST':
        form = VehiculoForm(request.POST)
        if form.is_valid():
            vehiculo = form.save()
            messages.success(request, f"Vehículo {vehiculo.marca} {vehiculo.modelo} añadido correctamente.")
            return redirect('vehiculos_list')
    else:
        form = VehiculoForm()

    return render(request, 'finanzas/vehiculo_form.html', {'form': form, 'titulo': 'Registrar Vehículo en Vitrina'})

# 3. EDITAR VEHÍCULO
@login_required
def vehiculo_edit(request, pk):
    max_permission = UserRole.objects.filter(usuario=request.user).aggregate(max=Max('rol__p_vehiculos'))['max'] or 0
    if max_permission < 2:
        messages.error(request, "No tienes permisos para modificar el catálogo vehicular.")
        return redirect('vehiculos_list')

    vehiculo_obj = get_object_or_404(Vehiculo, pk=pk)

    if request.method == 'POST':
        form = VehiculoForm(request.POST, instance=vehiculo_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Información del vehículo actualizada correctamente.")
            return redirect('vehiculos_list')
    else:
        form = VehiculoForm(instance=vehiculo_obj)

    return render(request, 'finanzas/vehiculo_form.html', {'form': form, 'titulo': f'Editar {vehiculo_obj.marca} {vehiculo_obj.modelo}'})

@login_required
def prestamos_list(request):
    max_permission = UserRole.objects.filter(usuario=request.user).aggregate(max=Max('rol__p_simulaciones'))['max'] or 0
    if max_permission == 0:
        messages.error(request, "No cuentas con acceso al módulo de Préstamos.")
        return redirect('dashboard')

    prestamos_queryset = Simulacion.objects.all().order_by('-created_at').select_related('cliente', 'vehiculo', 'banco')

    buscar = request.GET.get('buscar', '').strip()
    if buscar:
        prestamos_queryset = prestamos_queryset.filter(
            Q(cliente__documento_identidad__icontains=buscar) |
            Q(cliente__nombres__icontains=buscar) |
            Q(cliente__apellidos__icontains=buscar) |
            Q(cliente__razon_social__icontains=buscar) |
            Q(banco__nombre__icontains=buscar)
        )

    return render(request, 'finanzas/prestamos_list.html', {
        'prestamos': prestamos_queryset,
        'buscar': buscar,
        'max_permission': max_permission
    })

@login_required
def simulador_view(request):
    max_permission = UserRole.objects.filter(usuario=request.user).aggregate(max=Max('rol__p_simulaciones'))['max'] or 0
    if max_permission == 0:
        messages.error(request, "No cuentas con acceso al módulo de Simulación.")
        return redirect('dashboard')

    resultado = None
    form = SimulacionForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        # Instanciamos el objeto en memoria sin guardarlo permanentemente aún
        simulacion_instancia = form.save(commit=False)
        simulacion_instancia.created_by = request.user
        
        # Ejecutamos el motor de cálculo
        resultado = calcular_cronograma_compra_inteligente(simulacion_instancia)
        
        # Evaluamos el Scoring de capacidad de pago (Regla de negocio: Máximo 30%)
        cuota_mensual_regular = resultado['cronograma'][simulacion_instancia.meses_gracia + 1]['cuota_total']
        ingreso_cliente = simulacion_instancia.cliente.ingreso_mensual
        ratio_endeudamiento = (cuota_mensual_regular / ingreso_cliente) * 100
        
        resultado['ratio_endeudamiento'] = ratio_endeudamiento
        resultado['aprobado'] = ratio_endeudamiento <= 30
        
        # Si el usuario decide confirmar y guardar el registro histórico
        if 'guardar_prestamo' in request.POST and resultado['aprobado']:
            simulacion_instancia.tcea_calculada = resultado['tcea']
            simulacion_instancia.van_calculado = resultado['van']
            simulacion_instancia.tir_calculada = resultado['tir']
            simulacion_instancia.save()
            messages.success(request, f"Simulación #{simulacion_instancia.id} guardada exitosamente en el historial de préstamos.")
            return redirect('dashboard')

    return render(request, 'finanzas/simulador.html', {
        'form': form,
        'resultado': resultado,
        'max_permission': max_permission
    })

@login_required
def prestamo_detail(request, pk):
    max_permission = UserRole.objects.filter(usuario=request.user).aggregate(max=Max('rol__p_simulaciones'))['max'] or 0
    if max_permission == 0:
        messages.error(request, "No tienes acceso a los expedientes de créditos.")
        return redirect('dashboard')

    prestamo = get_object_or_404(Simulacion, pk=pk)
    
    resultado = calcular_cronograma_compra_inteligente(prestamo)
    
    return render(request, 'finanzas/prestamo_detail.html', {
        'prestamo': prestamo,
        'resultado': resultado
    })