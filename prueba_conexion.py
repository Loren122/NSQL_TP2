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

listar_capitulos()