from django.urls import path
from .views import home, products, register, login_view, logout_view, admin_inicio, tecnico_inicio, usuario_inicio

urlpatterns = [
    path('', home, name='home'),
    path('products/', products, name='products'),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),


    path('admin_inicio/', admin_inicio, name='admin_inicio'),
    path('tecnico_inicio/', tecnico_inicio, name='tecnico_inicio'),
    path('usuario_inicio/', usuario_inicio, name='usuario_inicio'),
]
