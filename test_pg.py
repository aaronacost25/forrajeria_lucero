import psycopg2

try:
    conn = psycopg2.connect(
        dbname="tienda",
        user="postgres",
        password="aaron",
        host="localhost",
        port="5432"
    )
    print("✅ Conexión exitosa a PostgreSQL.")
    conn.close()
except Exception as e:
    print("❌ Error al conectar:", e)
