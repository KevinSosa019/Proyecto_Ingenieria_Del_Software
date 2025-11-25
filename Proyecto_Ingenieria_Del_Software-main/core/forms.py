from django import forms
from .models import Usuario, Maquina, OrdenTrabajo
from .models import OrdenTrabajo, Maquina, Tipo, Prioridad, Estado, Tecnico, Usuario, Proveedor
from django.utils import timezone


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

    # -------------------------------
    # VALIDACIÓN DE CORREO
    # -------------------------------
    def clean_email(self):
        email = self.cleaned_data.get('email')

        # Validar que tenga @
        if "@" not in email:
            raise forms.ValidationError("El correo debe contener '@'.")

        # Evitar correos duplicados
        if Usuario.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Este correo electrónico ya está registrado')

        return email

    # -------------------------------
    # VALIDACIÓN DE CONTRASEÑA
    # -------------------------------
    def clean(self):
        cleaned_data = super().clean()
        contraseña = cleaned_data.get("contraseña")
        confirmar = cleaned_data.get("confirmar_contraseña")

        # Validar coincidencia
        if contraseña != confirmar:
            raise forms.ValidationError("Las contraseñas no coinciden")

        # Validar longitud solo si se ingresó una nueva contraseña
        if contraseña and len(contraseña) < 8:
            raise forms.ValidationError("La contraseña debe tener al menos 8 caracteres")

        return cleaned_data




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
            'fecha_adquisicion': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'max': timezone.now().date()  # Esto deshabilita fechas futuras
                }
            ),
            'notas': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar usuarios asignados si quieres que solo aparezcan Clientes y Administradores
        self.fields['usuario_asignado'].queryset = Usuario.objects.filter(
            rol__nombre__in=['Cliente', 'Administrador']
        )

     #---------------------------------------------------------------

          

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        hoy_str = timezone.now().strftime('%Y-%m-%dT%H:%M')
        for field_name in ['fecha_creacion', 'fecha_asignacion', 'fecha_inicio', 'fecha_finalizacion']:
            self.fields[field_name].widget.attrs['min'] = hoy_str

    def clean(self):
        cleaned_data = super().clean()
        for field_name in ['fecha_creacion', 'fecha_asignacion', 'fecha_inicio', 'fecha_finalizacion']:
            fecha = cleaned_data.get(field_name)
            if fecha and fecha < timezone.now():
                self.add_error(field_name, "No se puede seleccionar una fecha anterior a hoy")
        return cleaned_data

#---------------------------------------------------------------
class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'contacto', 'telefono', 'email', 'direccion', 'rtn', 'activo']
        
    def clean_email(self):
        email = self.cleaned_data.get('email')

        # Validar que tenga @
        if "@" not in email:
            raise forms.ValidationError("El correo debe contener '@'.")

        return email