import redis
import json

connection = redis.StrictRedis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True
)

capitulos = {
    "1": {"titulo": "El Mandaloriano", "estado": "disponible", "precio": 10},
    "2": {"titulo": "El Niño", "estado": "disponible", "precio": 12},
    "3": {"titulo": "El Pecado", "estado": "disponible", "precio": 15}
}

for num, data in capitulos.items():
    connection.set(f"capitulo:{num}", json.dumps(data))

connection.set("usuario:saldo", 30)

def listar_capitulos():
    keys= connection.keys("capitulo:*")
    for key in keys:
        num = key.split(":")[1]
        cap_data = connection.get(key)
        cap_info = json.loads(cap_data)

        if cap_info["estado"] == "alquilado" and not connection.exists(f"alquiler:{num}"):
            cap_info["estado"] = "disponible"

        print(f"Capítulo {num}: {cap_info['titulo']} - Estado: {cap_info['estado']} - Precio: {cap_info['precio']}")

def alquilar_capitulo(num):
    cap_key = f"capitulo:{num}"
    cap_data = connection.get(cap_key)

    if not cap_data:
        print("Capitulo no encontrado")
        return

    cap_info = json.loads(cap_data)
    if cap_info["estado"] != "disponible":
        print("Capitulo no disponible")
        return

    cap_info["estado"] = "reservado"
    connection.set(cap_key, json.dumps(cap_info))
    connection.setex(f"reserva:{num}", 240, "pendiente")
    print(f"Capítulo {num} reservado por 4 minutos")

def confirmar_pago(num):
    cap_key = f"capitulo:{num}"
    cap_data = connection.get(cap_key)

    if not cap_data:
        print("Capitulo no encontrado")
        return

    cap_info = json.loads(cap_data)

    if cap_info["estado"] != "reservado":
        print(f"Capitulo {num} no reservado")
        return

    saldo = int(connection.get("usuario:saldo"))
    precio = int(cap_info["precio"])

    if saldo < precio:
        print("Saldo insuficiente")
        return

    nuevo_saldo = saldo - precio
    connection.set("usuario:saldo", nuevo_saldo)

    cap_info["estado"] = "alquilado"
    connection.set(cap_key, json.dumps(cap_info))
    connection.setex(f"alquiler:{num}", 86400, "activo")
    connection.delete(f"reserva:{num}")
    print(f"Capítulo {num} alquilado por 24 horas. Saldo restante: ${nuevo_saldo}")

listar_capitulos()
print("----------------------------------------------")
alquilar_capitulo(1)
print("----------------------------------------------")
listar_capitulos()
print("----------------------------------------------")
confirmar_pago(1)
print("----------------------------------------------")
listar_capitulos()