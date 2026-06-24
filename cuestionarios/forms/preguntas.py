# HU-012: Agregar pregunta
# HU-013: Editar pregunta
from django import forms
from ..models import Pregunta


class PreguntaForm(forms.ModelForm):

    etiqueta_opcion_1 = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Ej: Triste',
        }),
        label='Etiqueta opción 1 (valor 0)',
    )
    etiqueta_opcion_2 = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Ej: Feliz',
        }),
        label='Etiqueta opción 2 (valor 1)',
    )

    class Meta:
        model = Pregunta
        fields = ['texto', 'escala', 'peso', 'etiqueta_opcion_1', 'etiqueta_opcion_2']
        widgets = {
            'texto': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': 250,
                'placeholder': 'Escribe la pregunta...',
            }),
            'escala': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_escala',
            }),
            'peso': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 10,
            }),
        }
        labels = {
            'texto': 'Texto de la pregunta',
            'escala': 'Tipo de respuesta',
            'peso': 'Peso en el puntaje (0 a 10)',
        }

    def clean(self):
        cleaned = super().clean()
        escala = cleaned.get('escala')

        # Etiquetas requeridas para tipo binario
        if escala == Pregunta.ESCALA_BINARIO:
            if not cleaned.get('etiqueta_opcion_1'):
                self.add_error('etiqueta_opcion_1', 'Debes escribir la primera etiqueta.')
            if not cleaned.get('etiqueta_opcion_2'):
                self.add_error('etiqueta_opcion_2', 'Debes escribir la segunda etiqueta.')

        # Tipos sin puntaje: forzar peso a 0
        if escala in Pregunta.ESCALAS_SIN_PUNTAJE:
            cleaned['peso'] = 0

        return cleaned
