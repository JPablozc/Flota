from django.contrib import admin
from .models import Vehiculo, TipoDocumento, DocumentoVehiculo

@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ('placa', 'marca', 'modelo', 'anio', 'tipo', 'activo')
    search_fields = ('placa', 'marca', 'modelo')
    list_filter = ('activo', 'tipo')


@admin.register(TipoDocumento)
class TipoDocumentoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)


@admin.register(DocumentoVehiculo)
class DocumentoVehiculoAdmin(admin.ModelAdmin):
    list_display = ('vehiculo', 'tipo', 'fecha_vencimiento', 'estado')
    list_filter = ('tipo', 'fecha_vencimiento')
    search_fields = ('vehiculo__placa',)
