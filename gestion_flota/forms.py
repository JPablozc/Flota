from django import forms
from .models import Vehiculo, DocumentoVehiculo


# =========================
# Vehículo
# =========================

class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = [
            'placa',
            'marca',
            'modelo',
            'anio',
            'tipo',
            'foto',
            'activo',
            'responsable_nombre',
            'responsable_email',
        ]
        widgets = {
            'placa': forms.TextInput(attrs={'placeholder': 'ABC123'}),
            'marca': forms.TextInput(),
            'modelo': forms.TextInput(),
            'anio': forms.NumberInput(attrs={'min': 1900, 'max': 2100}),
            'tipo': forms.TextInput(attrs={'placeholder': 'Ej: Camioneta'}),
            'responsable_nombre': forms.TextInput(),
            'responsable_email': forms.EmailInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Clase Bootstrap por defecto
        for name, field in self.fields.items():

            # Checkbox (campo "activo")
            if name == "activo":
                field.widget.attrs.update({'class': 'form-check-input'})
                continue

            # Campos file (foto)
            if field.widget.input_type == 'file':
                field.widget.attrs.update({'class': 'form-control'})
                continue

            # Campos normales de texto / número
            field.widget.attrs.update({'class': 'form-control'})


# =========================
# Documento de Vehículo
# =========================

class DocumentoVehiculoForm(forms.ModelForm):
    class Meta:
        model = DocumentoVehiculo
        fields = ['tipo', 'fecha_expedicion', 'fecha_vencimiento', 'archivo']
        widgets = {
            'fecha_expedicion': forms.DateInput(attrs={'type': 'date'}),
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():

            # Campo PDF
            if field.widget.input_type == 'file':
                field.widget.attrs.update({'class': 'form-control'})
                continue

            # Resto de campos
            field.widget.attrs.update({'class': 'form-control'})
