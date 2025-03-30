from flask import Flask, render_template, send_file, flash
from src.querys import listarQuerys
from flask import request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Clave secreta para sesiones

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
        print("Redirección a login - Sesión inválida:", session)
        flash("Debes iniciar sesión como administrador", "warning")
        return redirect(url_for("login"))
    
    print("Acceso concedido a inicio. Sesión:", session)
    return render_template("inicio.html")

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
    query = "select *from recursos;"
    resultados = listarQuerys(query)
    
    if resultados:
        for row in resultados:
            print(row)  # Imprimir cada fila de los resultados
    else:
        print("No se obtuvieron resultados.")
        
    return render_template("recursos.html",title="Recursos")

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
def crear_actividad():
    try:
        nombre = request.form.get('nombre', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        grado_dif = float(request.form.get('grado_dif', 2.0))
        
        # Validar que el grado esté entre los valores permitidos
        if not all([nombre, descripcion]):
            print("Validación fallida: Campos vacíos")
            flash("Nombre y descripción son requeridos", "danger")
            return redirect(url_for('actividades'))
        
        if grado_dif not in [1.0, 2.0, 3.0]:
            print(f"Grado no válido: {grado_dif}")
            flash("Grado de dificultad no válido", "danger")
            return redirect(url_for('actividades'))
        
        # Usar el nombre correcto de la columna (grado_dif)
        query = """
            INSERT INTO actividades (nombre, descripcion, grado_dif)
            VALUES (%s, %s, %s) RETURNING id
        """
        params = (nombre, descripcion, grado_dif)
        print(f"Consulta: {query % params}")
        
        resultado = listarQuerys(query, params)
        print(f"Resultado: {resultado}")
        
        if resultado:
            print("Actividad creada con éxito")
            flash("Actividad creada exitosamente", "success")
        else:
            print("Error en la consulta SQL")
            flash("Error al crear actividad", "danger")
            
    except ValueError as ve:
        print(f"Error de valor: {str(ve)}")
        flash("El valor de dificultad no es válido", "danger")
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        flash("Ocurrió un error al crear la actividad", "danger")
    
    return redirect(url_for('actividades'))







if __name__ == "__main__":
    app.run(debug=True)
