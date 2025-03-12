# querys.py
from src.conexion import conectar_db  # Importación relativa


def eliminarRecurso(id):
    #me conecto a base de datos
    conexion = conectar_db()
    if conexion:
        try:
            #creamos el cursor
            cursor = conexion.cursor()
            #preparamos la query
            query = """
            delete from recursos where id = %s;
            """
            #ingresamos la consulta
            cursor.execute(query,(id,))
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
def insertarRecursos(titulo,autor, contenido):
    #me conecto a base de datos
    conexion = conectar_db()
    if conexion:
        try:
            #creamos el cursor
            cursor = conexion.cursor()
            #preparamos la query
            query = """
            insert into recursos (titulo,autor,contenido) values(%s,%s,%s);
            """
            #ingresamos la consulta
            cursor.execute(query,(titulo,autor,contenido))
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

def listarQuerys(query):
    # Verificar que se haya pasado una consulta
    if not query:
        print("No se proporcionó ninguna consulta.")
        return None

    connection = conectar_db()
    if connection:
        try:
            cursor = connection.cursor()
            
            # Ejecutar la consulta proporcionada
            cursor.execute(query)
            rows = cursor.fetchall()  # Obtener todas las filas resultantes
            
            cursor.close()
            connection.close()

            return rows  # Retornar las filas obtenidas

        except Exception as e:
            print(f"Error al realizar la consulta: {e}")
            return None
    else:
        print("No se pudo establecer la conexión con la base de datos.")
        return None

# Llamamos a la función principal solo si este archivo es ejecutado directamente
if __name__ == "__main__":
    # Ejemplo de llamada a la función con una consulta
    titulo = 'redes'
    autor = 'anonymus'
    contenido = 'contenido red'
    
    insertarRecursos(titulo,autor,contenido)
    