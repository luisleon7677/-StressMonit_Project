# querys.py
from src.conexion import conectar_db  # Importación relativa

from werkzeug.security import generate_password_hash, check_password_hash

def listarQuerys(query, params=None):
    connection = conectar_db()
    if not connection:
        print("Error: No se pudo conectar a la base de datos")
        return None

    try:
        cursor = connection.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if query.strip().upper().startswith('SELECT'):
            rows = cursor.fetchall()
            return rows
        else:
            connection.commit()
            return True
            
    except Exception as e:
        print(f"Error en la consulta: {str(e)}")
        connection.rollback()
        return None
    finally:
        if connection:
            cursor.close()
            connection.close()


            
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




def create_user(username, password):
    hashed_pw = generate_password_hash(password)
    # Guardar hashed_pw en lugar de la contraseña en texto plano
    query = f"INSERT INTO usuarios (username, password) VALUES ('{username}', '{hashed_pw}');"
    # Ejecutar query...

def verify_password(username, password):
    query = f"SELECT password FROM usuarios WHERE username = '{username}';"
    result = listarQuerys(query)
    if result and len(result) > 0:
        return check_password_hash(result[0][0], password)
    return False