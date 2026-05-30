from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Cliente
from .forms import ClienteForm
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