import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

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


# ---------- פונקציות כתיבה ----------

def upsert_product(product):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO products (barcode, name, manufacturer, unit_quantity)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (barcode) DO UPDATE SET
            name = EXCLUDED.name,
            manufacturer = EXCLUDED.manufacturer,
            unit_quantity = EXCLUDED.unit_quantity;
    """, (
        product.get("barcode"),
        product.get("name"),
        product.get("manufacturer"),
        product.get("unit_quantity"),
    ))

    conn.commit()
    cur.close()
    conn.close()


def insert_price(price_row):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO prices (chain_id, store_id, barcode, price, updated_at)
        VALUES (%s, %s, %s, %s, %s);
    """, (
        price_row.get("chain_id"),
        price_row.get("store_id"),
        price_row.get("barcode"),
        price_row.get("price"),
        price_row.get("updated_at") or datetime.utcnow(),
    ))

    conn.commit()
    cur.close()
    conn.close()


# ---------- פונקציות קריאה ל‑API ----------

def search_products_from_db(search: str = "", limit: int = 100):
    conn = get_connection()
    cur = conn.cursor()

    if search:
        like = f"%{search.lower()}%"
        cur.execute("""
            SELECT
                p.barcode,
                p.name,
                p.manufacturer,
                p.unit_quantity
            FROM products p
            WHERE LOWER(p.name) LIKE %s
               OR LOWER(p.manufacturer) LIKE %s
            LIMIT %s;
        """, (like, like, limit))
    else:
        cur.execute("""
            SELECT
                p.barcode,
                p.name,
                p.manufacturer,
                p.unit_quantity
            FROM products p
            LIMIT %s;
        """, (limit,))

    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows