import pg8000

conn = pg8000.connect(
    host="127.0.0.1",
    port=5433,
    database="paititi",
    user="admin",
    password="123456",
)
print("Conexión exitosa")
conn.close()
