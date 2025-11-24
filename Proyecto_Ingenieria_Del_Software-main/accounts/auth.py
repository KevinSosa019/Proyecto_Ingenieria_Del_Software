from .database import get_connection
from datetime import datetime

# ------------------------------------------------------------
# authenticate_user(email, password)
#
# Función encargada de validar las credenciales del usuario.
# Usa conexión directa a SQL Server (sin ORM de Django).
#
# RETORNA:
#   - dict con { "id": X, "role": Y } → si la autenticación es correcta
#   - None → si falla por usuario inexistente, inactivo o contraseña incorrecta
#
# NOTA:
#   Esta función NO hace hashing de contraseñas. Si en el futuro
#   querés implementar seguridad real, habría que agregar hashing
#   (bcrypt, argon2, etc.). Por ahora funciona con la BD actual.
# ------------------------------------------------------------
def authenticate_user(email, password):

    # Conectar a SQL Server usando pyodbc
    conn = get_connection()
    cursor = conn.cursor()

    # ------------------------------------------------------------
    # 1. Buscar usuario por email
    # ------------------------------------------------------------
    cursor.execute("""
        SELECT id, contraseña, rol_id, activo
        FROM usuarios
        WHERE email = ?
    """, (email,))

    row = cursor.fetchone()

    # Usuario no encontrado en la BD
    if not row:
        return None

    user_id, db_password, role_id, active = row

    # Usuario desactivado (campo 'activo = 0')
    if not active:
        return None

    # Contraseña incorrecta
    # Nota: Se compara directo porque la BD no usa hashing.
    if db_password != password:
        return None

    # ------------------------------------------------------------
    # 2. Actualizar "ultimo_login"
    # ------------------------------------------------------------
    cursor.execute("""
        UPDATE usuarios 
        SET ultimo_login = ? 
        WHERE id = ?
    """, (datetime.now(), user_id))

    conn.commit()

    # ------------------------------------------------------------
    # 3. Devolver datos esenciales del usuario
    # ------------------------------------------------------------
    return {
        "id": user_id,
        "role": role_id
    }
