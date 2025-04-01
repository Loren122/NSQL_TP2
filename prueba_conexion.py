import redis
import json

connection = redis.StrictRedis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True
)

capitulos = {
    "1": {"titulo": "El Mandaloriano", "estado": "disponible"},
    "2": {"titulo": "El Niño", "estado": "disponible"},
    "3": {"titulo": "El Pecado", "estado": "disponible"}
}

for num, data in capitulos.items():
    connection.set(f"capitulo:{num}", json.dumps(data))

def listar_capitulos():
    keys= connection.keys("capitulo:*")
    for key in keys:
        num = key.split(":")[1]
        data = json.loads(connection.get(key))
        print(f"Capítulo {num}: {data['titulo']} - Estado: {data['estado']}")

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
    connection.setex(cap_key, 240, json.dumps(cap_info))
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

    cap_info["estado"] = "alquilado"
    connection.setex(cap_key, 86400, json.dumps(cap_info))
    print(f"Capítulo {num} alquilado por 24 horas")

listar_capitulos()
print("----------------------------------------------")
alquilar_capitulo(1)
print("----------------------------------------------")
listar_capitulos()
print("----------------------------------------------")
confirmar_pago(2)
print("----------------------------------------------")
listar_capitulos()