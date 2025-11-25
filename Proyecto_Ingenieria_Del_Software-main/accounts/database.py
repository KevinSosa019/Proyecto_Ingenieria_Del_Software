import pyodbc

# ------------------------------------------------------------
# get_connection()
#
# Retorna una conexión directa a SQL Server usando pyodbc.
#
# IMPORTANTE:
# - No maneja pooling de conexiones (cada llamada abre una nueva).
# - Las credenciales están en texto plano (backend local).
# - La conexión se cierra automáticamente cuando Django termina
#   de usar el cursor, pero si querés cerrar manualmente,
#   podés usar conn.close().
#
# NOTA:
#   Si en el futuro querés migrar a variables de entorno (.env)
#   o agregar pooling, este es el archivo donde se haría.
# ------------------------------------------------------------
def get_connection():
    return pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=DESKTOP-PU1H6AA;'
        'DATABASE=MaquinasDePoker;'
        'UID=KevinS;'
        'PWD=Ichigo19.'
    )
