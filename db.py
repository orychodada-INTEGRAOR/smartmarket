import psycopg2
from psycopg2.extras import execute_values
import os

DATABASE_URL = os.environ.get("DATABASE_URL")


def bulk_upsert_products(products):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    query = """
        INSERT INTO products (barcode, name, manufacturer, unit_quantity)
        VALUES %s
        ON CONFLICT (barcode) DO UPDATE SET
            name = EXCLUDED.name,
            manufacturer = EXCLUDED.manufacturer,
            unit_quantity = EXCLUDED.unit_quantity
    """

    data = [(p["barcode"], p["name"], p["manufacturer"], p["unit_quantity"]) for p in products]

    execute_values(cur, query, data)
    conn.commit()
    cur.close()
    conn.close()


def bulk_insert_prices(prices):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    query = """
        INSERT INTO prices (chain_id, store_id, barcode, price, updated_at)
        VALUES %s
    """

    data = [(p["chain_id"], p["store_id"], p["barcode"], p["price"], p["updated_at"]) for p in prices]

    execute_values(cur, query, data)
    conn.commit()
    cur.close()
    conn.close()