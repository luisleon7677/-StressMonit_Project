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
        username = request.form.get("username")
        password = request.form.get("password")
        
        # Consulta segura con parámetros
        query = "SELECT id, username, password FROM usuarios WHERE username = %s;"
        user_data = listarQuerys(query, (username,))
        
        if user_data:
            # Comparación directa de contraseñas (TEXTO PLANO)
            if user_data[0][2] == password:
                session["user_id"] = user_data[0][0]
                session["username"] = user_data[0][1]
                flash("Inicio de sesión exitoso", "success")
                return redirect(url_for("inicio"))
        
        flash("Usuario o contraseña incorrectos", "danger")
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Has cerrado sesión correctamente", "info")
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        # Verificar si el usuario ya existe
        query = "SELECT id FROM usuarios WHERE username = %s;"
        if listarQuerys(query, (username,)):
            flash("El usuario ya está registrado", "danger")
            return render_template("register.html")
            
        # Crear usuario con contraseña en texto plano (NO RECOMENDADO PARA PRODUCCIÓN)
        query = "INSERT INTO usuarios (username, password) VALUES (%s, %s);"
        if listarQuerys(query, (username, password)):
            flash("Registro exitoso. Por favor inicia sesión", "success")
            return redirect(url_for("login"))
    
    return render_template("register.html")

@app.route("/inicio")
def inicio():
    return render_template("inicio.html", title="Inicio")

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