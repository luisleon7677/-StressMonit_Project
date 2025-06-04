from flask import Flask, render_template, send_file, flash
from src.querys import listarQuerys,insertarRecursos,eliminarRecurso,estresByUsers,recursosByIdVer
from flask import request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session
import os
#librerias para mapa de calor
import pandas as pd
import seaborn as sns
import plotly.express as px
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import time



app = Flask(__name__)
app.secret_key = 'bN3h$Qz9x@7P!tGv#Wf2LdY*RcVm8AzK'  # Clave secreta fija para sesiones


# Middleware para verificar autenticación
@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'static']
    if request.endpoint not in allowed_routes and 'user_id' not in session:
        return redirect(url_for('login'))


@app.route("/")
def home():
    return redirect(url_for("login"))

# app.py (parte relevante para el login)
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        
        if not username or not password:
            flash("Usuario y contraseña son requeridos", "danger")
            return render_template("login.html", username=username)
        
        # Consulta a la tabla administrador
        query = """
            SELECT id, nombre, username, password, cargo 
            FROM administrador 
            WHERE username = %s;
        """
        admin_data = listarQuerys(query, (username,))
        
        if admin_data:
            # Comparación directa (texto plano - solo para desarrollo)
            if admin_data[0][3] == password:
                # Configuración de la sesión
                session.clear()  # Limpiar sesión previa
                session.permanent = True
                
                # Datos esenciales para el sistema
                session["admin_id"] = admin_data[0][0]  # ID del administrador
                session["admin_nombre"] = admin_data[0][1]  # Nombre completo
                session["admin_username"] = admin_data[0][2]  # Username
                session["admin_cargo"] = admin_data[0][4]  # Cargo
                session["logged_in"] = True
                
                # Compatibilidad con tu sistema actual
                session["user_id"] = admin_data[0][0]  # Mismo ID para compatibilidad
                session["user_type"] = "admin"
                session["nombre"] = admin_data[0][1]
                session["username"] = admin_data[0][2]
                session["cargo"] = admin_data[0][4]
                
                print(f"Sesión establecida para admin ID: {admin_data[0][0]}")  # Depuración
                flash(f"Bienvenido {admin_data[0][1]}", "success")
                return redirect(url_for("inicio"))
            else:
                flash("Contraseña incorrecta", "danger")
        else:
            flash("Credenciales de administrador inválidas", "danger")
        
        return render_template("login.html", username=username)
    
    # GET request
    if session.get("logged_in"):
        return redirect(url_for("inicio"))
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        username = request.form.get("username")
        password = request.form.get("password")
        correo = request.form.get("correo")
        cargo = request.form.get("cargo")
        departamento = request.form.get("departamento")
        edad = request.form.get("edad")
        
        # Verificar si el administrador ya existe
        query = "SELECT id FROM administrador WHERE username = %s OR correo = %s;"
        if listarQuerys(query, (username, correo)):
            flash("El usuario o correo ya están registrados", "danger")
            return render_template("register.html")
            
        # Crear administrador (CONTRASEÑA EN TEXTO PLANO - SOLO DESARROLLO)
        query = """
            INSERT INTO administrador 
            (nombre, username, password, correo, cargo, departamento, edad) 
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        params = (nombre, username, password, correo, cargo, departamento, edad)
        if listarQuerys(query, params):
            flash("Registro de administrador exitoso", "success")
            return redirect(url_for("login"))
    
    return render_template("register.html")

@app.route("/inicio")
def inicio():
    # Verificación MEJORADA de sesión
    if not session.get("user_type") == "admin":
        #print("Redirección a login - Sesión inválida:", session)
        flash("Debes iniciar sesión como administrador", "warning")
        return redirect(url_for("login"))
    
    
    # Obtener usuarios desde la base de datos
    usuarios = estresByUsers(session["user_id"]) #usuarios es una lista de tuplas
    
    #defino columnas
    columnas = ['ID', 'Nombre', 'Actividad', 'Humedad', 'Temperatura', 'Pasos', 'Estres']
    #creo el dataframe
    # Crear el DataFrame , pero es un promedio de cada columna
    df = pd.DataFrame(usuarios, columns=columnas)
    #privoteamos la tabla
    df = df.pivot_table(index="Actividad", columns="Nombre", values="Estres", aggfunc="mean")
    #Genero el mapa de calor con plotly
    fig = px.imshow(df,
                text_auto=True,
                color_continuous_scale='RdYlGn_r',
                aspect='auto',
                title="Mapa de Calor de Estrés")
    # Guardar como archivo HTML (para web)
    fig.write_html("static/heatmap_interactivo.html")
    
    return render_template("inicio.html",usuarios=usuarios)

@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada correctamente", "info")
    return redirect(url_for("login"))

@app.route("/usuarios")
def usuarios():
    query = """
        SELECT id, nombre, username, password 
        FROM usuarios 
        WHERE id_administrador = %s;
    """
    usuarios = listarQuerys(query, (session["user_id"],))
    
    return render_template("usuarios.html", usuarios=usuarios)


@app.route("/actividades")
def actividades():
    query = """
        SELECT id, nombre, descripcion, grado_dif 
        FROM actividades 
        WHERE id_administrador = %s;
    """
    actividades = listarQuerys(query, (session["user_id"],))
    
    return render_template("actividades.html", actividades=actividades)

@app.route("/recursos")
def recursos():
    query = "select *from recursos WHERE id_administrador = %s;"
    resultados = listarQuerys(query, (session["user_id"],))
    #convertimos la tupla en diccionario
    recursos =[
        {'id':row[0],'titulo':row[1],'autor':row[2],'contenido':row[3]}
        for row in resultados
    ]
    
    titulo = request.args.get('titulo')
    autor=request.args.get('autor')
    contenido=request.args.get('contenido')
  
    return render_template("recursos.html",title="Recursos",resultados = recursos,titulo=titulo,autor=autor,contenido=contenido)

@app.route("/recursos/eliminar/<int:id>",methods=['POST'])
def eliminar_recursos(id):
    eliminarRecurso(id,session['user_id'])
    return redirect(url_for('recursos'))
    
#query = "DELETE FROM actividades WHERE id = %s AND id_administrador = %s"
 #   params = (id, session['user_id'])
 

@app.route("/recursos/get/<int:id>",methods=['POST'])
def obtenerRecursoById(id):
    #necesito crear una funcion que obtenga el titulo, autos y contenido de un recurso
    #mediante el id
    print(f"este es el id: {id}")
    data=recursosByIdVer(id)
    titulo= data[0][0]
    autor=data[0][1]
    contenido=data[0][2]
    return redirect(url_for('recursos',titulo= titulo,autor=autor,contenido=contenido)) #probemos con el titulo

  
@app.route("/recursos/registrar/submit" , methods=['post'])
def submit_recurso():
    titulo = request.form["titulo"]
    autor = request.form["autor"]
    contenido = request.form["contenido"]
    id_admin=session["user_id"]
    insertarRecursos(titulo,autor,contenido,id_admin)
    
    
    return redirect(url_for('recursos'))
    
@app.route("/recursos/registrar")
def registrar_recursos():
    return render_template("recurso_registrar.html",title="Registro Recursos")


@app.route("/soporte")
def soporte():
    return render_template("soporte.html",title="Soporte")


# Crear usuarios
@app.route("/crear_usuario", methods=["POST"])
def crear_usuario():
    try:
        # Obtener datos del formulario
        nombre = request.form.get("nombre", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        
        # Validación básica de campos
        if not all([nombre, username, password]):
            flash("Todos los campos son requeridos", "danger")
            return redirect(url_for("usuarios"))
        
        # Verificar si el usuario ya existe
        check_query = "SELECT id FROM usuarios WHERE username = %s"
        if listarQuerys(check_query, (username,)):
            flash("El nombre de usuario ya está en uso", "danger")
            return redirect(url_for("usuarios"))
        
        # Obtener ID del administrador de la sesión (sin validar si es admin)
        admin_id = session.get("admin_id") or session.get("user_id")
        
        if not admin_id:
            flash("No se pudo identificar al administrador", "danger")
            return redirect(url_for("usuarios"))
        
        # Insertar nuevo usuario con el ID del admin
        insert_query = """
            INSERT INTO usuarios 
            (nombre, username, password, id_administrador) 
            VALUES (%s, %s, %s, %s)
        """
        params = (nombre, username, password, admin_id)
        
        if listarQuerys(insert_query, params):
            flash("Usuario creado exitosamente", "success")
        else:
            flash("Error al crear usuario", "danger")
            
    except Exception as e:
        print(f"Error al crear usuario: {str(e)}")
        flash("Ocurrió un error al crear el usuario", "danger")
    
    return redirect(url_for("usuarios"))


@app.route('/crear_actividad', methods=['POST'])
def crear_actividad_route():  # Cambiamos el nombre para evitar conflicto
    try:
        if 'user_id' not in session:
            flash("Debes iniciar sesión primero", "danger")
            return redirect(url_for('login'))

        # Obtener datos del formulario
        nombre = request.form.get('nombre', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        grado_dif = request.form.get('grado_dif', '2.0')
        admin_id = session['user_id']  # ID del administrador logueado

        # Validaciones
        if not all([nombre, descripcion]):
            flash("Nombre y descripción son requeridos", "danger")
            return redirect(url_for('actividades'))

        try:
            grado_dif = float(grado_dif)
            if grado_dif not in [1.0, 2.0, 3.0]:
                flash("Grado de dificultad no válido", "danger")
                return redirect(url_for('actividades'))
        except ValueError:
            flash("Valor de dificultad no válido", "danger")
            return redirect(url_for('actividades'))

        # Llamar a la función de creación
        from src.querys import crear_actividad  # Importar la función
        resultado = crear_actividad(nombre, descripcion, grado_dif, admin_id)
        
        if resultado:
            flash("Actividad creada exitosamente", "success")
        else:
            flash("Error al crear actividad", "danger")

    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        flash("Ocurrió un error al crear la actividad", "danger")
    
    return redirect(url_for('actividades'))

@app.route('/editar_actividad/<int:id>', methods=['GET', 'POST'])
def editar_actividad(id):
    if 'user_id' not in session:
        flash("Debes iniciar sesión primero", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Procesar el formulario de edición
        nombre = request.form.get('nombre', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        grado_dif = float(request.form.get('grado_dif', 2.0))
        
        query = """
            UPDATE actividades 
            SET nombre = %s, descripcion = %s, grado_dif = %s
            WHERE id = %s AND id_administrador = %s
        """
        params = (nombre, descripcion, grado_dif, id, session['user_id'])
        
        if listarQuerys(query, params):
            flash("Actividad actualizada exitosamente", "success")
        else:
            flash("Error al actualizar la actividad", "danger")
        
        return redirect(url_for('actividades'))
    
    else:
        # Mostrar formulario de edición
        query = "SELECT id, nombre, descripcion, grado_dif FROM actividades WHERE id = %s AND id_administrador = %s"
        actividad = listarQuerys(query, (id, session['user_id']))
        
        if not actividad:
            flash("Actividad no encontrada o no tienes permisos", "danger")
            return redirect(url_for('actividades'))
            
        return render_template('editar_actividad.html', actividad=actividad[0])

@app.route('/eliminar_actividad/<int:id>', methods=['POST'])
def eliminar_actividad(id):
    if 'user_id' not in session:
        flash("Debes iniciar sesión primero", "danger")
        return redirect(url_for('login'))

    query = "DELETE FROM actividades WHERE id = %s AND id_administrador = %s"
    params = (id, session['user_id'])
    
    if listarQuerys(query, params):
        flash("Actividad eliminada exitosamente", "success")
    else:
        flash("Error al eliminar la actividad o no tienes permisos", "danger")
    
    return redirect(url_for('actividades'))




#esta configuracion debe ativarse cuando subimos a producción
#if __name__ == "__main__"
#    port = int(os.environ.get("PORT", 8000))
#    app.run(host="0.0.0.0", port=port)
    

#esta otra configuracion es para modo desarrollo
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=True)

