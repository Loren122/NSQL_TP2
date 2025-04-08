from flask import Flask, render_template, redirect, url_for, jsonify
from datetime import datetime, timedelta
import redis
import json

app = Flask(__name__)
connection = redis.StrictRedis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True
)

capitulos = {
    "1": {"titulo": "El Mandaloriano", "estado": "disponible", "precio": 10},
    "2": {"titulo": "El Niño", "estado": "disponible", "precio": 12},
    "3": {"titulo": "El Pecado", "estado": "disponible", "precio": 15},
    "4": {"titulo": "El Santuario", "estado": "disponible", "precio": 11},
    "5": {"titulo": "El Pistolero", "estado": "disponible", "precio": 13},
    "6": {"titulo": "El Prisionero", "estado": "disponible", "precio": 12},
    "7": {"titulo": "La Cuenta Atrás", "estado": "disponible", "precio": 14},
    "8": {"titulo": "Redención", "estado": "disponible", "precio": 15},
    "9": {"titulo": "El Asedio", "estado": "disponible", "precio": 13},
    "10": {"titulo": "La Jedi", "estado": "disponible", "precio": 16},
    "11": {"titulo": "El Creyente", "estado": "disponible", "precio": 14},
    "12": {"titulo": "El Rescate", "estado": "disponible", "precio": 17},
    "13": {"titulo": "El Expulsado", "estado": "disponible", "precio": 12},
    "14": {"titulo": "El Apostata", "estado": "disponible", "precio": 14},
    "15": {"titulo": "El Minero", "estado": "disponible", "precio": 13},
    "16": {"titulo": "El Heredero", "estado": "disponible", "precio": 16},
    "17": {"titulo": "La Fortaleza", "estado": "disponible", "precio": 15},
    "18": {"titulo": "Sombras del Pasado", "estado": "disponible", "precio": 14},
    "19": {"titulo": "El Camino", "estado": "disponible", "precio": 13},
    "20": {"titulo": "Destino", "estado": "disponible", "precio": 17}
}

for num, data in capitulos.items():
    if not connection.exists(f"capitulo:{num}"):
        connection.set(f"capitulo:{num}", json.dumps(data))

if not connection.exists("usuario:saldo"):
    connection.set("usuario:saldo", 30)

@app.route("/")
def home():
    keys = connection.keys("capitulo:*")
    lista = []
    for key in keys:
        num = key.split(":")[1]
        data = json.loads(connection.get(key))

        if data["estado"] == "alquilado" and not connection.exists(f"alquiler:{num}"):
            data["estado"] = "disponible"
            data.pop("expira", None)
            connection.set(key, json.dumps(data))

        if data["estado"] == "reservado" and not connection.exists(f"reserva:{num}"):
            data["estado"] = "disponible"
            data.pop("expira", None)
            connection.set(key, json.dumps(data))

        lista.append({"num": num, **data})

    saldo = int(connection.get("usuario:saldo"))
    return render_template("index.html", capitulos=list, saldo=saldo)

@app.route("/reservar/<num>")
def reservar(num):
    key = f"capitulo:{num}"
    data = json.loads(connection.get(key))

    if data["estado"] == "disponible":
        data["estado"] = "reservado"
        expira_en = datetime.utcnow() + timedelta(seconds=240)
        data["expira"] = expira_en.timestamp()
        connection.set(key, json.dumps(data))
        connection.setex(f"reserva:{num}", 240, "pendiente")

    return redirect(url_for("home"))

@app.route("/pagar/<num>")
def pagar(num):
    key = f"capitulo:{num}"
    data = json.loads(connection.get(key))

    if data["estado"] != "reservado":
        return redirect(url_for("home"))

    saldo = int(connection.get("usuario:saldo"))
    precio = data["precio"]

    if saldo < precio:
        return jsonify({"error": "Saldo insuficiente"}), 400

    saldo -= precio
    connection.set("usuario:saldo", saldo)

    data["estado"] = "alquilado"
    expira_en = datetime.utcnow() + timedelta(seconds=86400)
    data["expira"] = expira_en.timestamp()
    connection.set(key, json.dumps(data))
    connection.setex(f"alquiler:{num}", 86400, "activo")
    connection.delete(f"reserva:{num}")

    return redirect(url_for("home"))

@app.route("/capitulos")
def obtener_capitulos():
    keys = connection.keys("capitulo:*")
    lista = []

    for key in keys:
        num = key.split(":")[1]
        data = json.loads(connection.get(key))

        if data["estado"] == "alquilado" and not connection.exists(f"alquiler:{num}"):
            data["estado"] = "disponible"
            connection.set(key, json.dumps(data))

        lista.append({"num": num, **data})

    saldo = int(connection.get("usuario:saldo"))
    return jsonify({"capitulos": lista, "saldo": saldo})

@app.route("/recargar/<int:monto>")
def recargar(monto):
    saldo = int(connection.get("usuario:saldo"))
    saldo += monto
    connection.set("usuario:saldo", saldo)
    return "", 204


if __name__ == "__main__":
    app.run(debug=True)
