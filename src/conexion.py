import psycopg2
from dotenv import load_dotenv
import os


# Load environment variables from .env
load_dotenv()

def conectar_db():
    USER = os.getenv("USER")
    PASSWORD = os.getenv("PASSWORD")
    HOST = os.getenv("HOST")
    PORT = os.getenv("PORT")
    DBNAME = os.getenv("DBNAME")

    try:
        connection = psycopg2.connect(
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT,
            dbname=DBNAME
        )
        

        return connection
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None
    

