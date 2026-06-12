# HU-003: Activar cuenta como paciente
from django import forms

from cuentas.models import Usuario


class ActivarPacienteForm(forms.Form):

    username = forms.CharField(
        label='Nombre de usuario',
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
        label='Contrasena',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label='Confirmar contrasena',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    acepta_terminos = forms.BooleanField(
        label='Acepto los terminos y condiciones',
        required=True
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if Usuario.objects.filter(username=username).exists():
            raise forms.ValidationError('Este nombre de usuario ya existe.')
        return username

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Las contrasenas no coinciden.')
        if p1 and len(p1) < 8:
            raise forms.ValidationError('La contrasena debe tener al menos 8 caracteres.')
        return cleaned
