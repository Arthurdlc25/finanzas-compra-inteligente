from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Max
from .models import Usuario, Rol, UserRole
from .forms import UsuarioForm

import csv

@login_required
def dashboard_view(request):
    # 1. Traer los roles asociados al usuario actual
    user_roles = UserRole.objects.filter(usuario=request.user).select_related('rol')

    # 2. Definir los 5 módulos determinados para este sistema financiero
    modulos = ['clientes', 'vehiculos', 'simulaciones', 'configuraciones', 'usuarios']
    
    # Inicializar todos los permisos en 0 (Sin Acceso)
    permissions = {m: 0 for m in modulos}
    nombres_roles = []
    es_admin = False

    # 3. Evaluar los privilegios del usuario (capturando el nivel más alto si tiene varios roles)
    for ur in user_roles:
        rol = ur.rol
        nombres_roles.append(rol.role_name)
        
        if rol.is_admin:
            es_admin = True
            permissions = {m: 3 for m in modulos} # Acceso Total inmediato
            break 

        for m in modulos:
            if permissions[m] < 3:
                # Busca campos como rol.p_clientes, rol.p_simulaciones, etc.
                valor_permiso = getattr(rol, f'p_{m}', 0)
                if valor_permiso > permissions[m]:
                    permissions[m] = valor_permiso

    # 4. Enviar los permisos estructurados al contexto del HTML
    context = {
        'usuario': request.user,
        'permissions': permissions,
        'roles': nombres_roles,
        'es_admin': es_admin,
    }
    return render(request, 'dashboard.html', context)

# 1. LISTAR USUARIOS (CON FILTROS Y VALIDACIÓN DE PERMISOS)
@login_required
def usuarios_list(request):
    # Capturar el máximo permiso que tiene el usuario logueado para este módulo
    max_permission = UserRole.objects.filter(usuario=request.user).aggregate(max=Max('rol__p_usuarios'))['max'] or 0

    # Si no tiene permisos, lo regresa al Dashboard
    if max_permission == 0:
        messages.error(request, "No tienes acceso al módulo de gestión de personal.")
        return redirect('dashboard')
    
    # Listar los usuarios excluyendo superusuarios maestros para proteger el sistema
    usuarios_queryset = Usuario.objects.exclude(is_superuser=True).order_by('-created_at')

    # Aplicar filtros de búsqueda dinámicos (DNI o Nombre)
    q_busqueda = request.GET.get('buscar', '').strip()
    if q_busqueda:
        usuarios_queryset = usuarios_queryset.filter(
            Q(first_name__icontains=q_busqueda) | 
            Q(last_name__icontains=q_busqueda) | 
            Q(dni__icontains=q_busqueda)
        )

    context = {
        'usuarios': usuarios_queryset,
        'max_permission': max_permission,
        'buscar': q_busqueda
    }
    return render(request, 'usuarios/usuarios_list.html', context)


# 2. CREAR TRABAJADOR (CON CONTRASEÑA AUTOMÁTICA = DNI)
@login_required
def usuario_create(request):
    max_permission = UserRole.objects.filter(usuario=request.user).aggregate(max=Max('rol__p_usuarios'))['max'] or 0
    
    if max_permission < 2: # Requiere nivel de Escritura
        messages.error(request, "No tienes permisos para registrar nuevo personal.")
        return redirect('usuarios_list')

    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            dni_inicial = form.cleaned_data.get('dni')
            
            # Regla de Oro: Contraseña inicial es el DNI
            usuario.set_password(dni_inicial)
            usuario.must_change_password = True
            usuario.created_by = request.user
            usuario.save()

            # Guardar la relación en la tabla intermedia UserRole
            rol_seleccionado = form.cleaned_data.get('rol_asignado')
            UserRole.objects.create(usuario=usuario, rol=rol_seleccionado)

            messages.success(request, f"Trabajador {usuario.username} creado con éxito. Su clave de acceso inicial es su DNI.")
            return redirect('usuarios_list')
    else:
        form = UsuarioForm()

    return render(request, 'usuarios/usuario_form.html', {'form': form, 'titulo': 'Registrar Nuevo Personal'})


# 3. EDITAR DATOS O CAMBIAR ROL DEL TRABAJADOR
@login_required
def usuario_edit(request, pk):
    max_permission = UserRole.objects.filter(usuario=request.user).aggregate(max=Max('rol__p_usuarios'))['max'] or 0
    if max_permission < 2:
        messages.error(request, "No tienes permisos para modificar información del personal.")
        return redirect('usuarios_list')

    usuario_obj = get_object_or_404(Usuario, pk=pk)
    rol_relacion = UserRole.objects.filter(usuario=usuario_obj).first()

    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario_obj)
        if form.is_valid():
            form.save()

            # Actualizar el rol en la tabla intermedia
            nuevo_rol = form.cleaned_data.get('rol_asignado')
            if rol_relacion:
                rol_relacion.rol = nuevo_rol
                rol_relacion.save()
            else:
                UserRole.objects.create(usuario=usuario_obj, rol=nuevo_rol)

            messages.success(request, f"Datos de {usuario_obj.username} actualizados correctamente.")
            return redirect('usuarios_list')
    else:
        # Cargar los datos actuales en el formulario
        rol_inicial = rol_relacion.rol if rol_relacion else None
        form = UsuarioForm(instance=usuario_obj, initial={'rol_asignado': rol_inicial})

    return render(request, 'usuarios/usuario_form.html', {'form': form, 'titulo': 'Editar Información del Trabajador'})


# 4. SOFT DELETE (ACTIVAR / DESACTIVAR TRABAJADOR DE FORMA SEGURA)
@login_required
def toggle_usuario_status(request, pk):
    max_permission = UserRole.objects.filter(usuario=request.user).aggregate(max=Max('rol__p_usuarios'))['max'] or 0
    if max_permission < 2:
        messages.error(request, "No tienes permisos para dar de baja al personal.")
        return redirect('usuarios_list')

    usuario_obj = get_object_or_404(Usuario, pk=pk)
    
    if usuario_obj.pk == request.user.pk:
        messages.error(request, "Error de seguridad: No puedes dar de baja tu propia cuenta de acceso.")
        return redirect('usuarios_list')

    # Alternar el estado lógico de actividad
    if usuario_obj.is_active:
        usuario_obj.is_active = False
        messages.warning(request, f"El trabajador {usuario_obj.username} ha sido dado de BAJA en el sistema.")
    else:
        usuario_obj.is_active = True
        messages.success(request, f"El trabajador {usuario_obj.username} ha sido REACTIVADO correctamente.")
    
    usuario_obj.save()
    return redirect('usuarios_list')