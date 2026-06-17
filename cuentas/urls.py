from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'cuentas'

urlpatterns = [
    path('registro/', views.registro_especialista, name='registro'),
    path('login/', auth_views.LoginView.as_view(
        template_name='cuentas/login.html'
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('redireccion/', views.redireccion_por_rol, name='redireccion'),
    path('perfil/', views.perfil_paciente, name='perfil_paciente'),

    # HU-006: dashboard admin
    path('admin-dashboard/', views.dashboard_admin, name='dashboard_admin'),
    path('admin-dashboard/aprobar/<int:pk>/', views.aprobar_especialista, name='aprobar_especialista'),
    path('admin-dashboard/rechazar/<int:pk>/', views.rechazar_especialista, name='rechazar_especialista'),

    # HU-005: recuperacion de contrasena
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='cuentas/password_reset.html',
        email_template_name='cuentas/password_reset_email.html',
        success_url='/cuentas/password_reset_done/'
    ), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(
        template_name='cuentas/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='cuentas/password_reset_confirm.html',
        success_url='/cuentas/reset_complete/'
    ), name='password_reset_confirm'),
    path('reset_complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='cuentas/password_reset_complete.html'
    ), name='password_reset_complete'),
]