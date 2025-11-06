
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

class RolUsuario(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=20)

    class Meta:
        db_table = 'roles_usuario'
        managed = False

    def __str__(self):
        return self.nombre


class Usuario(models.Model):
    id = models.AutoField(primary_key=True)
    primer_nombre = models.CharField(max_length=50)
    segundo_nombre = models.CharField(max_length=50, null=True, blank=True)
    primer_apellido = models.CharField(max_length=50)
    segundo_apellido = models.CharField(max_length=50, null=True, blank=True)
    email = models.CharField(max_length=100, unique=True)
    contraseña = models.CharField(max_length=255)
    rol = models.ForeignKey(RolUsuario, on_delete=models.DO_NOTHING, db_column='rol_id', null=True, blank=True)
    telefono = models.CharField(max_length=20, unique=True, null=True, blank=True)
    activo = models.BooleanField(default=True)
    ultimo_login = models.DateTimeField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'usuarios'
        managed = False  # Muy importante: Django NO tocará la tabla

    def __str__(self):
        return f"{self.primer_nombre} {self.primer_apellido}"



class EstadoMaquina(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=20)

    class Meta:
        db_table = 'estados_maquina'
        managed = False

    def __str__(self):
        return self.nombre


class Proveedor(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    contacto = models.CharField(max_length=100, null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    direccion = models.TextField(null=True, blank=True)
    rtn = models.CharField(max_length=50, null=True, blank=True)
    tipo_servicio = models.CharField(max_length=100, null=True, blank=True)
    calificacion = models.TextField(null=True, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        db_table = 'proveedores'
        managed = False

    def __str__(self):
        return self.nombre


class Maquina(models.Model):
    id = models.AutoField(primary_key=True)
    numero_serie = models.CharField(max_length=50, unique=True)
    modelo = models.CharField(max_length=100)
    fecha_adquisicion = models.DateField(null=True, blank=True)
    estado = models.ForeignKey(EstadoMaquina, on_delete=models.DO_NOTHING, db_column='estado_id', null=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.DO_NOTHING, db_column='proveedor_id', null=True)
    # 🔹 Nuevos campos que existen en tu BD:
    ubicacion = models.ForeignKey('Ubicacion', on_delete=models.DO_NOTHING, db_column='ubicacion_id', null=True)
    usuario_asignado = models.ForeignKey('Usuario', on_delete=models.DO_NOTHING, db_column='usuario_asignado_id', null=True)
    notas = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'maquinas'
        managed = False

    def __str__(self):
        return self.numero_serie


class Ubicacion(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    direccion = models.TextField(null=True, blank=True)
    ciudad = models.CharField(max_length=50, null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    activa = models.BooleanField(default=True)

    class Meta:
        db_table = 'ubicaciones'
        managed = False

    def __str__(self):
        return self.nombre
    
    
    #---------------------------------------------------------------
    

class InventarioRepuesto(models.Model):
    id = models.AutoField(primary_key=True)
    nombre_repuesto = models.CharField(max_length=100, unique=True)
    cantidad = models.IntegerField(default=0)
    ultima_salida_fecha = models.DateTimeField(null=True, blank=True)
    ultima_salida_cantidad = models.IntegerField(null=True, blank=True)
    notas = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'inventario_repuestos'
        managed = False

    def __str__(self):
        return self.nombre_repuesto
    

class MantenimientoDetalleRepuesto(models.Model):
    id = models.AutoField(primary_key=True)
    mantenimiento = models.ForeignKey(
        'Mantenimiento',
        on_delete=models.CASCADE,  # elimina los detalles al eliminar mantenimiento
        db_column='mantenimiento_id'
    )
    inventario_repuesto = models.ForeignKey(
        'InventarioRepuesto',
        on_delete=models.DO_NOTHING,
        db_column='inventario_repuesto_id'
    )
    cantidad = models.IntegerField()

    class Meta:
        db_table = 'mantenimientos_detalle_repuestos'
        managed = False

    
class ResultadoMantenimiento(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=20)

    class Meta:
        db_table = 'resultados_mantenimiento'
        managed = False

    def __str__(self):
        return self.nombre

    
class Mantenimiento(models.Model):
    id = models.AutoField(primary_key=True)
    orden_trabajo = models.ForeignKey(
        'OrdenTrabajo',
        on_delete=models.CASCADE,  # 🔥 cambio importante
        db_column='orden_trabajo_id'
    )
    acciones_realizadas = models.TextField(null=True, blank=True)
    fecha_realizacion = models.DateTimeField(null=True, blank=True)
    resultado = models.ForeignKey(
        'ResultadoMantenimiento',
        on_delete=models.SET_NULL,
        db_column='resultado_id',
        null=True,
        blank=True
    )
    observaciones = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'mantenimientos'
        managed = False


class Tecnico(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey('Usuario', on_delete=models.DO_NOTHING, db_column='usuario_id')
    disponibilidad = models.CharField(max_length=20, default='disponible')
    vehiculo_asignado = models.CharField(max_length=50, null=True, blank=True)
    herramienta_asignada = models.TextField(null=True, blank=True)
    calificacion_promedio = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'tecnicos'
        managed = False

    def __str__(self):
        return f"{self.usuario.primer_nombre} {self.usuario.primer_apellido}"

class Tipo(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=20)

    class Meta:
        db_table = 'tipo'
        managed = False

    def __str__(self):
        return self.nombre


class Prioridad(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=20)

    class Meta:
        db_table = 'prioridad'
        managed = False

    def __str__(self):
        return self.nombre


class Estado(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=20)

    class Meta:
        db_table = 'estado'
        managed = False

    def __str__(self):
        return self.nombre


class OrdenTrabajo(models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=20, unique=True)
    maquina = models.ForeignKey('Maquina', on_delete=models.DO_NOTHING, db_column='maquina_id')
    tipo = models.ForeignKey(Tipo, on_delete=models.DO_NOTHING, db_column='tipo_id')
    prioridad = models.ForeignKey(Prioridad, on_delete=models.DO_NOTHING, db_column='prioridad_id')
    estado = models.ForeignKey(Estado, on_delete=models.DO_NOTHING, db_column='estado_id')
    descripcion = models.TextField()
    tecnico = models.ForeignKey('Tecnico', on_delete=models.DO_NOTHING, db_column='tecnico_id', null=True, blank=True)
    usuario_creador = models.ForeignKey('Usuario', on_delete=models.DO_NOTHING, db_column='usuario_creador_id')
    fecha_creacion = models.DateTimeField(null=True, blank=True)
    fecha_asignacion = models.DateTimeField(null=True, blank=True)
    fecha_inicio = models.DateTimeField(null=True, blank=True)
    fecha_finalizacion = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'ordenes_trabajo'
        managed = False

    def __str__(self):
        return self.codigo
