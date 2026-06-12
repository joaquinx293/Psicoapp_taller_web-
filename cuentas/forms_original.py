from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import Usuario


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
        label='Correo electronico',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    numero_registro = forms.CharField(
        label='Numero de registro profesional',
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    especialidad = forms.CharField(
        label='Especialidad',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    acepta_terminos = forms.BooleanField(
        label='Acepto los terminos y condiciones',
        required=True
    )
    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.rol = Usuario.ROL_ESPECIALISTA
        usuario.estado = Usuario.PENDIENTE      # <-- clave
        if commit:
            usuario.save()
        return usuario

    class Meta:
        model = Usuario
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'numero_registro', 'especialidad',
            'password1', 'password2', 'acepta_terminos'
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
            raise ValidationError('Este correo ya esta registrado.')
        return email