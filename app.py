from flask import Flask, render_template, send_file

app = Flask(__name__)

@app.route("/")
def login():
    return send_file("index.html")

@app.route("/inicio")
def inicio():
    return render_template("inicio.html", title="Inicio")


if __name__ == "__main__":
    app.run(debug=True)