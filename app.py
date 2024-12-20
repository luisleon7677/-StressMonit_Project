from flask import Flask, render_template, send_file

app = Flask(__name__)

@app.route("/")
def login():
    return send_file("index.html")

@app.route("/inicio")
def inicio():
    return render_template("inicio.html", title="Inicio")

@app.route("/usuarios")
def usuarios():
    return render_template("usuarios.html",title="Usuarios")

@app.route("/actividades")
def actividades():
    return render_template("actividades.html",title="Actividades")

@app.route("/recursos")
def recursos():
    return render_template("recursos.html",title="Recursos")

@app.route("/soporte")
def soporte():
    return render_template("soporte.html",title="Soporte")



if __name__ == "__main__":
    app.run(debug=True)