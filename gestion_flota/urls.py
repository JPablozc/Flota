from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    path('vehiculos/', views.VehiculoListView.as_view(), name='vehiculo_list'),
    path('vehiculos/nuevo/', views.vehiculo_create, name='vehiculo_create'),
    path('vehiculos/<int:pk>/', views.VehiculoDetailView.as_view(), name='vehiculo_detail'),
    path('vehiculos/<int:pk>/editar/', views.vehiculo_update, name='vehiculo_update'),
    path('vehiculos/exportar/csv/', views.vehiculo_export_csv, name='vehiculo_export_csv'),  # 👈 nueva

    path('vehiculos/<int:vehiculo_id>/documentos/nuevo/', views.documento_create, name='documento_create'),
    path('documentos/<int:pk>/editar/', views.documento_update, name='documento_update'),
    path('documentos/<int:pk>/eliminar/', views.documento_delete, name='documento_delete'),

    path('documentos/', views.documento_list, name='documento_list'),
    path('documentos/exportar/csv/', views.documento_export_csv, name='documento_export_csv'),
]
