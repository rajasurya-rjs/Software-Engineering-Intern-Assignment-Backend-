import psycopg2

DATABASE_URL = "postgresql://neondb_owner:npg_QXgCAz3mUOM9@ep-sweet-union-adde35pm-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def get_connection():
    return psycopg2.connect(DATABASE_URL)
