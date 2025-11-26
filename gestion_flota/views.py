from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.db.models import Q

from .models import Vehiculo, DocumentoVehiculo
from .forms import VehiculoForm, DocumentoVehiculoForm

from django.http import HttpResponseForbidden
from .permissions import user_is_operador, user_is_admin

import csv
from django.http import HttpResponse



@login_required
def dashboard(request):
    hoy = date.today()
    proximos = DocumentoVehiculo.objects.filter(
        fecha_vencimiento__gte=hoy,
        fecha_vencimiento__lte=hoy + timedelta(days=30)
    )
    vencidos = DocumentoVehiculo.objects.filter(
        fecha_vencimiento__lt=hoy
    )
    total_vehiculos = Vehiculo.objects.filter(activo=True).count()

    context = {
        'total_vehiculos': total_vehiculos,
        'proximos': proximos,
        'vencidos': vencidos,
    }
    return render(request, 'gestion_flota/dashboard.html', context)


@method_decorator(login_required, name='dispatch')
class VehiculoListView(ListView):
    model = Vehiculo
    template_name = 'gestion_flota/vehiculo_list.html'
    context_object_name = 'vehiculos'

    def get_queryset(self):
        qs = Vehiculo.objects.filter(activo=True).order_by('placa')
        q = self.request.GET.get('q')

        if q:
            qs = qs.filter(
                Q(placa__icontains=q) |
                Q(marca__icontains=q) |
                Q(modelo__icontains=q) |
                Q(tipo__icontains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        return context


@method_decorator(login_required, name='dispatch')
class VehiculoDetailView(DetailView):
    model = Vehiculo
    template_name = 'gestion_flota/vehiculo_detail.html'
    context_object_name = 'vehiculo'


@login_required
def vehiculo_create(request):
    if not user_is_operador(request.user):
        return HttpResponseForbidden("No tienes permiso para crear vehículos.")

    if request.method == 'POST':
        form = VehiculoForm(request.POST, request.FILES)
        if form.is_valid():
            vehiculo = form.save(commit=False)
            vehiculo.creado_por = request.user
            vehiculo.save()
            return redirect('vehiculo_detail', pk=vehiculo.pk)
    else:
        form = VehiculoForm()
    return render(request, 'gestion_flota/vehiculo_form.html', {'form': form})


@login_required
def vehiculo_update(request, pk):
    vehiculo = get_object_or_404(Vehiculo, pk=pk)

    if not user_is_operador(request.user):
        return HttpResponseForbidden("No tienes permiso para editar vehículos.")

    if request.method == 'POST':
        form = VehiculoForm(request.POST, request.FILES, instance=vehiculo)
        if form.is_valid():
            form.save()
            return redirect('vehiculo_detail', pk=vehiculo.pk)
    else:
        form = VehiculoForm(instance=vehiculo)
    return render(request, 'gestion_flota/vehiculo_form.html', {'form': form, 'vehiculo': vehiculo})


@login_required
def documento_create(request, vehiculo_id):
    vehiculo = get_object_or_404(Vehiculo, pk=vehiculo_id)

    if not user_is_operador(request.user):
        return HttpResponseForbidden("No tienes permiso para crear documentos.")

    if request.method == 'POST':
        form = DocumentoVehiculoForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.vehiculo = vehiculo
            doc.save()
            return redirect('vehiculo_detail', pk=vehiculo.pk)
    else:
        form = DocumentoVehiculoForm()
    return render(request, 'gestion_flota/documento_form.html', {'form': form, 'vehiculo': vehiculo})


@login_required
def documento_update(request, pk):
    """
    Editar un documento existente
    """
    doc = get_object_or_404(DocumentoVehiculo, pk=pk)
    vehiculo = doc.vehiculo

    if not user_is_operador(request.user):
        return HttpResponseForbidden("No tienes permiso para editar documentos.")

    if request.method == 'POST':
        form = DocumentoVehiculoForm(request.POST, request.FILES, instance=doc)
        if form.is_valid():
            form.save()
            return redirect('vehiculo_detail', pk=vehiculo.pk)
    else:
        form = DocumentoVehiculoForm(instance=doc)

    context = {
        'form': form,
        'vehiculo': vehiculo,
        'documento': doc,
    }
    return render(request, 'gestion_flota/documento_form.html', context)

@login_required
def vehiculo_export_csv(request):
    """
    Exporta los vehículos a CSV, respetando el filtro de búsqueda 'q'.
    """
    from .models import Vehiculo  # por si no está ya importado arriba

    q = request.GET.get('q')

    qs = Vehiculo.objects.filter(activo=True).order_by('placa')
    if q:
        from django.db.models import Q
        qs = qs.filter(
            Q(placa__icontains=q) |
            Q(marca__icontains=q) |
            Q(modelo__icontains=q) |
            Q(tipo__icontains=q)
        )

    response = HttpResponse(content_type='text/csv')
    nombre_filtro = q if q else "todos"
    response['Content-Disposition'] = f'attachment; filename="vehiculos_flota_{nombre_filtro}.csv"'

    writer = csv.writer(response)
    # Encabezados
    writer.writerow([
        'Placa',
        'Marca',
        'Modelo',
        'Año',
        'Tipo',
        'Activo',
        'Responsable',
        'Email responsable',
    ])

    for v in qs:
        writer.writerow([
            v.placa,
            v.marca,
            v.modelo,
            v.anio or '',
            v.tipo,
            'Sí' if v.activo else 'No',
            v.responsable_nombre or '',
            v.responsable_email or '',
        ])

    return response

@login_required
def documento_export_csv(request):
    """
    Exporta los documentos a CSV, respetando el filtro 'estado'
    (vencidos, proximos, vigentes o todos).
    """
    hoy = date.today()
    dias_alerta = 30
    estado = request.GET.get('estado')

    docs = DocumentoVehiculo.objects.select_related('vehiculo', 'tipo')

    if estado == 'vencidos':
        docs = docs.filter(fecha_vencimiento__lt=hoy)
    elif estado == 'proximos':
        docs = docs.filter(
            fecha_vencimiento__gte=hoy,
            fecha_vencimiento__lte=hoy + timedelta(days=dias_alerta)
        )
    elif estado == 'vigentes':
        docs = docs.filter(
            fecha_vencimiento__gt=hoy + timedelta(days=dias_alerta)
        )

    # Preparamos la respuesta HTTP como archivo CSV
    nombre_filtro = estado if estado else "todos"
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="documentos_flota_{nombre_filtro}.csv"'

    writer = csv.writer(response)
    # Encabezados
    writer.writerow([
        'Placa',
        'Tipo documento',
        'Fecha expedición',
        'Fecha vencimiento',
        'Estado',
        'Responsable',
        'Email responsable',
    ])

    for d in docs.order_by('fecha_vencimiento'):
        writer.writerow([
            d.vehiculo.placa,
            d.tipo.nombre,
            d.fecha_expedicion or '',
            d.fecha_vencimiento,
            d.estado,
            d.vehiculo.responsable_nombre or '',
            d.vehiculo.responsable_email or '',
        ])

    return response

@login_required
def documento_delete(request, pk):
    """
    Eliminar un documento (con pantalla de confirmación)
    """
    doc = get_object_or_404(DocumentoVehiculo, pk=pk)
    vehiculo = doc.vehiculo

    if not user_is_admin(request.user):
        return HttpResponseForbidden("Solo un administrador puede eliminar documentos.")

    if request.method == 'POST':
        doc.delete()
        return redirect('vehiculo_detail', pk=vehiculo.pk)

    context = {
        'vehiculo': vehiculo,
        'documento': doc,
    }
    return render(request, 'gestion_flota/documento_confirm_delete.html', context)

from datetime import date, timedelta
# ya debes tener este import arriba, si no, asegúrate de que esté

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import DocumentoVehiculo

# ... (el resto de vistas que ya tienes)

@login_required
def documento_list(request):
    hoy = date.today()
    dias_alerta = 30

    estado = request.GET.get('estado')  # 'vencidos', 'proximos', 'vigentes' o None

    docs = DocumentoVehiculo.objects.select_related('vehiculo', 'tipo')

    if estado == 'vencidos':
        docs = docs.filter(fecha_vencimiento__lt=hoy)
    elif estado == 'proximos':
        docs = docs.filter(
            fecha_vencimiento__gte=hoy,
            fecha_vencimiento__lte=hoy + timedelta(days=dias_alerta)
        )
    elif estado == 'vigentes':
        docs = docs.filter(
            fecha_vencimiento__gt=hoy + timedelta(days=dias_alerta)
        )
    # si no hay estado, mostramos todo

    total_vencidos = DocumentoVehiculo.objects.filter(fecha_vencimiento__lt=hoy).count()
    total_proximos = DocumentoVehiculo.objects.filter(
        fecha_vencimiento__gte=hoy,
        fecha_vencimiento__lte=hoy + timedelta(days=dias_alerta)
    ).count()
    total_vigentes = DocumentoVehiculo.objects.filter(
        fecha_vencimiento__gt=hoy + timedelta(days=dias_alerta)
    ).count()
    total_todos = DocumentoVehiculo.objects.count()

    context = {
        'documentos': docs.order_by('fecha_vencimiento'),
        'estado': estado,
        'total_vencidos': total_vencidos,
        'total_proximos': total_proximos,
        'total_vigentes': total_vigentes,
        'total_todos': total_todos,
    }
    return render(request, 'gestion_flota/documento_list.html', context)
