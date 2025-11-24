from accounts.database import get_connection

# ------------------------------------------------------------
# Obtiene datos básicos del cliente (nombre, email, teléfono)
# ------------------------------------------------------------
def get_client_info(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT primer_nombre, primer_apellido, email, telefono
        FROM usuarios
        WHERE id = ?
    """, (user_id,))

    row = cur.fetchone()
    if not row:
        return None

    return {
        "first_name": row[0],
        "last_name": row[1],
        "email": row[2],
        "phone": row[3],
    }

# ------------------------------------------------------------
# Devuelve todas las máquinas asignadas a un cliente.
#
# Une:
#  - maquinas
#  - ubicaciones
#  - estados_maquina
# ------------------------------------------------------------
def get_client_machines(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT m.id, m.numero_serie, m.modelo,
               u.nombre AS ubicacion,
               e.nombre AS estado
        FROM maquinas m
        LEFT JOIN ubicaciones u ON m.ubicacion_id = u.id
        LEFT JOIN estados_maquina e ON m.estado_id = e.id
        WHERE m.usuario_asignado_id = ?
    """, (user_id,))

    machines = []
    for row in cur.fetchall():
        machines.append({
            "id": row[0],
            "serial": row[1],
            "model": row[2],
            "location": row[3],
            "state": row[4],
        })

    return machines

# ------------------------------------------------------------
# Obtiene estadísticas de órdenes del cliente:
#  - Cantidad de órdenes abiertas
#  - Cantidad de órdenes urgentes
# ------------------------------------------------------------
def get_client_orders(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT o.id, o.estado_id, o.prioridad_id
        FROM ordenes_trabajo o
        INNER JOIN maquinas m ON o.maquina_id = m.id
        WHERE m.usuario_asignado_id = ?
    """, (user_id,))

    orders = cur.fetchall()

    # Estado 3 = completada (esto viene de la BD)
    open_orders = len([o for o in orders if o[1] != 3])

    # Prioridad 1 = alta
    urgent_orders = len([o for o in orders if o[2] == 1])

    return {
        "open": open_orders,
        "urgent": urgent_orders
    }

# ------------------------------------------------------------
# Total de reparaciones completadas de máquinas del cliente.
#
# Usa:
#  mantenimientos → ordenes_trabajo → maquinas
# ------------------------------------------------------------
def get_completed_repairs(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(*)
        FROM mantenimientos m
        INNER JOIN ordenes_trabajo o ON m.orden_trabajo_id = o.id
        INNER JOIN maquinas maq ON o.maquina_id = maq.id
        WHERE maq.usuario_asignado_id = ?
    """, (user_id,))

    return cur.fetchone()[0]

# ------------------------------------------------------------
# Estadísticas de máquinas por estado (4 categorías):
#   - Operativa
#   - En mantenimiento
#   - Fuera de servicio
#   - En reparación
#
# Se basa en coincidencia parcial en el nombre del estado.
# ------------------------------------------------------------
def get_machine_stats(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT e.nombre, COUNT(*)
        FROM maquinas m
        INNER JOIN estados_maquina e ON m.estado_id = e.id
        WHERE m.usuario_asignado_id = ?
        GROUP BY e.nombre
    """, (user_id,))

    stats = {
        "operativa": 0,
        "en_mantenimiento": 0,
        "fuera_servicio": 0,
        "en_reparacion": 0,
    }

    for row in cur.fetchall():
        state = row[0].lower()
        count = row[1]

        # Identificación flexible de nombres según la BD
        if "operativa" in state:
            stats["operativa"] = count
        elif "manten" in state:
            stats["en_mantenimiento"] = count
        elif "fuera" in state:
            stats["fuera_servicio"] = count
        elif "repar" in state:
            stats["en_reparacion"] = count

    return stats
