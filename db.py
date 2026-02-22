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
    from db import bulk_upsert_products, bulk_insert_prices

async def process_gov_sources():
    from gov_sources import SOURCES, fetch_gov_file

    results = {}
    total = 0

    for name, url in SOURCES.items():
        print(f"📡 מוריד {name}...")
        data = await fetch_gov_file(url)

        products = []
        prices = []

        for item in data:
            products.append({
                "barcode": item.get("item_code"),
                "name": item.get("item_name"),
                "manufacturer": item.get("manufacturer_name"),
                "chain_id": item.get("chain_id"),
                "store_id": item.get("store_id"),
            })

            prices.append({
                "barcode": item.get("item_code"),
                "price": item.get("item_price"),
                "store_id": item.get("store_id"),
                "chain_id": item.get("chain_id"),
            })

        bulk_upsert_products(products)
        bulk_insert_prices(prices)

        results[name] = len(products)
        total += len(products)

    return {"total": total, "details": results}