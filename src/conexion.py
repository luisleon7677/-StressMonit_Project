import psycopg2
from psycopg2 import pool, OperationalError, InterfaceError
from psycopg2.extensions import TRANSACTION_STATUS_IDLE
from dotenv import load_dotenv
import os
import atexit

load_dotenv()

connection_pool = None


def initialize_pool():
    global connection_pool
    print("📡 Intentando conectar con Supabase...")
    try:
        # maxconn bajo: Supabase (free/pro) limita conexiones concurrentes.
        # keepalives evitan que el servidor cierre sockets idle demasiado pronto.
        connection_pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=5,
            user=os.getenv("DB_USER") or os.getenv("USER"),
            password=os.getenv("PASSWORD"),
            host=os.getenv("HOST"),
            port=os.getenv("PORT"),
            database=os.getenv("DBNAME"),
            sslmode="require",
            keepalives=1,
            keepalives_idle=30,
            keepalives_interval=10,
            keepalives_count=5,
            connect_timeout=10,
        )
        print("Pool de conexiones creado exitosamente")
    except Exception as e:
        connection_pool = None
        print(f"Error al crear pool de conexiones: {e}")


def _is_connection_alive(connection):
    """Comprueba si la conexión sigue usable (Supabase cierra las idle)."""
    try:
        if connection is None or connection.closed:
            return False
        old_autocommit = connection.autocommit
        connection.autocommit = True
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        finally:
            connection.autocommit = old_autocommit
        return True
    except (OperationalError, InterfaceError, psycopg2.Error):
        return False


def get_connection():
    """Obtiene una conexión viva del pool; descarta las que ya cerró el servidor."""
    global connection_pool
    if not connection_pool:
        initialize_pool()
    if not connection_pool:
        return None

    last_error = None
    for _ in range(3):
        try:
            connection = connection_pool.getconn()
        except Exception as e:
            last_error = e
            initialize_pool()
            if not connection_pool:
                break
            continue

        if _is_connection_alive(connection):
            return connection

        # Conexión muerta: cerrarla y no devolverla al pool
        try:
            connection_pool.putconn(connection, close=True)
        except Exception:
            try:
                connection.close()
            except Exception:
                pass

    if last_error:
        print(f"Error al obtener conexión: {last_error}")
    return None


def return_connection(connection, close=False):
    """Devuelve la conexión al pool, o la cierra si está rota."""
    if not connection_pool or connection is None:
        return

    try:
        if close or connection.closed:
            connection_pool.putconn(connection, close=True)
            return

        # Dejar la conexión idle limpia antes de reutilizarla
        try:
            if connection.get_transaction_status() != TRANSACTION_STATUS_IDLE:
                connection.rollback()
        except (OperationalError, InterfaceError):
            connection_pool.putconn(connection, close=True)
            return

        connection_pool.putconn(connection)
    except Exception:
        try:
            connection.close()
        except Exception:
            pass


@atexit.register
def close_pool():
    if connection_pool:
        connection_pool.closeall()
        print("Pool de conexiones cerrado")


initialize_pool()
