import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="lab6",
    user="qeedy",
    password="postgres"
)

with conn.cursor() as cur:
    cur.execute(
        "CREATE TABLE IF NOT EXISTS currencies ("
        "id SERIAL PRIMARY KEY,"
        "currency_name VARCHAR(50) NOT NULL,"
        "rate NUMERIC(50) NOT NULL)"
    )

    cur.execute(
        "CREATE TABLE IF NOT EXISTS admins ("
        "id SERIAL PRIMARY KEY,"
        "chat_id VARCHAR(50) NOT NULL)"
    )
    conn.commit()
