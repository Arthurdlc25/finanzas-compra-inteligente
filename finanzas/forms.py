from django import forms
from .models import Cliente, Banco, Vehiculo

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['tipo_cliente', 'documento_identidad', 'nombres', 'apellidos', 'razon_social', 'email', 'telefono', 'ingreso_mensual']
        widgets = {
            'tipo_cliente': forms.Select(attrs={'class': 'w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600 focus:bg-white text-sm', 'id': 'id_tipo_cliente'}),
            'documento_identidad': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600 focus:bg-white text-sm', 'placeholder': 'DNI o RUC'}),
            'nombres': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600 focus:bg-white text-sm', 'placeholder': 'Nombres'}),
            'apellidos': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600 focus:bg-white text-sm', 'placeholder': 'Apellidos'}),
            'razon_social': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600 focus:bg-white text-sm', 'placeholder': 'Nombre de la empresa'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600 focus:bg-white text-sm', 'placeholder': 'correo@ejemplo.com'}),
            'telefono': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600 focus:bg-white text-sm', 'placeholder': '9########'}),
            'ingreso_mensual': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600 focus:bg-white text-sm', 'placeholder': '0.00'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        tipo_cliente = cleaned_data.get('tipo_cliente')
        
        if tipo_cliente == 'NATURAL':
            if not cleaned_data.get('nombres') or not cleaned_data.get('apellidos'):
                raise forms.ValidationError("Para una Persona Natural, los campos Nombres y Apellidos son obligatorios.")
            cleaned_data['razon_social'] = None
        elif tipo_cliente == 'JURIDICA':
            if not cleaned_data.get('razon_social'):
                raise forms.ValidationError("Para una Persona Jurídica / Entidad, la Razón Social es obligatoria.")
            cleaned_data['nombres'] = None
            cleaned_data['apellidos'] = None
            
        return cleaned_data

class BancoForm(forms.ModelForm):
    class Meta:
        model = Banco
        fields = ['nombre', 'tea', 'tasa_desgravamen', 'tasa_seguro_vehicular', 'comision_portes']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600 focus:bg-white text-sm', 'placeholder': 'Ej. BCP, BBVA, Interbank'}),
            'tea': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600 focus:bg-white text-sm', 'placeholder': '0.00', 'step': '0.01'}),
            'tasa_desgravamen': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600 focus:bg-white text-sm', 'placeholder': '0.0000', 'step': '0.0001'}),
            'tasa_seguro_vehicular': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600 focus:bg-white text-sm', 'placeholder': '0.00', 'step': '0.01'}),
            'comision_portes': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600 focus:bg-white text-sm', 'placeholder': '0.00', 'step': '0.01'}),
        }

class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = ['marca', 'modelo', 'anio', 'precio_base', 'disponible']
        widgets = {
            'marca': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600 focus:bg-white text-sm', 'placeholder': 'Ej. Toyota, Hyundai, Kia'}),
            'modelo': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600 focus:bg-white text-sm', 'placeholder': 'Ej. RAV4, Tucson, Sportage'}),
            'anio': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600 focus:bg-white text-sm', 'placeholder': 'Año de fabricación'}),
            'precio_base': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600 focus:bg-white text-sm', 'placeholder': 'Valor comercial en USD', 'step': '0.01'}),
            'disponible': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 cursor-pointer'}),
        }