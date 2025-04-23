import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv
import os
import atexit

# Configuración inicial
load_dotenv()



# Pool de conexiones
connection_pool = None




def initialize_pool():
    global connection_pool
    print("📡 Intentando conectar con Supabase...")
    try:
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            user=os.getenv("USER"),
            password=os.getenv("PASSWORD"),
            host=os.getenv("HOST"),
            port=os.getenv("PORT"),
            database=os.getenv("DBNAME")
        )
        print("Pool de conexiones creado exitosamente")
    except Exception as e:
        print(f"Error al crear pool de conexiones: {e}")

def get_connection():
    if not connection_pool:
        initialize_pool()
    return connection_pool.getconn()

def return_connection(connection):
    if connection_pool:
        connection_pool.putconn(connection)

# Cierra el pool al terminar la aplicación
@atexit.register
def close_pool():
    if connection_pool:
        connection_pool.closeall()
        print("Pool de conexiones cerrado")

initialize_pool()