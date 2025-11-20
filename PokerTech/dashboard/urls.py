from django.urls import path

# Importamos TODAS tus vistas de manera ordenada
from .views import (
    # Cliente
    client_dashboard,
    client_orders,
    client_order_detail,
    report_problem,
    
    # Técnico
    technician_dashboard,
    technician_start_work,
    technician_take_order,
    technician_update_progress,
    technician_complete,
    technician_order_detail,

    # Admin (luego lo completarás)
    admin_dashboard,
)

# Namespace utilizado por {% url 'dashboard:...' %}
app_name = "dashboard"

urlpatterns = [

    # --------------------------------------------------------
    # CLIENTE
    # --------------------------------------------------------
    path("client/", client_dashboard, name="client_dashboard"),
    path("client/orders/", client_orders, name="client_orders"),
    path("client/order/<int:order_id>/", client_order_detail, name="client_order_detail"),

    # Cliente reporta problemas
    path("report/", report_problem, name="report_problem"),

    # --------------------------------------------------------
    # TÉCNICO
    # --------------------------------------------------------
    path("technician/", technician_dashboard, name="technician_dashboard"),
    path("technician/start/<int:order_id>/", technician_start_work, name="technician_start"),
    path("technician/take/<int:order_id>/", technician_take_order, name="technician_take"),
    path("technician/update/<int:order_id>/", technician_update_progress, name="technician_update_progress"),
    path("technician/complete/<int:order_id>/", technician_complete, name="technician_complete"),
    path("technician/order/<int:order_id>/", technician_order_detail, name="technician_order_detail"),

    # --------------------------------------------------------
    # ADMIN
    # --------------------------------------------------------
    path("admin/", admin_dashboard, name="admin_dashboard"),
]
