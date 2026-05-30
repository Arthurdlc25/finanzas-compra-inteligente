from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Cliente, Banco, Vehiculo
from .forms import ClienteForm, BancoForm, VehiculoForm
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