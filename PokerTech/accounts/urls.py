from django.urls import path
from .views import login_view, logout_view

# ------------------------------------------------------------
# URLS DEL MÓDULO "accounts"
#
# Este archivo solo controla las rutas relacionadas con:
#   - Login
#   - Logout
#
# NOTA IMPORTANTE:
#   Estas rutas NO usan namespace porque se incluyen directamente
#   en pokertech/urls.py como:
#
#       path("accounts/", include("accounts.urls"))
#
#   Por eso en las plantillas las URLs se llaman así:
#
#       {% url 'login' %}
#       {% url 'logout' %}
# ------------------------------------------------------------

urlpatterns = [
    # Página de inicio de sesión
    path("login/", login_view, name="login"),

    # Cerrar sesión (elimina la sesión actual y redirige al login)
    path("logout/", logout_view, name="logout"),
]
