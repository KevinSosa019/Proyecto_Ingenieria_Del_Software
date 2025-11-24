from django.urls import path, include
from .views import home, products, register, login_view, logout_view, admin_inicio, tecnico_inicio, usuario_inicio, maquinas_inicio
from .views import usuarios_list, usuario_create, usuario_update, usuario_delete
from .views import maquinas_list, maquina_create, maquina_update, maquina_delete
from .views import ordenes_trabajo_list, orden_trabajo_create, orden_trabajo_update, orden_trabajo_delete, ordenes_trabajo_inicio
from .views import proveedores_inicio, proveedor_create, proveedor_delete, proveedor_update
urlpatterns = [
    path('', home, name='home'),
    path('products/', products, name='products'),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    path('dashboard/', include('dashboard.urls')),
    path('accounts/', include('accounts.urls')),

    path('admin_inicio/', admin_inicio, name='admin_inicio'),
    path('tecnico_inicio/', tecnico_inicio, name='tecnico_inicio'),
    path('usuario_inicio/', usuario_inicio, name='usuario_inicio'),
    
    
    path('usuarios/', usuarios_list, name='usuarios_list'),
    path('usuarios/crear/', usuario_create, name='usuario_create'),
    path('usuarios/<int:id>/editar/', usuario_update, name='usuario_update'),
    path('usuarios/<int:id>/eliminar/', usuario_delete, name='usuario_delete'),
    
    path('maquinas/', maquinas_inicio, name='maquinas_inicio'),
    path('maquinas/', maquinas_list, name='maquinas_list'),
    path('maquinas/nueva/', maquina_create, name='maquina_create'),
    path('maquinas/editar/<int:id>/', maquina_update, name='maquina_update'),
    path('maquinas/eliminar/<int:id>/', maquina_delete, name='maquina_delete'),
    
    
    path('ordenes_trabajo/', ordenes_trabajo_inicio, name='ordenes_trabajo_inicio'),
    path('ordenes_trabajo/listar/', ordenes_trabajo_list, name='ordenes_trabajo_list'),
    path('ordenes_trabajo/crear/', orden_trabajo_create, name='orden_trabajo_create'),
    path('ordenes_trabajo/editar/<int:id>/', orden_trabajo_update, name='orden_trabajo_update'),
    path('ordenes_trabajo/eliminar/<int:id>/', orden_trabajo_delete, name='orden_trabajo_delete'),


    path('proveedores/', proveedores_inicio, name='proveedores_inicio'),
    path('proveedores/crear/', proveedor_create, name='proveedor_create'),
    path('proveedores/editar/<int:id>/', proveedor_update, name='proveedor_update'),
    path('proveedores/eliminar/<int:id>/', proveedor_delete, name='proveedor_delete'),
]
