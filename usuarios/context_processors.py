from .models import UserRole
from django.db.models import Max

def permisos_globales(request):
    if request.user.is_authenticated:
        user_roles = UserRole.objects.filter(usuario=request.user).select_related('rol')
        modulos = ['clientes', 'vehiculos', 'simulaciones', 'configuraciones', 'usuarios']
        permissions = {m: 0 for m in modulos}
        es_admin = False

        for ur in user_roles:
            rol = ur.rol
            if rol.is_admin:
                return {
                    'permissions': {m: 3 for m in modulos},
                    'es_admin': True
                }

            for m in modulos:
                if permissions[m] < 3:
                    valor_permiso = getattr(rol, f'p_{m}', 0)
                    if valor_permiso > permissions[m]:
                        permissions[m] = valor_permiso

        return {'permissions': permissions, 'es_admin': es_admin}
    
    return {'permissions': {}, 'es_admin': False}