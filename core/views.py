from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from .models import Usuario, Maquina, Proveedor
from .forms import UsuarioForm

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
    data = {'form': UsuarioForm()}

    if request.method == 'POST':
        user_form = UsuarioForm(data=request.POST)
        if user_form.is_valid():
            user = user_form.save(commit=False)
            # Convertir email a minúsculas
            user.email = user.email.lower()
            # Establecer fechas
            now = timezone.now()
            user.fecha_creacion = now
            user.fecha_actualizacion = now
            user.activo = True
            # Guardamos la contraseña directamente SIN encriptar
            user.save()
            messages.success(request, 'Usuario registrado correctamente.')
            return redirect('login')
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

