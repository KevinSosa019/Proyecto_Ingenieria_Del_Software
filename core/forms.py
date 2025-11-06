from django import forms
from .models import Usuario, Maquina, OrdenTrabajo
from .models import OrdenTrabajo, Maquina, Tipo, Prioridad, Estado, Tecnico, Usuario


class UsuarioForm(forms.ModelForm):
    contraseña = forms.CharField(widget=forms.PasswordInput)
    confirmar_contraseña = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ['primer_nombre', 'segundo_nombre', 'primer_apellido', 'segundo_apellido',
                  'email', 'telefono', 'rol', 'contraseña']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # No requerir contraseña al editar
            self.fields['contraseña'].required = False
            self.fields['confirmar_contraseña'].required = False

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Este correo electrónico ya está registrado')
        return email

    def clean(self):
        cleaned_data = super().clean()
        contraseña = cleaned_data.get("contraseña")
        confirmar = cleaned_data.get("confirmar_contraseña")

        if contraseña != confirmar:
            raise forms.ValidationError("Las contraseñas no coinciden")


class MaquinaForm(forms.ModelForm):
    class Meta:
        model = Maquina
        fields = [
            'numero_serie',
            'modelo',
            'fecha_adquisicion',
            'estado',
            'ubicacion',
            'proveedor',
            'usuario_asignado',
            'notas'
        ]
        widgets = {
            'fecha_adquisicion': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notas': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
        
        
        
        
class OrdenTrabajoForm(forms.ModelForm):
    tecnico = forms.ModelChoiceField(
        queryset=Tecnico.objects.all(),
        required=False,
        empty_label="Seleccione un técnico"
    )

    class Meta:
        model = OrdenTrabajo
        fields = [
            'codigo', 'maquina', 'tipo', 'prioridad', 'estado', 'descripcion',
            'tecnico', 'usuario_creador', 'fecha_creacion', 'fecha_asignacion',
            'fecha_inicio', 'fecha_finalizacion'
        ]
        widgets = {
            'fecha_creacion': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'fecha_asignacion': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'fecha_inicio': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'fecha_finalizacion': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
