from django.shortcuts import redirect
from django.urls import path
from . import views

app_name = 'gestion_usuarios'

urlpatterns = [
    # /gestion/ sin subpath → redirige al dashboard del especialista
    path('', lambda request: redirect('gestion_usuarios:dashboard')),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('invitar/', views.invitar_paciente, name='invitar_paciente'),
    path('pacientes/', views.listado_pacientes, name='listado_pacientes'),

    # HU-003: activación por PIN (2 pasos)
    path('activar/', views.ingresar_pin, name='ingresar_pin'),
    path('activar/completar/', views.completar_registro, name='completar_registro'),

    # HU-025: Configurar pregunta diaria por paciente
    path('pacientes/<int:paciente_id>/pregunta-diaria/', views.pregunta_diaria, name='pregunta_diaria'),

    # HU-035: Tasa de completitud de cuestionarios del paciente
    path('pacientes/<int:paciente_id>/completitud/', views.completitud_paciente, name='completitud_paciente'),
]
