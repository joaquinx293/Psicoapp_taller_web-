# HU-001: Registro de especialista
# HU-002: Aceptar términos y condiciones (campo acepta_terminos)
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from ..models import Especialidad, Usuario


class RegistroEspecialistaForm(UserCreationForm):

    first_name = forms.CharField(
        label='Nombre',
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label='Apellido',
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    especialidad = forms.ModelChoiceField(
        label='Especialidad',
        queryset=Especialidad.objects.all(),
        empty_label='Selecciona una especialidad',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    # HU-002: aceptación de términos y condiciones
    acepta_terminos = forms.BooleanField(
        label='Acepto los términos y condiciones',
        required=True
    )

    class Meta:
        model = Usuario
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'especialidad', 'password1', 'password2', 'acepta_terminos'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise ValidationError('Este correo ya está registrado.')
        return email

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.rol = Usuario.ROL_ESPECIALISTA
        usuario.estado = Usuario.PENDIENTE
        if commit:
            usuario.save()
        return usuario
