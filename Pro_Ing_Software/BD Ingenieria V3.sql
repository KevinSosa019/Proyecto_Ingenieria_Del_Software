CREATE DATABASE MaquinasdePoker;
GO

USE MaquinasdePoker;
GO

CREATE TABLE [inventario_repuestos] (
  [id] int PRIMARY KEY IDENTITY(1, 1),
  [nombre_repuesto] nvarchar(100) UNIQUE NOT NULL,
  [cantidad] int DEFAULT (0),
  [ultima_salida_fecha] datetime,
  [ultima_salida_cantidad] int,
  [notas] nvarchar(max)
)
GO

CREATE TABLE [mantenimientos] (
  [id] int PRIMARY KEY IDENTITY(1, 1),
  [orden_trabajo_id] int,
  [acciones_realizadas] nvarchar(max),
  [fecha_realizacion] datetime2,
  [resultado_id] int,
  [observaciones] nvarchar(max)
)
GO

CREATE TABLE [mantenimientos_detalle_repuestos] (
  [id] int PRIMARY KEY IDENTITY(1, 1),
  [mantenimiento_id] int,
  [inventario_repuesto_id] int,
  [cantidad] int
)
GO

CREATE TABLE [maquinas] (
  [id] int PRIMARY KEY IDENTITY(1, 1),
  [numero_serie] nvarchar(50) UNIQUE,
  [modelo] nvarchar(100),
  [fecha_adquisicion] date,
  [estado_id] int,
  [ubicacion_id] int,
  [proveedor_id] int,
  [usuario_asignado_id] int,
  [notas] nvarchar(max)
)
GO

CREATE TABLE [ordenes_trabajo] (
  [id] int PRIMARY KEY IDENTITY(1, 1),
  [codigo] nvarchar(20) UNIQUE,
  [maquina_id] int,
  [tipo_id] int,
  [prioridad_id] int,
  [estado_id] int,
  [descripcion] nvarchar(max),
  [tecnico_id] int,
  [usuario_creador_id] int,
  [fecha_creacion] datetime DEFAULT (getdate()),
  [fecha_asignacion] datetime,
  [fecha_inicio] datetime,
  [fecha_finalizacion] datetime
)
GO

CREATE TABLE [proveedores] (
  [id] int PRIMARY KEY IDENTITY(1, 1),
  [nombre] nvarchar(100),
  [contacto] nvarchar(100),
  [telefono] nvarchar(20),
  [email] nvarchar(100),
  [direccion] text,
  [rtn] nvarchar(50),
  [tipo_servicio] nvarchar(100),
  [calificacion] nvarchar(max),
  [activo] bit DEFAULT (1)
)
GO

CREATE TABLE [tecnicos] (
  [id] int PRIMARY KEY IDENTITY(1, 1),
  [usuario_id] int,
  [disponibilidad] nvarchar(20) DEFAULT 'disponible',
  [vehiculo_asignado] nvarchar(50),
  [herramienta_asignada] nvarchar(max),
  [calificacion_promedio] decimal(3,2)
)
GO

CREATE TABLE [ubicaciones] (
  [id] int PRIMARY KEY IDENTITY(1, 1),
  [nombre] nvarchar(100),
  [direccion] nvarchar(max),
  [ciudad] nvarchar(50),
  [telefono] nvarchar(20),
  [activa] bit DEFAULT (1)
)
GO

CREATE TABLE [usuarios] (
  [id] int PRIMARY KEY IDENTITY(1, 1),
  [primer_nombre] nvarchar(50) NOT NULL,
  [segundo_nombre] nvarchar(50),
  [primer_apellido] nvarchar(50) NOT NULL,
  [segundo_apellido] nvarchar(50),
  [email] nvarchar(100) UNIQUE,
  [contraseña] varchar(255) NOT NULL,
  [rol_id] int,
  [telefono] nvarchar(20) UNIQUE,
  [activo] bit DEFAULT (1),
  [ultimo_login] datetime,
  [fecha_creacion] datetime DEFAULT (getdate()),
  [fecha_actualizacion] datetime
)
GO

CREATE TABLE [resultados_mantenimiento] (
  [id] int PRIMARY KEY IDENTITY(1, 1),
  [nombre] nvarchar(20)
)
GO

CREATE TABLE [estados_maquina] (
  [id] int PRIMARY KEY IDENTITY(1, 1),
  [nombre] nvarchar(20)
)
GO

CREATE TABLE [roles_usuario] (
  [id] int PRIMARY KEY IDENTITY(1, 1),
  [nombre] nvarchar(20)
)
GO

CREATE TABLE [tipo] (
  [id] int PRIMARY KEY IDENTITY(1, 1),
  [nombre] nvarchar(20)
)
GO

CREATE TABLE [prioridad] (
  [id] int PRIMARY KEY IDENTITY(1, 1),
  [nombre] nvarchar(20)
)
GO

CREATE TABLE [estado] (
  [id] int PRIMARY KEY IDENTITY(1, 1),
  [nombre] nvarchar(20)
)
GO

ALTER TABLE [mantenimientos] ADD FOREIGN KEY ([orden_trabajo_id]) REFERENCES [ordenes_trabajo] ([id])
GO

ALTER TABLE [mantenimientos] ADD FOREIGN KEY ([resultado_id]) REFERENCES [resultados_mantenimiento] ([id])
GO

ALTER TABLE [maquinas] ADD FOREIGN KEY ([proveedor_id]) REFERENCES [proveedores] ([id])
GO

ALTER TABLE [maquinas] ADD FOREIGN KEY ([ubicacion_id]) REFERENCES [ubicaciones] ([id])
GO

ALTER TABLE [maquinas] ADD FOREIGN KEY ([estado_id]) REFERENCES [estados_maquina] ([id])
GO

ALTER TABLE [maquinas] ADD FOREIGN KEY ([usuario_asignado_id]) REFERENCES [usuarios] ([id])
GO

ALTER TABLE [ordenes_trabajo] ADD FOREIGN KEY ([maquina_id]) REFERENCES [maquinas] ([id])
GO

ALTER TABLE [ordenes_trabajo] ADD FOREIGN KEY ([tecnico_id]) REFERENCES [tecnicos] ([id])
GO

ALTER TABLE [ordenes_trabajo] ADD FOREIGN KEY ([usuario_creador_id]) REFERENCES [usuarios] ([id])
GO

ALTER TABLE [ordenes_trabajo] ADD FOREIGN KEY ([tipo_id]) REFERENCES [tipo] ([id])
GO

ALTER TABLE [ordenes_trabajo] ADD FOREIGN KEY ([prioridad_id]) REFERENCES [prioridad] ([id])
GO

ALTER TABLE [ordenes_trabajo] ADD FOREIGN KEY ([estado_id]) REFERENCES [estado] ([id])
GO

ALTER TABLE [tecnicos] ADD FOREIGN KEY ([usuario_id]) REFERENCES [usuarios] ([id])
GO

ALTER TABLE [usuarios] ADD FOREIGN KEY ([rol_id]) REFERENCES [roles_usuario] ([id])
GO

ALTER TABLE [mantenimientos_detalle_repuestos] ADD FOREIGN KEY ([mantenimiento_id]) REFERENCES [mantenimientos] ([id])
GO

ALTER TABLE [mantenimientos_detalle_repuestos] ADD FOREIGN KEY ([inventario_repuesto_id]) REFERENCES [inventario_repuestos] ([id])
GO

ALTER TABLE proveedores
DROP COLUMN tipo_servicio, calificacion;

INSERT INTO [roles_usuario] ([nombre])
VALUES
('admin'), 
('client'), 
('technician');
GO

INSERT INTO [usuarios] 
([primer_nombre], [segundo_nombre], [primer_apellido], [segundo_apellido], [email], [contraseña], [rol_id], [telefono], [activo], [ultimo_login], [fecha_creacion], [fecha_actualizacion])
VALUES
('Kevin', NULL, 'Admin', NULL, 'kereadmin@hotmail.es', 'pokemon1', 1, '0000-0001', 1, NULL, GETDATE(), NULL),
('Kevin', NULL, 'Cliente', NULL, 'kereclient@hotmail.es', 'pokemon1', 2, '0000-0002', 1, NULL, GETDATE(), NULL),
('Kevin', NULL, 'Tecnico', NULL, 'keretechnician@hotmail.es', 'pokemon1', 3, '0000-0003', 1, NULL, GETDATE(), NULL);
GO

INSERT INTO estados_maquina (nombre) VALUES
('Operativa'),
('En reparación'),
('Fuera de servicio'),
('En mantenimiento');

INSERT INTO ubicaciones (nombre, direccion, ciudad, telefono, activa) VALUES
('Sala Principal', 'Edificio Central', 'Tegucigalpa', '2222-0000', 1),
('Entrada Principal', 'Edificio Central', 'Tegucigalpa', '2222-0001', 1),
('Sala VIP', 'Edificio Central', 'Tegucigalpa', '2222-0002', 1);

INSERT INTO proveedores (nombre, contacto, telefono, email, direccion, rtn, activo) VALUES
('ProveedorTech', 'Laura Martínez', '9999-1111', 'proveedor@tech.com', 'Boulevard Centro', '0801199999', 1);

INSERT INTO maquinas
(numero_serie, modelo, fecha_adquisicion, estado_id, ubicacion_id, proveedor_id, usuario_asignado_id, notas)
VALUES
('A-123', 'Modelo Alpha 2024', '2024-05-10', 1, 1, 1, 2, 'Máquina operativa y en buen estado'),

('B-456', 'Modelo Beta Pro', '2024-03-22', 2, 3, 1, 2, 'Pantalla parpadea ocasionalmente'),

('C-789', 'Modelo Classic', '2023-11-05', 1, 2, 1, 2, 'Sin problemas reportados');

INSERT INTO estado (nombre) VALUES
('Pendiente'),
('En progreso'),
('Completada'),
('Cancelada');

INSERT INTO prioridad (nombre) VALUES
('Baja'),
('Media'),
('Alta');

INSERT INTO tipo (nombre) VALUES
('Eléctrico'),
('Electrónico'),
('Software'),
('Hardware'),
('Pantalla'),
('Monedero'),
('Impresora'),
('Otros');

INSERT INTO tecnicos (usuario_id, disponibilidad, vehiculo_asignado, herramienta_asignada, calificacion_promedio)
VALUES (3, 'disponible', 'Camioneta #1', 'Caja básica', 4.80);
