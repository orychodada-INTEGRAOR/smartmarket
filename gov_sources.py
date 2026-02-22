import gzip
import json
import httpx
from db import bulk_upsert_products, bulk_insert_prices

SOURCES = {
    "gov_full": "https://next.obudget.org/sijui_utp/utp_prices_full.json.gz",
    "gov_updates": "https://next.obudget.org/sijui_utp/utp_prices_updates.json.gz",
    "gov_promotions": "https://next.obudget.org/sijui_utp/utp_prices_promotions.json.gz",
}

async def fetch_gov_file(url: str):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }
    async with httpx.AsyncClient(headers=headers, timeout=60) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        data = gzip.decompress(resp.content)
        return json.loads(data)

async def process_gov_sources():
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