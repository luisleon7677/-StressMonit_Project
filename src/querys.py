from src.conexion import get_connection, return_connection
from werkzeug.security import generate_password_hash, check_password_hash

def listarQuerys(query, params=None):
    connection = get_connection()
    if not connection:
        print("Error: No se pudo obtener conexión del pool")
        return None

    try:
        with connection:
            with connection.cursor() as cursor:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                if query.strip().upper().startswith('SELECT'):
                    return cursor.fetchall()
                else:
                    # El 'with connection' hace commit automático al salir
                    return True
                    
    except Exception as e:
        print(f"Error en la consulta: {str(e)}")
        # El 'with connection' hará rollback si hay excepción
        return None
    finally:
        if connection:
            return_connection(connection)

def create_user(username, password):
    hashed_pw = generate_password_hash(password)
    query = "INSERT INTO usuarios (username, password) VALUES (%s, %s)"
    return listarQuerys(query, (username, hashed_pw))

def verify_password(username, password):
    query = "SELECT password FROM usuarios WHERE username = %s"
    result = listarQuerys(query, (username,))
    if result and len(result) > 0:
        return check_password_hash(result[0][0], password)
    return False

def crear_actividad(nombre, descripcion, grado_dif, id_administrador):
    """Crea una nueva actividad con el administrador asignado"""
    query = """
        INSERT INTO actividades (nombre, descripcion, grado_dif, id_administrador)
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """
    params = (nombre, descripcion, float(grado_dif), int(id_administrador))
    return listarQuerys(query, params)