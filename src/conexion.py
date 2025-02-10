import psycopg2

try:
    conection = psycopg2.connect(
        host='localhost',
        user='postgres',
        password='1234',
        database='dbstressmonit'
        
    )
    print("conexion exitosa")
    #creamos un cursor para interacturar con la base de datos
    cursor=conection.cursor()
    cursor.execute("SELECT * FROM usuarios")
    #imprimimos las filas
    rows=cursor.fetchall()
    for row in rows:
        print(row)
        
except Exception as ex:
    print(ex)
    
finally:
    conection.close()
    print("Conexion finalizada")