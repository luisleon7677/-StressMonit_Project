from flask import Flask, render_template, send_file, flash
from src.querys import listarQuerys,insertarRecursos,eliminarRecurso,estresByUsers,crear_actividad,recursosByIdVer,recursosByTitle
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
        query = '''
            SELECT id, nombre, username, password, cargo, correo, departamento, edad
            FROM administrador
            WHERE username = %s;
        '''
        admin_data = listarQuerys(query, (username,))

        if admin_data and admin_data[0][3] == password:
            # Configuración de la sesión con nuevos campos
            session.clear()
            session['admin_id']      = admin_data[0][0]
            session['admin_nombre']  = admin_data[0][1]
            session['admin_username']= admin_data[0][2]
            session['admin_cargo']   = admin_data[0][4]
            session['correo']        = admin_data[0][5]
            session['departamento']  = admin_data[0][6]
            session['edad']          = admin_data[0][7]
            session['user_id']       = admin_data[0][0]
            session['user_type']     = 'admin'
                
            flash(f"Bienvenido {admin_data[0][1]}", "success")
            return redirect(url_for("inicio"))
        else:
                flash("Contraseña incorrecta", "danger")
        
        return render_template("login.html", username=username)
    
    # GET request
    if session.get("logged_in"):
        return redirect(url_for("inicio"))
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        correo = request.form.get("correo", "").strip()
        cargo = request.form.get("cargo", "").strip()
        departamento = request.form.get("departamento", "").strip()
        edad = request.form.get("edad", "").strip()

        # Validación de edad ≥ 18
        try:
            edad_int = int(edad)
        except ValueError:
            flash("La edad debe ser un número válido", "danger")
            return render_template("register.html")
        if edad_int < 18:
            flash("Debes tener al menos 18 años para registrarte", "danger")
            return render_template("register.html")

        # Verificar si el administrador ya existe
        query = "SELECT id FROM administrador WHERE username = %s OR correo = %s;"
        if listarQuerys(query, (username, correo)):
            flash("El usuario o correo ya están registrados", "danger")
            return render_template("register.html")

        # Crear administrador
        query = """
            INSERT INTO administrador 
            (nombre, username, password, correo, cargo, departamento, edad) 
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        params = (nombre, username, password, correo, cargo, departamento, edad_int)
        if listarQuerys(query, params):
            flash("Registro de administrador exitoso", "success")
            return redirect(url_for("login"))

    # GET o fallo en POST
    return render_template("register.html")

@app.route("/inicio")
def inicio():
    
    try:
        # Verificación de sesión
        if session.get("user_type") != "admin":
            flash("Debes iniciar sesión como administrador", "warning")
            return redirect(url_for("login"))
        
        # Obtiene la lista (ahora siempre lista, aunque vacía)
        usuarios = estresByUsers(session["user_id"])
        print("Tipo de usuarios:", type(usuarios))
        
         # Columnas esperadas
        columnas = ['ID', 'Nombre', 'Actividad', 'Humedad', 'Temperatura', 'Pasos', 'Estres']

        # Si no hay usuarios, se crea un DataFrame vacío con las columnas esperadas
        if not usuarios:
            flash("No hay datos de usuarios para mostrar.", "info")
            df = pd.DataFrame(columns=columnas)
        else:
            print("Primer elemento:", usuarios[0])
            print("Tipo de primer elemento:", type(usuarios[0]))
            df = pd.DataFrame(usuarios, columns=columnas)
            df = df.pivot_table(index="Actividad", columns="Nombre", values="Estres", aggfunc="mean")
        #Genero el mapa de calor con plotly
        fig = px.imshow(df if not df.empty else [[None]],
                    labels=dict(x="Nombre", y="Actividad", color="Nivel Estrés"),
                    text_auto=".1f", #limita la cantidad de decimales
                    color_continuous_scale='RdYlGn_r',
                    aspect='auto',
                    title="Mapa de Calor de Estrés")
        # Guardar como archivo HTML (para web)
        fig.write_html("static/heatmap_interactivo.html")
        
        return render_template("inicio.html",usuarios=usuarios,pagina='inicio')
    except Exception as e:
        # Captura cualquier error inesperado y lo muestra
        flash(f"Ocurrió un error al generar el mapa de calor: {str(e)}", "danger")
        return render_template("inicio.html", usuarios=[])

@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada correctamente", "info")
    return redirect(url_for("login"))

@app.route("/usuarios")
def usuarios():
    # 1. Lista básica de usuarios
    query = """
        SELECT id, nombre, username, password
        FROM usuarios
        WHERE id_administrador = %s;
    """
    usuarios = listarQuerys(query, (session["user_id"],)) or []

    # 2. Estrés promedio general por usuario
    avg_rows = listarQuerys("""
        SELECT nombre_usuario,
               ROUND(AVG(estres)::numeric, 2) AS avg_estres
        FROM proceso
        WHERE id_administrador = %s
        GROUP BY nombre_usuario;
    """, (session["user_id"],)) or []
    avg_dict = {row[0]: row[1] for row in avg_rows}

    # 3. Promedio de estrés y de duración por actividad y usuario
    act_rows = listarQuerys("""
        SELECT nombre_usuario,
               nombre_actividades,
               ROUND(AVG(estres)::numeric, 2)     AS avg_estres,
               ROUND(AVG(duracion)/60::numeric, 2)   AS avg_duracion_min
        FROM proceso
        WHERE id_administrador = %s
        GROUP BY nombre_usuario, nombre_actividades
        ORDER BY nombre_usuario;
    """, (session["user_id"],)) or []

    activities_by_user = {}
    for nombre_usuario, actividad, est, dur_min in act_rows:
        activities_by_user.setdefault(nombre_usuario, []).append({
            "actividad": actividad,
            "avg_estres":  est,
            "avg_duracion_min": dur_min
        })

    return render_template(
        "usuarios.html",
        usuarios=usuarios,
        avg_dict=avg_dict,
        activities_by_user=activities_by_user,
        pagina='usuarios'
    )


@app.route("/actividades")
def actividades():
    query = """
        SELECT id, nombre, descripcion, grado_dif 
        FROM actividades 
        WHERE id_administrador = %s;
    """
    actividades = listarQuerys(query, (session["user_id"],))
    
    return render_template("actividades.html", actividades=actividades,pagina='actividades')

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
    
    if(titulo is None):
        titulo ="Contenido vacío"
    if(autor is None):
        autor="Seleccione algún recurso para ver su contenido."
    if(contenido is None):
        contenido=""
  
    return render_template("recursos.html",title="Recursos",resultados = recursos,titulo=titulo,autor=autor,contenido=contenido,pagina='recursos')
#creamos una llamada a recursos filtrados por titulo
@app.route("/recursos/find")
def recursosFind():
    titulo= request.args.get('titulo')
    try:
        resultados = recursosByTitle(titulo,session["user_id"])
        if not resultados:
            print("La lista esta vacia")
            return render_template('recursos.html')
        else:
            #print("la consulta fue exitosa")
            #print(resultados)
            #organizamos la lista para enviarla a la tabla
            #convertimos la tupla en diccionario
            recursos =[
                {'id':row[0],'titulo':row[1],'autor':row[2],'contenido':row[3]}
                for row in resultados
            ]
            #print("Este es el resulta de la tupla como diccionario:")
            #print(recursos)
            return render_template('recursos.html',title="Recursos",resultados = recursos) #todo conforme, solo falta corregir lo del boton de ver
    except Exception as e:
        print("Ocurrio un error en la consulta: ", e)
        return render_template('recursos.html')
        

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
    return render_template("soporte.html",title="Soporte",pagina='soporte')

# Crear usuarios
@app.route('/crear_usuario', methods=['GET', 'POST'])
def crear_usuario_route():
    if request.method == 'GET':
        return render_template('crear_usuario.html', title='Crear Usuario')

    # POST: procesa creación
    nombre   = request.form.get('nombre', '').strip()
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()

    # Validación básica
    if not nombre or not username or not password:
        flash("Campos requeridos a completar", "danger")
        return redirect(url_for('crear_usuario_route'))

    # Inserción directa
    insert_query = """
        INSERT INTO usuarios
        (nombre, username, password, id_administrador)
        VALUES (%s, %s, %s, %s)
    """
    params = (nombre, username, password, session['user_id'])
    resultado = listarQuerys(insert_query, params)

    if resultado:
        flash("Usuario creado exitosamente", "success")
        return redirect(url_for('usuarios'))
    else:
        flash("Error al crear usuario", "danger")
        return redirect(url_for('crear_usuario_route'))

# EDITAR usuario (GET muestra formulario; POST procesa)
@app.route('/editar_usuario/<int:id>', methods=['GET', 'POST'])
def editar_usuario_route(id):
    if request.method == 'GET':
        row = listarQuerys(
            "SELECT id, nombre, username, password FROM usuarios WHERE id = %s AND id_administrador = %s",
            (id, session['user_id'])
        )
        if not row:
            flash("Usuario no encontrado o sin permisos", "danger")
            return redirect(url_for('usuarios'))
        usuario = {'id': row[0][0], 'nombre': row[0][1], 'username': row[0][2]}
        return render_template('editar_usuario.html', usuario=usuario, title='Editar Usuario')

    # POST: procesar edición
    nombre   = request.form.get('nombre', '').strip()
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()

    # Campos obligatorios
    if not nombre or not username:
        flash("Nombre y usuario son requeridos", "danger")
        return redirect(url_for('editar_usuario_route', id=id))

    # Duplicado (exceptuando al propio usuario)
    exists = listarQuerys(
        "SELECT 1 FROM usuarios WHERE username = %s AND id_administrador = %s AND id <> %s",
        (username, session['user_id'], id)
    )
    if exists:
        flash("Un usuario ya tiene ese nombre", "danger")
        return redirect(url_for('editar_usuario_route', id=id))

    # Construir query
    if password:
        query = """
            UPDATE usuarios
            SET nombre = %s, username = %s, password = %s
            WHERE id = %s AND id_administrador = %s
        """
        params = (nombre, username, password, id, session['user_id'])
    else:
        query = """
            UPDATE usuarios
            SET nombre = %s, username = %s
            WHERE id = %s AND id_administrador = %s
        """
        params = (nombre, username, id, session['user_id'])

    if listarQuerys(query, params):
        flash("Usuario actualizado exitosamente", "success")
    else:
        flash("Error al actualizar usuario", "danger")
    return redirect(url_for('usuarios'))

# ELIMINAR usuario
@app.route('/eliminar_usuario/<int:id>', methods=['POST'])
def eliminar_usuario_route(id):
    if listarQuerys(
        "DELETE FROM usuarios WHERE id = %s AND id_administrador = %s",
        (id, session['user_id'])
    ):
        flash("Usuario eliminado exitosamente", "success")
    else:
        flash("Error al eliminar usuario o sin permisos", "danger")
    return redirect(url_for('usuarios'))


@app.route('/crear_actividad', methods=['GET', 'POST'])
def crear_actividad_route():
    if request.method == 'GET':
        # GET: solo renderiza el formulario
        return render_template('crear_actividad.html', title='Crear Actividad')

    # POST: procesa el envío del formulario
    nombre      = request.form.get('nombre', '').strip()
    descripcion = request.form.get('descripcion', '').strip()
    try:
        grado_dif = float(request.form.get('grado_dif', 0))
    except ValueError:
        grado_dif = 0.0

    # Validación de campos obligatorios
    if not nombre or not descripcion or grado_dif not in [1.0, 2.0, 3.0]:
        flash("Campos requeridos a completar", "danger")
        return redirect(url_for('crear_actividad_route'))

    # Validación de duplicado
    existe = listarQuerys(
        "SELECT 1 FROM actividades WHERE nombre = %s AND id_administrador = %s",
        (nombre, session['user_id'])
    )
    if existe:
        flash("Una actividad ya tiene ese nombre", "danger")
        return redirect(url_for('crear_actividad_route'))

    # Inserción en la base de datos
    resultado = crear_actividad(nombre, descripcion, grado_dif, session['user_id'])
    if resultado:
        flash("Actividad creada exitosamente", "success")
        return redirect(url_for('actividades'))
    else:
        flash("Error al crear actividad", "danger")
        return redirect(url_for('crear_actividad_route'))

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

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'admin_id' not in session:
        flash("Debes iniciar sesión primero", "danger")
        return redirect(url_for('login'))

    # Obtiene datos del formulario
    admin_id     = session['admin_id']
    nombre       = request.form['nombre'].strip()
    username     = request.form['username'].strip()
    correo       = request.form['correo'].strip()
    cargo        = request.form['cargo'].strip()
    departamento = request.form['departamento'].strip()
    edad         = request.form['edad'].strip()

    # Ejecuta UPDATE en la tabla administrador
    update_q = '''
        UPDATE administrador
        SET nombre=%s, username=%s, correo=%s, cargo=%s, departamento=%s, edad=%s
        WHERE id = %s;
    '''
    success = listarQuerys(update_q, (nombre, username, correo, cargo, departamento, edad, admin_id))

    if success:
        # Sincroniza la sesión con los nuevos datos
        session['admin_nombre']   = nombre
        session['admin_username'] = username
        session['correo']         = correo
        session['cargo']          = cargo
        session['departamento']   = departamento
        session['edad']           = edad
        flash("Perfil actualizado", "success")
    else:
        flash("Error al actualizar perfil", "danger")

    return redirect(url_for('inicio'))

@app.route('/edit_profile', methods=['GET'])
def edit_profile():
    # Muestra el formulario de edición completo
    return render_template('edit_profile.html', title='Editar Perfil')



#esta configuracion debe ativarse cuando subimos a producción
#if __name__ == "__main__":
#    port = int(os.environ.get("PORT", 8000))
#    app.run(host="0.0.0.0", port=port)
    

#esta otra configuracion es para modo desarrollo
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=True)
