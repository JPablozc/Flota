from django import forms
from .models import Vehiculo, DocumentoVehiculo


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name in ['activo']:
                field.widget.attrs.update({'class': 'form-check-input'})
            elif hasattr(field.widget, 'input_type') and field.widget.input_type == 'file':
                field.widget.attrs.update({'class': 'form-control'})
            else:
                field.widget.attrs.update({'class': 'form-control'})


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
            if hasattr(field.widget, 'input_type') and field.widget.input_type == 'file':
                field.widget.attrs.update({'class': 'form-control'})
            else:
                field.widget.attrs.update({'class': 'form-control'})
