from contextlib import asynccontextmanager
from fastapi import FastAPI
import psycopg2
import os

# Database helper function
def get_db():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        database=os.getenv("POSTGRES_DB", "mydb"),
        user=os.getenv("POSTGRES_USER", "admin"),
        password=os.getenv("POSTGRES_PASSWORD", "admin123"),
        port=os.getenv("POSTGRES_PORT", "5432")
    )

# 1. Define the lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup: Run your database table creation here ---
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS messages (
        id SERIAL PRIMARY KEY,
        content TEXT,
        created_at TIMESTAMP DEFAULT NOW()
    )""")
    cur.execute("SELECT COUNT(*) FROM messages")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO messages (content) VALUES ('Hello from PostgreSQL!')")
    conn.commit()
    cur.close()
    conn.close()
    
    yield  # The application is now running
    
    # --- Shutdown: Clean up any resources here (if needed) ---
    print("Application is shutting down.")

# 2. Pass the lifespan to the FastAPI instance
app = FastAPI(lifespan=lifespan)

@app.get("/")
def root():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT content, created_at FROM messages ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    cur.close()
    conn.close()
    
    if row:
        return {"message": row[0], "time": row[1].isoformat()}
    return {"message": "no data", "time": ""}