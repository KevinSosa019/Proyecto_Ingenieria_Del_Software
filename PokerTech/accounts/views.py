from django.shortcuts import render, redirect
from .auth import authenticate_user

# ------------------------------------------------------------
# login_view(request)
#
# Controla:
#   - Mostrar el formulario de login (GET)
#   - Procesar credenciales (POST)
#   - Crear sesión si las credenciales son correctas
#   - Redirigir según el rol del usuario
#
# ROLES:
#   1 = Administrador
#   2 = Cliente
#   3 = Técnico
#
# NOTA IMPORTANTE:
#   Esta vista NO usa el sistema de auth de Django, porque
#   estamos autenticando contra tu propia tabla "usuarios".
# ------------------------------------------------------------
def login_view(request):

    # Si el usuario envía el formulario
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Autenticar contra la BD real (SQL Server)
        user = authenticate_user(email, password)

        # Credenciales incorrectas
        if not user:
            return render(request, "accounts/login.html", {
                "error": "Credenciales incorrectas."
            })

        # --------------------------------------------------------
        # Crear sesión manualmente
        # --------------------------------------------------------
        request.session["user_id"] = user["id"]     # ID en tu BD
        request.session["role"] = user["role"]      # Rol (1, 2 o 3)

        # --------------------------------------------------------
        # Redirección según rol
        # --------------------------------------------------------
        if user["role"] == 1:
            # Administrador
            return redirect("/dashboard/admin/")

        elif user["role"] == 2:
            # Cliente
            return redirect("/dashboard/client/")

        elif user["role"] == 3:
            # Técnico
            return redirect("/dashboard/technician/")

    # Si es GET, solo mostrar el formulario
    return render(request, "accounts/login.html")


# ------------------------------------------------------------
# logout_view(request)
#
# Elimina toda la información almacenada en sesión:
#   - user_id
#   - role
#   - cualquier otra variable futura
#
# Luego redirige al inicio de sesión.
# ------------------------------------------------------------
def logout_view(request):
    request.session.flush()  # elimina la sesión completa
    return redirect("/accounts/login/")
