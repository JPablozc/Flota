import os
from datetime import date

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.utils.text import slugify


# =========================
# Helpers para rutas (upload_to)
# =========================

def vehiculo_foto_path(instance, filename):
    """
    Define la ruta lógica donde se guardará la foto del vehículo en Cloudinary.

    Ejemplo:
    vehiculos/ABC123/foto.jpg
    """
    base, ext = os.path.splitext(filename)
    ext = ext.lower() or ".jpg"
    placa = (instance.placa or "sin_placa").upper()
    return f"vehiculos/{placa}/foto{ext}"


def documento_vehiculo_path(instance, filename):
    """
    Define la ruta lógica donde se guardarán los documentos del vehículo en Cloudinary.

    Ejemplo:
    documentos_vehiculos/ABC123/soat/2025-01-01.pdf
    """
    base, ext = os.path.splitext(filename)
    ext = ext.lower() or ".pdf"

    placa = (instance.vehiculo.placa or "sin_placa").upper()
    tipo_slug = slugify(instance.tipo.nombre) if instance.tipo and instance.tipo.nombre else "documento"
    fecha_str = instance.fecha_vencimiento.isoformat() if instance.fecha_vencimiento else "sin_fecha"

    return f"documentos_vehiculos/{placa}/{tipo_slug}/{fecha_str}{ext}"


# =========================
# Modelos
# =========================

class Vehiculo(models.Model):
    placa = models.CharField(max_length=10, unique=True)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    anio = models.PositiveIntegerField(null=True, blank=True)
    tipo = models.CharField(
        max_length=50,
        blank=True,
        help_text="Ej: camioneta, camión, moto, automóvil, etc.",
    )
    foto = models.ImageField(
        upload_to=vehiculo_foto_path,
        null=True,
        blank=True,
        help_text="Foto del vehículo. Se almacena en Cloudinary.",
    )
    activo = models.BooleanField(default=True)

    # Responsable del vehículo
    responsable_nombre = models.CharField(max_length=100, blank=True)
    responsable_email = models.EmailField(blank=True)

    creado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vehiculos_creados",
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Vehículo"
        verbose_name_plural = "Vehículos"
        ordering = ["placa"]

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

    class Meta:
        verbose_name = "Tipo de documento"
        verbose_name_plural = "Tipos de documento"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class DocumentoVehiculo(models.Model):
    vehiculo = models.ForeignKey(
        Vehiculo,
        on_delete=models.CASCADE,
        related_name='documentos',
    )
    tipo = models.ForeignKey(
        TipoDocumento,
        on_delete=models.PROTECT,
    )
    fecha_expedicion = models.DateField(null=True, blank=True)
    fecha_vencimiento = models.DateField()

    archivo = models.FileField(
        upload_to=documento_vehiculo_path,
        null=True,
        blank=True,
        validators=[FileExtensionValidator(['pdf'])],
        help_text="Archivo PDF del documento. Se almacena en Cloudinary.",
    )

    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['fecha_vencimiento']
        verbose_name = "Documento de vehículo"
        verbose_name_plural = "Documentos de vehículos"

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
