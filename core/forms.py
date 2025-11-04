from django import forms
from .models import Usuario

class UsuarioForm(forms.ModelForm):
    contraseña = forms.CharField(widget=forms.PasswordInput)
    confirmar_contraseña = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ['primer_nombre', 'segundo_nombre', 'primer_apellido', 'segundo_apellido',
                  'email', 'telefono', 'rol', 'contraseña']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo electrónico ya está registrado')
        return email

    def clean(self):
        cleaned_data = super().clean()
        contraseña = cleaned_data.get("contraseña")
        confirmar = cleaned_data.get("confirmar_contraseña")

        if contraseña != confirmar:
            raise forms.ValidationError("Las contraseñas no coinciden")
