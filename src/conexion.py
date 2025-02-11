import psycopg2

def consultaSQL(consulta):
    conection = psycopg2.connect(
        host='localhost',
        user='postgres',
        password='1234',
        database='dbstressmonit'
        
    )
    #creamos un cursor para interacturar con la base de datos
    cursor=conection.cursor()
    cursor.execute(consulta)
    #Obtenemos todos los registros
    rows=cursor.fetchall()
    
    return rows 