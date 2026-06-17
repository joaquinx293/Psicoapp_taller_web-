# HU-007: Invitar paciente por correo
from django import forms

from ..models import InvitacionPaciente
from cuentas.models import Usuario


class InvitarPacienteForm(forms.ModelForm):

    class Meta:
        model = InvitacionPaciente
        fields = ['nombre_paciente', 'correo_paciente']
        widgets = {
            'nombre_paciente': forms.TextInput(attrs={'class': 'form-control'}),
            'correo_paciente': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'nombre_paciente': 'Nombre del paciente',
            'correo_paciente': 'Correo electrónico',
        }

    def clean_correo_paciente(self):
        correo = self.cleaned_data.get('correo_paciente')
        if Usuario.objects.filter(email=correo).exists():
            raise forms.ValidationError(
                'Ya existe una cuenta con este correo.'
            )
        return correo
