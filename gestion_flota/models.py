from django.db import models
from django.contrib.auth.models import User
from datetime import date


class Vehiculo(models.Model):
    placa = models.CharField(max_length=10, unique=True)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    anio = models.PositiveIntegerField(null=True, blank=True)
    tipo = models.CharField(max_length=50, blank=True)  # camioneta, camión, moto, etc.
    foto = models.ImageField(upload_to='vehiculos/', null=True, blank=True)
    activo = models.BooleanField(default=True)

    # Responsable del vehículo
    responsable_nombre = models.CharField(max_length=100, blank=True)
    responsable_email = models.EmailField(blank=True)

    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.placa} - {self.marca} {self.modelo}"

    @property
    def estado_documentos(self):
        """
        Devuelve:
        - 'sin_documentos'
        - 'con_vencidos'
        - 'con_proximos'
        - 'al_dia'
        """
        docs = list(self.documentos.all())
        if not docs:
            return 'sin_documentos'

        estados = [d.estado for d in docs]

        if 'vencido' in estados:
            return 'con_vencidos'
        if 'proximo' in estados:
            return 'con_proximos'
        return 'al_dia'


class TipoDocumento(models.Model):
    nombre = models.CharField(max_length=50)  # SOAT, Tecnomecánica, Seguro, etc.
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre


class DocumentoVehiculo(models.Model):
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, related_name='documentos')
    tipo = models.ForeignKey(TipoDocumento, on_delete=models.PROTECT)
    fecha_expedicion = models.DateField(null=True, blank=True)
    fecha_vencimiento = models.DateField()
    archivo = models.FileField(upload_to='documentos_vehiculos/', null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['fecha_vencimiento']

    def __str__(self):
        return f"{self.tipo} - {self.vehiculo.placa}"

    @property
    def estado(self):
        """
        Devuelve: 'vigente', 'proximo', 'vencido'
        """
        hoy = date.today()
        if self.fecha_vencimiento < hoy:
            return 'vencido'
        delta_alerta = 30
        if (self.fecha_vencimiento - hoy).days <= delta_alerta:
            return 'proximo'
        return 'vigente'
