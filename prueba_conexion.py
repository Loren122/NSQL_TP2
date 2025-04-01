import redis
import json

connection = redis.StrictRedis(
    host="localhost",
    port=6379,
    db=0
)

capitulos = {
    "1": {"titulo": "El Mandaloriano", "estado": "disponible"},
    "2": {"titulo": "El Niño", "estado": "disponible"},
    "3": {"titulo": "El Pecado", "estado": "disponible"}
}

for num, data in capitulos.items():
    connection.set(f"capitulo:{num}", json.dumps(data))

# print(json.loads(connection.get("capitulo:1")))