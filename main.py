from fastapi import FastAPI
from data_sources import get_latest_sources
from fetcher import fetch_with_headers
from data_processor import DataProcessor
from db import bulk_upsert_products, bulk_insert_prices

app = FastAPI()

SOURCES = {}


@app.on_event("startup")
async def startup_event():
    global SOURCES
    print("📡 טוען רשימת קבצים ממשרד הכלכלה...")
    SOURCES = await get_latest_sources()
    print("✅ SOURCES נטען בהצלחה")


@app.get("/update-all")
async def update_all():
    processor = DataProcessor()
    total_products = 0

    for chain_id, urls in SOURCES.items():
        print(f"🚀 מעבד רשת {chain_id}...")

        # PriceFull פעם ביום
        if urls["full"]:
            print("📡 מוריד PriceFull...")
            content = await fetch_with_headers(urls["full"])
            products, prices = processor.process_gz(content)
            bulk_upsert_products(products)
            bulk_insert_prices(prices)
            total_products += len(products)

        # PriceUpdate כל שעה
        if urls["update"]:
            print("📡 מוריד PriceUpdate...")
            content = await fetch_with_headers(urls["update"])
            products, prices = processor.process_gz(content)
            bulk_upsert_products(products)
            bulk_insert_prices(prices)
            total_products += len(products)

    return {"status": "success", "total_products": total_products}