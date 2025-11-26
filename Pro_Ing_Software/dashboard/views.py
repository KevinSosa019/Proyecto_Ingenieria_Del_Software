from django.shortcuts import render, redirect
from datetime import datetime, timedelta
from accounts.database import get_connection
from django.db import connection

# Funciones de consulta para el cliente
from .queries import (
    get_client_info,
    get_client_machines,
    get_client_orders,
    get_completed_repairs,
    get_machine_stats
)

"""
===========================================================
                     UTILIDADES GENERALES
===========================================================
"""

def check_session(request):
    """Devuelve el rol si existe en sesión, si no None."""
    return request.session.get("role")


"""
===========================================================
                         PANEL CLIENTE
===========================================================
"""

def client_dashboard(request):
    """Dashboard principal del cliente."""
    if request.session.get("role") != 2:
        return redirect("/login/")


    user_id = request.session["user_id"]

    # Datos del cliente
    client = get_client_info(user_id)
    machines = get_client_machines(user_id)
    orders = get_client_orders(user_id)
    repairs = get_completed_repairs(user_id)
    stats = get_machine_stats(user_id)

    context = {
        "client": client,
        "machines": machines,

        # estadísticas de máquinas
        "fuera_servicio": stats["fuera_servicio"],
        "en_mantenimiento": stats["en_mantenimiento"],
        "en_reparacion": stats["en_reparacion"],
        "operativas": stats["operativa"],

        # estadísticas adicionales
        "orders_open": orders["open"],
        "orders_urgent": orders["urgent"],
        "repairs_done": repairs,

        # catálogos para modal
        "problem_types": get_problem_types(),
        "priorities": get_priorities(),
    }

    return render(request, "dashboard/client_dashboard.html", context)


def report_problem(request):
    """Cliente reporta un problema → crea orden de trabajo."""
    if request.method != "POST":
        return redirect("/dashboard/client/")

    user_id = request.session["user_id"]

    # Campos del form
    maquina_id = request.POST["maquina_id"]
    tipo_id = request.POST["tipo_id"]
    prioridad_id = request.POST["prioridad_id"]
    descripcion = request.POST["descripcion"]

    conn = get_connection()
    cur = conn.cursor()

    # Generar código OT-XXXX
    cur.execute("SELECT COUNT(*) FROM ordenes_trabajo")
    total = cur.fetchone()[0] + 1
    codigo = f"OT-{total:04d}"

    # Insertar orden
    cur.execute("""
        INSERT INTO ordenes_trabajo
        (codigo, maquina_id, tipo_id, prioridad_id, estado_id, descripcion, usuario_creador_id, fecha_creacion)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        codigo, maquina_id, tipo_id, prioridad_id,
        1,  # estado pendiente
        descripcion, user_id, datetime.now()
    ))
    
    # poner la máquina en estado "En Mantenimiento" (ID = 4, por ejemplo)
    cur.execute("""
        UPDATE maquinas
        SET estado_id = 4
        WHERE id = ?
    """, (maquina_id,))

    conn.commit()
    return redirect("/dashboard/client/")


def get_problem_types():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre FROM tipo")
    return [{"id": r[0], "name": r[1]} for r in cur.fetchall()]


def get_priorities():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre FROM prioridad")
    return [{"id": r[0], "nombre": r[1]} for r in cur.fetchall()]


def client_orders(request):
    """Lista de todas las órdenes creadas por el cliente."""
    user_id = request.session.get("user_id")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            ot.id, ot.codigo, ot.descripcion,
            ot.fecha_creacion, ot.fecha_inicio, ot.fecha_finalizacion,
            t.nombre, p.nombre, e.nombre,
            m.numero_serie, m.modelo
        FROM ordenes_trabajo ot
        JOIN maquinas m ON ot.maquina_id = m.id
        JOIN tipo t ON ot.tipo_id = t.id
        JOIN prioridad p ON ot.prioridad_id = p.id
        JOIN estado e ON ot.estado_id = e.id
        WHERE ot.usuario_creador_id = ?
        ORDER BY ot.fecha_creacion DESC
    """, (user_id,))

    rows = cur.fetchall()

    orders = [
        {
            "id": r[0], "codigo": r[1], "descripcion": r[2],
            "fecha": r[3], "inicio": r[4], "fin": r[5],
            "tipo": r[6], "prioridad": r[7], "estado": r[8],
            "serial": r[9], "modelo": r[10],
        } for r in rows
    ]

    return render(request, "dashboard/client_orders.html", {"orders": orders})


def client_order_detail(request, order_id):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("/login/")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            o.id,
            o.codigo,
            o.descripcion,
            o.fecha_creacion,
            o.fecha_asignacion,
            o.fecha_inicio,
            o.fecha_finalizacion,

            t.nombre AS tipo,
            p.nombre AS prioridad,
            e.nombre AS estado,

            m.numero_serie,
            m.modelo,

            u.primer_nombre + ' ' + u.primer_apellido AS cliente_nombre,
            u.telefono AS cliente_telefono,

            tec.primer_nombre + ' ' + tec.primer_apellido AS tecnico_nombre,
            tec.telefono AS tecnico_telefono
        FROM ordenes_trabajo o
        LEFT JOIN tipo t           ON o.tipo_id = t.id
        LEFT JOIN prioridad p      ON o.prioridad_id = p.id
        LEFT JOIN estado e         ON o.estado_id = e.id
        LEFT JOIN maquinas m       ON o.maquina_id = m.id
        LEFT JOIN usuarios u       ON o.usuario_creador_id = u.id
        LEFT JOIN usuarios tec     ON o.tecnico_id = tec.id
        WHERE o.id = ? AND o.usuario_creador_id = ?
    """, (order_id, user_id))

    row = cursor.fetchone()

    if not row:
        return redirect("/dashboard/client/orders/")

    order = {
        "id": row[0],
        "codigo": row[1],
        "descripcion": row[2],
        "fecha_creacion": row[3],
        "fecha_asignacion": row[4],
        "fecha_inicio": row[5],
        "fecha_finalizacion": row[6],
        "tipo": row[7],
        "prioridad": row[8],
        "estado": row[9],
        "serial": row[10],
        "modelo": row[11],
        "cliente_nombre": row[12],
        "cliente_telefono": row[13],
        "tecnico_nombre": row[14],
        "tecnico_telefono": row[15],
    }

    return render(request, "dashboard/client_order_detail.html", {"order": order})


"""
===========================================================
                         PANEL TÉCNICO
===========================================================
"""

def technician_dashboard(request):
    """Dashboard del técnico con métricas y órdenes asignadas o disponibles."""
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("/login/")

    conn = get_connection()
    cur = conn.cursor()

    # Obtener técnico real
    cur.execute("""
        SELECT t.id, u.primer_nombre, u.primer_apellido
        FROM tecnicos t
        JOIN usuarios u ON t.usuario_id = u.id
        WHERE t.usuario_id = ?
    """, (user_id,))
    row = cur.fetchone()
    if not row:
        return redirect("/login/")

    tecnico_id = row[0]
    tecnico_nombre = f"{row[1]} {row[2]}"

    # Órdenes asignadas o disponibles
    cur.execute("""
        SELECT 
            ot.id, ot.codigo, ot.descripcion,
            ot.fecha_asignacion, ot.fecha_inicio, ot.fecha_finalizacion,
            p.nombre, e.nombre, t.nombre,
            m.numero_serie, m.modelo,
            u.primer_nombre, u.primer_apellido, u.telefono,
            ot.tecnico_id
        FROM ordenes_trabajo ot
        LEFT JOIN prioridad p ON ot.prioridad_id = p.id
        LEFT JOIN estado e ON ot.estado_id = e.id
        LEFT JOIN tipo t ON ot.tipo_id = t.id
        LEFT JOIN maquinas m ON ot.maquina_id = m.id
        LEFT JOIN usuarios u ON ot.usuario_creador_id = u.id
        WHERE (ot.tecnico_id = ? OR ot.tecnico_id IS NULL)
        ORDER BY ot.fecha_asignacion DESC
    """, (tecnico_id,))

    rows = cur.fetchall()

    orders = []
    for r in rows:
        asignacion, inicio = r[3], r[4]

        # Tiempo desde asignación
        tiempo_desde = None
        if asignacion:
            diff = datetime.now() - asignacion
            if diff.days > 0:
                tiempo_desde = f"{diff.days} días"
            elif diff.seconds >= 3600:
                tiempo_desde = f"{diff.seconds//3600} horas"
            else:
                tiempo_desde = f"{diff.seconds//60} min"

        # Tiempo desde inicio
        tiempo_inicio = None
        if inicio:
            diff2 = datetime.now() - inicio
            if diff2.days > 0:
                tiempo_inicio = f"{diff2.days} días"
            elif diff2.seconds >= 3600:
                tiempo_inicio = f"{diff2.seconds//3600} horas"
            else:
                tiempo_inicio = f"{diff2.seconds//60} min"

        orders.append({
            "id": r[0], "codigo": r[1], "descripcion": r[2],
            "fecha_asignacion": r[3], "fecha_inicio": r[4], "fecha_finalizacion": r[5],
            "prioridad": r[6], "estado": r[7], "tipo": r[8],
            "serial": r[9], "modelo": r[10],
            "cliente_nombre": f"{r[11]} {r[12]}", "cliente_telefono": r[13],
            "tecnico_id": r[14],
            "tiempo_desde": tiempo_desde,
            "tiempo_desde_inicio": tiempo_inicio,
        })

    # Métricas
    asignadas = sum(1 for o in orders if o["tecnico_id"] == tecnico_id)
    completadas_hoy = sum(
        1 for o in orders
        if o["fecha_finalizacion"] and o["fecha_finalizacion"].date() == datetime.now().date()
    )
    urgentes = sum(1 for o in orders if o["prioridad"] and o["prioridad"].lower() == "alta")

    tiempos = []
    for o in orders:
        if o["fecha_inicio"] and o["fecha_finalizacion"]:
            diff = o["fecha_finalizacion"] - o["fecha_inicio"]
            tiempos.append(diff.total_seconds() / 3600)

    tiempo_promedio = f"{sum(tiempos)/len(tiempos):.1f}h" if tiempos else "0h"

    # --- FILTRO POR PRIORIDAD ---
    priority_filter = request.GET.get("priority", "").lower()
    
    filtered_orders = orders
    
    if priority_filter in ["alta", "media", "baja"]:
        filtered_orders = [o for o in orders if o["prioridad"].lower() == priority_filter]
    
    elif priority_filter == "completada":
        filtered_orders = [o for o in orders if o["estado"].lower() == "completada"]
    
    
    return render(request, "dashboard/technician_dashboard.html", {
        "orders": filtered_orders,
        "asignadas": asignadas,
        "completadas_hoy": completadas_hoy,
        "urgentes": urgentes,
        "tiempo_promedio": tiempo_promedio,
        "tecnico_nombre": tecnico_nombre,
        "tecnico_id": tecnico_id,
        "priority_filter": priority_filter,
    })
    


def technician_take_order(request, order_id):
    """Técnico toma una orden que no tiene técnico asignado."""
    if request.method != "POST":
        return redirect("/dashboard/technician/")

    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("/login/")

    conn = get_connection()
    cur = conn.cursor()

    # Obtener tecnico real
    cur.execute("SELECT id FROM tecnicos WHERE usuario_id = ?", (user_id,))
    t = cur.fetchone()
    if not t:
        return redirect("/dashboard/technician/")

    tecnico_id = t[0]

    # Verificar si ya tiene técnico
    cur.execute("SELECT tecnico_id FROM ordenes_trabajo WHERE id = ?", (order_id,))
    row = cur.fetchone()
    if row and row[0]:
        return redirect("/dashboard/technician/")

    now = datetime.now()
    cur.execute("""
        UPDATE ordenes_trabajo
        SET tecnico_id = ?, estado_id = 2,
            fecha_asignacion = COALESCE(fecha_asignacion, ?),
            fecha_inicio = COALESCE(fecha_inicio, ?)
        WHERE id = ?
    """, (tecnico_id, now, now, order_id))

    # cambiar máquina a "En reparación" (ID = 2)
    cur.execute("""
        UPDATE maquinas
        SET estado_id = 2
        WHERE id = (
            SELECT maquina_id FROM ordenes_trabajo WHERE id = ?
        )
    """, (order_id,))

    conn.commit()
    return redirect("/dashboard/technician/")


def technician_start_work(request, order_id):
    """Marca inicio de trabajo explícitamente."""
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    with connection.cursor() as cur:
        cur.execute("SELECT id FROM tecnicos WHERE usuario_id = %s", [user_id])
        t = cur.fetchone()

    if not t:
        return redirect("dashboard:technician_dashboard")

    tecnico_id = t[0]

    with connection.cursor() as cur:
        cur.execute("""
            UPDATE ordenes_trabajo
            SET fecha_inicio = GETDATE(), estado_id = 2
            WHERE id = %s AND tecnico_id = %s
        """, [order_id, tecnico_id])

    return redirect("dashboard:technician_dashboard")


def technician_update_progress(request, order_id):
    """Actualiza campo de descripción como progreso."""
    if request.method != "POST":
        return redirect("/dashboard/technician/")

    progreso = request.POST["progreso"]

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE ordenes_trabajo
        SET descripcion = ?
        WHERE id = ?
    """, (progreso, order_id))

    conn.commit()
    return redirect("/dashboard/technician/")


def technician_complete(request, order_id):
    """Marca una orden como completada."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE ordenes_trabajo
        SET estado_id = 3, fecha_finalizacion = ?
        WHERE id = ?
    """, (datetime.now(), order_id))

    # cambiar máquina a estado "Operativa" (ID = 1)
    cur.execute("""
        UPDATE maquinas
        SET estado_id = 1
        WHERE id = (
            SELECT maquina_id FROM ordenes_trabajo WHERE id = ?
        )
    """, (order_id,))


    conn.commit()
    return redirect("/dashboard/technician/")


def technician_order_detail(request, order_id):
    """Detalle completo para el técnico."""
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    with connection.cursor() as cur:
        cur.execute("""
            SELECT 
                o.id, o.codigo, o.descripcion,
                o.fecha_creacion, o.fecha_asignacion, o.fecha_inicio, o.fecha_finalizacion,
                m.id, m.numero_serie, m.modelo,
                u.id, u.primer_nombre + ' ' + u.primer_apellido, u.telefono,
                pr.nombre, e.nombre, t.nombre,
                tec.id,
                (SELECT primer_nombre + ' ' + primer_apellido FROM usuarios WHERE id = tec.usuario_id)
            FROM ordenes_trabajo o
            INNER JOIN maquinas m ON o.maquina_id = m.id
            INNER JOIN usuarios u ON o.usuario_creador_id = u.id
            INNER JOIN prioridad pr ON o.prioridad_id = pr.id
            INNER JOIN estado e ON o.estado_id = e.id
            INNER JOIN tipo t ON o.tipo_id = t.id
            LEFT JOIN tecnicos tec ON o.tecnico_id = tec.id
            WHERE o.id = %s
        """, [order_id])

        row = cur.fetchone()

    if not row:
        return redirect("dashboard:technician_dashboard")

    order = {
        "id": row[0], "codigo": row[1], "descripcion": row[2],
        "fecha_creacion": row[3], "fecha_asignacion": row[4],
        "fecha_inicio": row[5], "fecha_finalizacion": row[6],
        "maquina_id": row[7], "serial": row[8], "modelo": row[9],
        "cliente_id": row[10], "cliente_nombre": row[11],
        "cliente_telefono": row[12],
        "prioridad": row[13], "estado": row[14], "tipo": row[15],
        "tecnico_id": row[16], "tecnico_nombre": row[17],
    }

    return render(request, "dashboard/technician_order_detail.html", {"order": order})


"""
===========================================================
                     PANEL ADMIN (placeholder)
===========================================================
"""

def admin_dashboard(request):
    """WIP admin dashboard."""
    if check_session(request) != 1:
        return redirect("/login/")
    return render(request, "dashboard/admin_dashboard.html")



def client_toggle_machine_state(request, machine_id):
    """El cliente puede poner su máquina Operativa o Fuera de Servicio manualmente."""
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("/login/")

    conn = get_connection()
    cur = conn.cursor()

    # Verifica que la máquina pertenece al cliente
    cur.execute("""
        SELECT estado_id FROM maquinas
        WHERE id = ? AND usuario_asignado_id = ?
    """, (machine_id, user_id))

    row = cur.fetchone()
    if not row:
        return redirect("/dashboard/client/")

    estado_actual = row[0]

    # 1 = Operativa
    # 3 = Fuera de servicio
    nuevo_estado = 3 if estado_actual == 1 else 1

    cur.execute("""
        UPDATE maquinas
        SET estado_id = ?
        WHERE id = ?
    """, (nuevo_estado, machine_id))

    conn.commit()

    return redirect("/dashboard/client/")
