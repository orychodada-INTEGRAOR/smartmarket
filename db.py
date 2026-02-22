import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_connection():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not set")
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS chains (
        id SERIAL PRIMARY KEY,
        chain_id VARCHAR(50) UNIQUE NOT NULL,
        name TEXT NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS stores (
        id SERIAL PRIMARY KEY,
        chain_id VARCHAR(50) NOT NULL,
        store_id VARCHAR(50) NOT NULL,
        name TEXT,
        city TEXT,
        address TEXT,
        UNIQUE(chain_id, store_id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id SERIAL PRIMARY KEY,
        barcode VARCHAR(50),
        name TEXT NOT NULL,
        manufacturer TEXT,
        unit_quantity TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS prices (
        id SERIAL PRIMARY KEY,
        chain_id VARCHAR(50) NOT NULL,
        store_id VARCHAR(50) NOT NULL,
        barcode VARCHAR(50) NOT NULL,
        price NUMERIC(10, 2) NOT NULL,
        updated_at TIMESTAMP NOT NULL
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS promotions (
        id SERIAL PRIMARY KEY,
        chain_id VARCHAR(50) NOT NULL,
        store_id VARCHAR(50) NOT NULL,
        barcode VARCHAR(50) NOT NULL,
        description TEXT,
        price NUMERIC(10, 2),
        valid_from TIMESTAMP,
        valid_to TIMESTAMP
    );
    """)

    conn.commit()
    cur.close()
    conn.close()