from . import conexion

def listarUsuarios():
    usuarios=conexion.consultaSQL("Select *from personas")
    #existen diferentes maneras en como se pasan objetos o listas a jinja y los interpreta diferente, averiguar mas sobre ello
    return usuarios
