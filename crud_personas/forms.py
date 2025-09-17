from django import forms
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError
from .models import Persona, Correo, Telefono, Direccion
import base64
from django.core.files.base import ContentFile
from datetime import datetime

class PersonaFormulario(forms.ModelForm):
    imagen_recortada = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Persona
        fields = ['nombres', 'apellido_paterno', 'apellido_materno', 'fecha_nacimiento', 'alias', 'fotografia']
        widgets = {
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido_paterno': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido_materno': forms.TextInput(attrs={'class': 'form-control'}),
            'alias': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def save(self, commit=True):
        instancia = super().save(commit=False)
        data = self.cleaned_data.get('imagen_recortada')
        if data:
            try:
                formato, contenido = data.split(';base64,')
                ext = 'png' if 'png' in formato.lower() else 'jpg'
                nombre_archivo = f"recorte_{datetime.now().strftime('%Y%m%d%H%M%S')}.{ext}"
                instancia.fotografia = ContentFile(base64.b64decode(contenido), name=nombre_archivo)
            except Exception:
                pass
        if commit:
            instancia.save()
        return instancia

class CorreoFormulario(forms.ModelForm):
    def clean_correo(self):
        return (self.cleaned_data.get('correo') or '').strip()  # EmailField valida formato

    class Meta:
        model = Correo
        fields = ['correo']
        widgets = {
            'correo': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@dominio.com'})
        }

class TelefonoFormulario(forms.ModelForm):
    def clean_numero(self):
        numero = (self.cleaned_data.get('numero') or '').strip()
        if numero and not numero.isdigit():
            raise ValidationError('El teléfono debe contener solo números.')
        if len(numero) > 10:
            raise ValidationError('El teléfono debe tener máximo 10 dígitos.')
        return numero

    class Meta:
        model = Telefono
        fields = ['etiqueta', 'numero']
        widgets = {
            'etiqueta': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'casa, oficina, celular...'}),
            'numero': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': '0000000000',
                'inputmode': 'numeric', 'pattern': r'\d{1,10}', 'maxlength': '10'
            }),
        }

class DireccionFormulario(forms.ModelForm):
    def clean_cp(self):
        cp = (self.cleaned_data.get('cp') or '').strip()
        if cp and not cp.isdigit():
            raise ValidationError('El C.P. debe contener solo números.')
        return cp

    class Meta:
        model = Direccion
        fields = ['linea1','linea2','ciudad','estado','cp','pais']
        widgets = {
            'linea1': forms.TextInput(attrs={'class': 'form-control'}),
            'linea2': forms.TextInput(attrs={'class': 'form-control'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.TextInput(attrs={'class': 'form-control'}),
            'cp': forms.TextInput(attrs={'class': 'form-control', 'inputmode': 'numeric', 'pattern': r'\d*'}),
            'pais': forms.TextInput(attrs={'class': 'form-control'}),
        }

CorreoFormsetCrear = inlineformset_factory(
    Persona, Correo,
    form=CorreoFormulario,
    fields=['correo'],
    extra=1, can_delete=True,
)

TelefonoFormsetCrear = inlineformset_factory(
    Persona, Telefono,
    form=TelefonoFormulario,
    fields=['etiqueta', 'numero'],
    extra=1, can_delete=True,
)

DireccionFormsetCrear = inlineformset_factory(
    Persona, Direccion,
    form=DireccionFormulario,
    fields=['linea1','linea2','ciudad','estado','cp','pais'],
    extra=1, can_delete=True,
)

CorreoFormsetEditar = inlineformset_factory(
    Persona, Correo,
    form=CorreoFormulario,
    fields=['correo'],
    extra=0, can_delete=True,
)

TelefonoFormsetEditar = inlineformset_factory(
    Persona, Telefono,
    form=TelefonoFormulario,
    fields=['etiqueta', 'numero'],
    extra=0, can_delete=True,
)

DireccionFormsetEditar = inlineformset_factory(
    Persona, Direccion,
    form=DireccionFormulario,
    fields=['linea1','linea2','ciudad','estado','cp','pais'],
    extra=0, can_delete=True,
)
