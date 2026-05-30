from django.urls import path
from .views import clientes_list, cliente_create, cliente_edit

urlpatterns = [
    path('clientes/', clientes_list, name='clientes_list'),
    path('clientes/nuevo/', cliente_create, name='cliente_create'),
    path('clientes/editar/<int:pk>/', cliente_edit, name='cliente_edit'),
]