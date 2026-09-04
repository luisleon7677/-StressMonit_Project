from src.conexion import get_connection, return_connection
from werkzeug.security import generate_password_hash, check_password_hash
from psycopg2 import OperationalError, InterfaceError
import time


def _is_connection_error(error):
    message = str(error).lower()
    return isinstance(error, (OperationalError, InterfaceError)) or (
        "server closed the connection" in message
        or "connection already closed" in message
        or "terminating connection" in message
    )


def eliminarRecurso(id, id_admin):
    conexion = get_connection()
    if not conexion:
        return None
    close_conn = False
    try:
        cursor = conexion.cursor()
        query = """
        delete from recursos where id = %s AND id_administrador = %s;
        """
        cursor.execute(query, (id, id_admin,))
        conexion.commit()
        cursor.close()
        print("recurso eliminado")
        return "Recurso elimindo", 200
    except Exception as e:
        print(f"Error al eliminar registro: {e}")
        close_conn = _is_connection_error(e)
        try:
            conexion.rollback()
        except Exception:
            pass
        return None
    finally:
        return_connection(conexion, close=close_conn)


def insertarRecursos(titulo, autor, contenido, id_admin):
    conexion = get_connection()
    if not conexion:
        return None
    close_conn = False
    try:
        cursor = conexion.cursor()
        query = """
        insert into recursos (titulo,autor,contenido,id_administrador) values(%s,%s,%s,%s);
        """
        cursor.execute(query, (titulo, autor, contenido, id_admin))
        conexion.commit()
        cursor.close()
        print("recurso insertado")
        return "Recurso insertado", 200
    except Exception as e:
        print(f"Error al insertar registro: {e}")
        close_conn = _is_connection_error(e)
        try:
            conexion.rollback()
        except Exception:
            pass
        return None
    finally:
        return_connection(conexion, close=close_conn)


def recursosByIdVer(id_recurso):
    conexion = get_connection()
    if not conexion:
        return None

    cursor = None
    try:
        start_time = time.time()
        cursor = conexion.cursor()
        query = """
        select titulo,autor,contenido from recursos where id=%s; 
        """
        cursor.execute(query, (id_recurso,))
        resultados = cursor.fetchall()
        duration = time.time() - start_time
        print(f"🔍 Consulta a Supabase tardó: {duration:.2f} segundos")

        if resultados:
            print("Recurso por id:")
            return resultados
        print("No se encontraron resultados")
        return "No se encontraron datos", 404
    except Exception as e:
        print(f"Error al realizar consulta: {e}")
        return_connection(conexion, close=_is_connection_error(e))
        conexion = None
        return None
    finally:
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if conexion:
            return_connection(conexion)


def estresByUsers(id_admin):
    conexion = get_connection()
    if not conexion:
        return []
    try:
        start_time = time.time()
        cursor = conexion.cursor()
        query = """
        SELECT id, nombre_usuario, nombre_actividades, humedad, temperatura, pasos, estres 
        FROM proceso 
        WHERE id_administrador = %s
        ORDER BY id DESC;
        """
        cursor.execute(query, (id_admin,))
        resultados = cursor.fetchall()
        duration = time.time() - start_time
        print(f"🔍 Consulta a Supabase tardó: {duration:.2f} segundos")
        cursor.close()
        return resultados if resultados else []
    except Exception as e:
        print(f"Error al realizar consulta: {e}")
        return_connection(conexion, close=_is_connection_error(e))
        conexion = None
        return []
    finally:
        if conexion:
            return_connection(conexion)


def listarQuerys(query, params=None):
    """Ejecuta una consulta con reintento si Supabase cerró la conexión idle."""
    last_error = None

    for attempt in range(2):
        connection = get_connection()
        if not connection:
            print("Error: No se pudo obtener conexión del pool")
            return None

        try:
            with connection.cursor() as cursor:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

                if query.strip().upper().startswith("SELECT"):
                    result = cursor.fetchall()
                else:
                    connection.commit()
                    result = True
            return_connection(connection)
            return result
        except Exception as e:
            last_error = e
            print(f"Error en la consulta: {str(e)}")
            try:
                connection.rollback()
            except Exception:
                pass
            return_connection(connection, close=_is_connection_error(e))
            if not _is_connection_error(e) or attempt == 1:
                break

    return None


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


def recursosByTitle(titulo, id_admin):
    conexion = get_connection()
    if not conexion:
        return []
    try:
        start_time = time.time()
        cursor = conexion.cursor()
        query = """
        SELECT * 
        FROM recursos
        WHERE titulo ILIKE '%%'|| %s || '%%' AND id_administrador=%s;
        """
        cursor.execute(query, (titulo, int(id_admin),))
        resultados = cursor.fetchall()
        duration = time.time() - start_time
        print(f"🔍 Consulta a Supabase tardó: {duration:.2f} segundos")
        cursor.close()
        return resultados if resultados else []
    except Exception as e:
        print(f"Error al realizar consulta: {e}")
        return_connection(conexion, close=_is_connection_error(e))
        conexion = None
        return []
    finally:
        if conexion:
            return_connection(conexion)
