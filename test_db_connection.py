import psycopg2

DATABASE_URL = "postgresql://neondb_owner:npg_QXgCAz3mUOM9@ep-sweet-union-adde35pm-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

try:
    conn = psycopg2.connect(DATABASE_URL)
    print("Connected to PostgreSQL/NeonDB")
    conn.close()
except Exception as e:
    print("Connection failed:", e)
