# HU-003: Paso 1 — ingresar correo y PIN para activar cuenta
from django import forms


class IngresarPinForm(forms.Form):

    correo = forms.EmailField(
        label='Tu correo electronico',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    pin = forms.CharField(
        label='Codigo de activacion (6 digitos)',
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '123456',
            'inputmode': 'numeric',
        })
    )

    def clean_pin(self):
        pin = self.cleaned_data.get('pin', '')
        if not pin.isdigit():
            raise forms.ValidationError('El codigo debe contener solo numeros.')
        return pin
