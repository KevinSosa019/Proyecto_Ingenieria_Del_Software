
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
    notas = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'maquinas'
        managed = False

    def __str__(self):
        return self.numero_serie