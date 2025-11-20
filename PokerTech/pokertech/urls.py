from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [

    # Rutas del sistema de login / logout
    path('accounts/', include('accounts.urls')),

    # Rutas del dashboard (cliente, técnico, admin)
    path('dashboard/', include('dashboard.urls')),

    # Ruta raíz → redirige al login
    path('', lambda request: redirect('/accounts/login/')),
]
