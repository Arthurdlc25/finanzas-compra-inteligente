from django import forms
from .models import Cliente

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

    # Validación lógica del lado del servidor
    def clean(self):
        cleaned_data = super().clean()
        tipo_cliente = cleaned_data.get('tipo_cliente')
        
        if tipo_cliente == 'NATURAL':
            if not cleaned_data.get('nombres') or not cleaned_data.get('apellidos'):
                raise forms.ValidationError("Para una Persona Natural, los campos Nombres y Apellidos son obligatorios.")
            cleaned_data['razon_social'] = None # Limpia basura si cambiaron de opinión
        elif tipo_cliente == 'JURIDICA':
            if not cleaned_data.get('razon_social'):
                raise forms.ValidationError("Para una Persona Jurídica / Entidad, la Razón Social es obligatoria.")
            cleaned_data['nombres'] = None
            cleaned_data['apellidos'] = None
            
        return cleaned_data