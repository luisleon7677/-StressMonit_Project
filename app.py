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
        
        query = "SELECT id, nombre, username, password, cargo FROM administrador WHERE username = %s;"
        admin_data = listarQuerys(query, (username,))
        
        if admin_data:
            if admin_data[0][3] == password:  # Comparación directa
                # Configuración COMPLETA de la sesión
                session.permanent = True
                session["user_type"] = "admin"  # Tipo de usuario
                session["user_id"] = admin_data[0][0]
                session["nombre"] = admin_data[0][1]
                session["username"] = admin_data[0][2]
                session["cargo"] = admin_data[0][4]
                
                print("Sesión establecida:", session)  # Depuración
                return redirect(url_for("inicio"))
            else:
                flash("Contraseña incorrecta", "danger")
        else:
            flash("Usuario no encontrado en administradores", "danger")
        
        return render_template("login.html", username=username)
    
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
    query = "SELECT id, nombre, username, password FROM usuarios;"
    usuarios = listarQuerys(query)
    
    if usuarios:
        for row in usuarios:
            print(row)  # Imprimir cada fila de los resultados
    else:
        print("No se obtuvieron resultados.")
    return render_template("usuarios.html",usuarios=usuarios)

@app.route("/actividades")
def actividades():
    query = "SELECT nombre, descripcion, grado_dif FROM actividades"
    actividades = listarQuerys(query)
    
    if actividades:
        for row in actividades:
            print(row)  # Imprimir cada fila de los resultados
    else:
        print("No se obtuvieron resultados.")
    return render_template("actividades.html",actividades=actividades)

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


if __name__ == "__main__":
    app.run(debug=True)