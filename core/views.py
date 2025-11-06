from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import Usuario, Maquina, Proveedor, OrdenTrabajo, Mantenimiento, MantenimientoDetalleRepuesto, ResultadoMantenimiento, Tecnico, InventarioRepuesto
from .forms import UsuarioForm, MaquinaForm, OrdenTrabajoForm
from django.db import transaction, IntegrityError


# ==========================
# Vista de inicio (home)
# ==========================

# views.py

def home(request):
    user = None
    if 'user_id' in request.session:
        try:
            user = Usuario.objects.get(id=request.session['user_id'])
        except Usuario.DoesNotExist:
            request.session.flush()  # Limpiar sesión si no existe
    return render(request, 'core/home.html', {'user': user})

# ==========================
# Vista de productos (login requerido)
# ==========================
def products(request):
    user = None
    if 'user_id' in request.session:
        try:
            user = Usuario.objects.get(id=request.session['user_id'])
        except Usuario.DoesNotExist:
            request.session.flush()
            messages.error(request, 'Debes iniciar sesión para ver esta página.')
            return redirect('login')
    else:
        messages.error(request, 'Debes iniciar sesión para ver esta página.')
        return redirect('login')

    return render(request, 'core/products.html', {'user': user})

# ==========================
# Registro de usuario
# ==========================
def register(request):
    usuarios = Usuario.objects.all().order_by('primer_nombre')  # Lista de usuarios
    data = {'form': UsuarioForm(), 'usuarios': usuarios}

    if request.method == 'POST':
        user_form = UsuarioForm(request.POST)
        if user_form.is_valid():
            user = user_form.save(commit=False)
            # Convertir email a minúsculas
            user.email = user.email.lower()
            # Establecer fechas
            now = timezone.now()
            user.fecha_creacion = now
            user.fecha_actualizacion = now
            user.activo = True
            # Guardar la contraseña
            if user_form.cleaned_data.get('contraseña'):
                user.contraseña = user_form.cleaned_data['contraseña']
            user.save()
            messages.success(request, 'Usuario registrado correctamente.')
            return redirect('register')  # Recarga la misma página
        else:
            data['form'] = user_form

    return render(request, 'registration/register.html', data)
# ==========================
# Login de usuario
# ==========================


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')

        if not email or not password:
            messages.error(request, 'Debe ingresar correo y contraseña.')
            return render(request, 'registration/login.html')

        try:
            # Depuración
            print(f"Intentando login con email: {email}")
            user = Usuario.objects.get(email__iexact=email)
            print(f"Usuario encontrado: {user.primer_nombre} {user.primer_apellido}")

            if user.contraseña == password:
                # Guardar sesión
                request.session['user_id'] = user.id
                request.session.save()

                # Actualizar último login
                user.ultimo_login = timezone.now()
                user.save()

                messages.success(request, f'Bienvenido {user.primer_nombre}!')

                # 🔹 Redirección según rol
                if user.rol:
                    rol_nombre = user.rol.nombre.lower().strip()
                    print(f"Rol detectado: {rol_nombre}")

                    if rol_nombre == 'administrador':
                        print("Redirigiendo al panel del administrador")
                        return redirect('admin_inicio')

                    elif rol_nombre in ['técnico', 'tecnico']:
                        print("Redirigiendo al panel del técnico")
                        return redirect('tecnico_inicio')

                    elif rol_nombre == 'usuario':
                        print("Redirigiendo al panel del usuario")
                        return redirect('usuario_inicio')

                    else:
                        print("Rol desconocido, redirigiendo a home")
                        return redirect('home')

                else:
                    print("Usuario sin rol asignado, redirigiendo a home")
                    return redirect('home')

            else:
                print("Contraseña incorrecta")
                messages.error(request, 'Contraseña incorrecta.')

        except Usuario.DoesNotExist:
            print(f"No se encontró usuario con email: {email}")
            messages.error(request, 'No existe una cuenta con ese correo electrónico.')

    return render(request, 'registration/login.html')

# ==========================
# Logout
# ==========================
def logout_view(request):
    request.session.flush()
    messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('login')

def admin_inicio(request):
    # --- Usuarios ---
    usuarios = Usuario.objects.all()
    usuarios_activos = usuarios.filter(activo=True).count()
    total_usuarios = usuarios.count()

    # --- Máquinas ---
    maquinas = Maquina.objects.select_related('estado').all()
    total_maquinas = maquinas.count()
    maquinas_operativas = maquinas.filter(estado__nombre='Operativa').count()
    porcentaje_operativas = round((maquinas_operativas / total_maquinas) * 100, 2) if total_maquinas else 0

    # --- Proveedores ---
    proveedores = Proveedor.objects.filter(activo=True)
    total_proveedores = proveedores.count()

    # --- Alertas simuladas (puedes luego conectar con una tabla real si la agregas) ---
    alertas = [
        {"descripcion": "Temperatura alta en máquina MX-2025", "tiempo": "Hace 2 días"},
        {"descripcion": "Error de conexión con servidor", "tiempo": "Hace 1 día"},
    ]
    alertas_activas = len(alertas)

    context = {
        'usuarios': usuarios,
        'usuarios_activos': usuarios_activos,
        'total_usuarios': total_usuarios,
        'maquinas': maquinas,
        'maquinas_operativas': maquinas_operativas,
        'total_maquinas': total_maquinas,
        'porcentaje_operativas': porcentaje_operativas,
        'proveedores': proveedores,
        'alertas': alertas,
        'alertas_activas': alertas_activas,
    }

    return render(request, 'admin_maquinas/admin_inicio.html', context)

def tecnico_inicio(request):
    return render(request, 'tecnico/tecnico_inicio.html')

def usuario_inicio(request):
    return render(request, 'usuario/usuario_inicio.html')


# Listar usuarios
def usuarios_list(request):
    usuarios = Usuario.objects.all()
    return render(request, 'admin_usuarios/usuarios_list.html', {'usuarios': usuarios})

# Crear usuario
def usuario_create(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = user.email.lower()
            now = timezone.now()
            user.fecha_creacion = now
            user.fecha_actualizacion = now
            user.activo = True
            if form.cleaned_data.get('contraseña'):
                user.contraseña = form.cleaned_data['contraseña']
            user.save()
            messages.success(request, "Usuario creado correctamente")
            return redirect('usuarios_list')
    else:
        form = UsuarioForm()
    return render(request, 'admin_usuarios/usuario_form.html', {'form': form})

# Editar usuario
def usuario_update(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = user.email.lower()
            user.fecha_actualizacion = timezone.now()
            if form.cleaned_data.get('contraseña'):
                user.contraseña = form.cleaned_data['contraseña']
            user.save()
            messages.success(request, "Usuario actualizado correctamente")
            return redirect('register')
    else:
        form = UsuarioForm(instance=usuario)
    return render(request, 'admin_maquinas/editar_admin.html', {'form': form})

# Eliminar usuario

def usuario_delete(request, id):
    usuario = get_object_or_404(Usuario, id=id)
    
    if request.method == 'POST':
        try:
            usuario.delete()
            messages.success(request, 'Usuario eliminado correctamente.')
        except IntegrityError:
            # Si el usuario tiene registros relacionados en otras tablas (como ordenes_trabajo)
            messages.error(request, 'No se puede eliminar este usuario porque tiene registros asociados (por ejemplo: órdenes de trabajo).')
        return redirect('register')

    return redirect('register')

# ==========================
# Maquinas
# ==========================
def maquinas_inicio(request):
    maquinas = Maquina.objects.select_related('estado', 'proveedor', 'ubicacion', 'usuario_asignado')
    if request.method == 'POST':
        form = MaquinaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Máquina creada correctamente.")
            return redirect('maquinas_inicio')
    else:
        form = MaquinaForm()
    return render(request, 'admin_maquinas/maquinas_inicio.html', {'form': form, 'maquinas': maquinas})

def maquinas_list(request):
    maquinas = Maquina.objects.select_related('estado', 'proveedor', 'ubicacion', 'usuario_asignado')
    return render(request, 'admin_maquinas/maquinas_list.html', {'maquinas': maquinas})


def maquina_create(request):
    if request.method == 'POST':
        form = MaquinaForm(request.POST)
        if form.is_valid():
            maquina = form.save(commit=False)
            maquina.fecha_adquisicion = form.cleaned_data.get('fecha_adquisicion')
            maquina.save()
            messages.success(request, "Máquina creada correctamente")
            return redirect('maquinas_list')
    else:
        form = MaquinaForm()
    return render(request, 'admin_maquinas/maquina_form.html', {'form': form})


def maquina_update(request, id):
    maquina = get_object_or_404(Maquina, id=id)
    if request.method == 'POST':
        form = MaquinaForm(request.POST, instance=maquina)
        if form.is_valid():
            form.save()
            messages.success(request, "Máquina actualizada correctamente.")
            return redirect('maquinas_inicio')
    else:
        form = MaquinaForm(instance=maquina)
    return render(request, 'admin_maquinas/editar_maquinas.html', {'form': form})


def maquina_delete(request, id):
    maquina = get_object_or_404(Maquina, id=id)
    if request.method == 'POST':
        maquina.delete()
        messages.success(request, 'Máquina eliminada correctamente.')
        return redirect('maquinas_list')

    return redirect('maquinas_list')



# ==========================
# Ordenes de Trabajo
# ==========================

def ordenes_trabajo_inicio(request):
    ordenes = OrdenTrabajo.objects.all()
    if request.method == 'POST':
        form = OrdenTrabajoForm(request.POST)
        if form.is_valid():
            orden = form.save(commit=False)
            if not orden.fecha_creacion:
                orden.fecha_creacion = timezone.now()
            orden.save()
            messages.success(request, 'Orden creada correctamente.')
            return redirect('ordenes_trabajo_inicio')
    else:
        form = OrdenTrabajoForm()
    return render(request, 'admin_maquinas/ordenes_trabajo_inicio.html', {'ordenes': ordenes, 'form': form})



# Listar órdenes de trabajo
def ordenes_trabajo_list(request):
    ordenes = OrdenTrabajo.objects.all()
    return render(request, 'admin_ordenes/ordenes_list.html', {'ordenes': ordenes})

# Crear orden de trabajo
def orden_trabajo_create(request):
    if request.method == 'POST':
        form = OrdenTrabajoForm(request.POST)
        if form.is_valid():
            orden = form.save(commit=False)
            if not orden.fecha_creacion:
                orden.fecha_creacion = timezone.now()
            orden.save()
            messages.success(request, 'Orden de trabajo creada correctamente.')
            return redirect('ordenes_trabajo_list')
    else:
        form = OrdenTrabajoForm()
    return render(request, 'admin_ordenes/orden_trabajo_form.html', {'form': form})

# Editar orden de trabajo
def orden_trabajo_update(request, id):
    orden = get_object_or_404(OrdenTrabajo, id=id)
    if request.method == 'POST':
        form = OrdenTrabajoForm(request.POST, instance=orden)
        if form.is_valid():
            form.save()
            messages.success(request, 'Orden de trabajo actualizada correctamente.')
            return redirect('ordenes_trabajo_list')
    else:
        form = OrdenTrabajoForm(instance=orden)
    return render(request, 'admin_ordenes/editar_orden_trabajo.html', {'form': form})

# Eliminar orden de trabajo

# Eliminar orden de trabajo
def orden_trabajo_delete(request, id):
    orden = get_object_or_404(OrdenTrabajo, id=id)
    if request.method == 'POST':
        try:
            # Buscar todos los mantenimientos de la orden
            mantenimientos = Mantenimiento.objects.filter(orden_trabajo=orden)

            for m in mantenimientos:
                # Eliminar los detalles del mantenimiento asociados
                MantenimientoDetalleRepuesto.objects.filter(mantenimiento=m).delete()
                # Eliminar el mantenimiento
                m.delete()

            # Finalmente eliminar la orden
            orden.delete()
            messages.success(request, 'Orden de trabajo eliminada correctamente.')
        except Exception as e:
            print("Error al eliminar:", e)
            messages.error(request, f'No se pudo eliminar la orden: {str(e)}')

        return redirect('ordenes_trabajo_inicio')

    # Si entra por GET, mostrar la página de inicio de órdenes
    ordenes = OrdenTrabajo.objects.all()
    return render(request, 'admin_maquinas/ordenes_trabajo_inicio.html', {'ordenes': ordenes})

