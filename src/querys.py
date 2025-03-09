# querys.py
from src.conexion import conectar_db  # Importación relativa

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
    query = "SELECT * FROM recursos;"
    result = listarQuerys(query)
    if result:
        for row in result:
            print(row)

    query = "SELECT * FROM actividades;"
    result = listarQuerys(query)
    if result:
        for row in result:
            print(row)
    
    query = "SELECT * FROM usuarios;"
    result = listarQuerys(query)
    if result:
        for row in result:
            print(row)