from flask import Flask, render_template, send_file
from src.querys import listarQuerys
from flask import request, redirect, url_for

app = Flask(__name__)

# Credenciales de prueba
users = {"admin": "password123", "testuser": "mypassword"}

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username in users and users[username] == password:
            return redirect(url_for("inicio"))
        return "Credenciales inválidas", 401
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        if username in users:
            return "Usuario ya existe", 400
        users[username] = password
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/inicio")
def inicio():
    return render_template("inicio.html", title="Inicio")

@app.route("/usuarios")
def usuarios():
    query = "select *from usuarios;"
    resultados1 = listarQuerys(query)
    
    if resultados1:
        for row in resultados1:
            print(row)  # Imprimir cada fila de los resultados
    else:
        print("No se obtuvieron resultados.")
    return render_template("usuarios.html",title="Usuarios")

@app.route("/actividades")
def actividades():
    query = "select *from actividades;"
    resultados2 = listarQuerys(query)
    
    if resultados2:
        for row in resultados2:
            print(row)  # Imprimir cada fila de los resultados
    else:
        print("No se obtuvieron resultados.")
    return render_template("actividades.html",title="Actividades")

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