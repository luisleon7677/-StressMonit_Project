from src.conexion import get_connection, return_connection
from werkzeug.security import generate_password_hash, check_password_hash

def eliminarRecurso(id,id_admin):
    #me conecto a base de datos
    conexion = get_connection()
    if conexion:
        try:
            #creamos el cursor
            cursor = conexion.cursor()
            #preparamos la query
            query = """
            delete from recursos where id = %s AND id_administrador = %s;
            """
            #ingresamos la consulta
            cursor.execute(query,(id,id_admin,))
            #confirmo la insersion a base de datos (IMPORTANTE)
            conexion.commit()
            #cerrar la conexion
            cursor.close()
            conexion.close()
            print("recurso eliminado")
            return "Recurso elimindo",200
            
        except Exception as e:
            print(f"Error al eliminar registro: {e}")
            return None
def insertarRecursos(titulo,autor, contenido,id_admin):
    #me conecto a base de datos
    conexion = get_connection()
    if conexion:
        try:
            #creamos el cursor
            cursor = conexion.cursor()
            #preparamos la query
            query = """
            insert into recursos (titulo,autor,contenido,id_administrador) values(%s,%s,%s,%s);
            """
            #ingresamos la consulta
            cursor.execute(query,(titulo,autor,contenido,id_admin))
            #confirmo la insersion a base de datos (IMPORTANTE)
            conexion.commit()
            #cerrar la conexion
            cursor.close()
            conexion.close()
            print("recurso insertado")
            return "Recurso insertado",200
            
        except Exception as e:
            print(f"Error al insertar registro: {e}")
            return None

#funcion para obtener data de estres por usuarios
def estresByUsers(id_admin):
    #me conecto a base de datos
    conexion = get_connection()
    if conexion:
        try:
            #creamos el cursor
            cursor = conexion.cursor()
            #preparamos la query
            query = """
            select id,nombre_usuario,nombre_actividades,humedad,temperatura,pasos,estres from proceso where id_administrador=%s;
            """
            #ingresamos la consulta
            cursor.execute(query,(id_admin,))
            
             # Recuperamos los resultados
            resultados = cursor.fetchall()
                
            # Si hay resultados, los retornamos
            if resultados:
                    print("Lista de usuarios por estrés:")
                    return resultados # Devolver los resultados con un código de éxito
            else:
                    print("No se encontraron resultados")
                    return "No se encontraron datos", 404  # Código de error si no hay datos
            
        except Exception as e:
            print(f"Error al realizar consulta: {e}")
            return None

def listarQuerys(query, params=None):
    connection = get_connection()
    if not connection:
        print("Error: No se pudo obtener conexión del pool")

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
# Llamamos a la función principal solo si este archivo es ejecutado directamente
if __name__ == "__main__":
    # Ejemplo de llamada a la función con una consulta
    
    id_user = 1
    
    estresByUsers(id_user)
    
