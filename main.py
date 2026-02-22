import os
import asyncio
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import httpx

from data_processor import DataProcessor
from db import (
    init_db,
    upsert_product,
    insert_price,
    search_products_from_db
)

app = FastAPI()
processor = DataProcessor()

# -----------------------------
# מקורות מחירונים
# -----------------------------
SOURCES = {
    "shufersal": "https://url-to-file.gz",
    "victory": "https://url-to-file.gz",
    "ramilevy": "https://url-to-file.gz"
}


# -----------------------------
# הורדה עם Retry
# -----------------------------
async def download_with_retry(url: str, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response
        except Exception as e:
            print(f"⚠️ ניסיון {attempt + 1} נכשל: {e}")
            if attempt < max_retries - 1:
                wait = 2 ** attempt
                print(f"⏳ מחכה {wait} שניות...")
                await asyncio.sleep(wait)
            else:
                print("❌ כל הניסיונות נכשלו")
                return None


# -----------------------------
# עיבוד ושמירה ל‑DB
# -----------------------------
async def fetch_and_process(source_id: str):
    try:
        url = SOURCES.get(source_id)
        if not url:
            print(f"❌ מקור לא קיים: {source_id}")
            return []

        print(f"📡 מוריד מ-{source_id}...")

        response = await download_with_retry(url)
        if response is None:
            print(f"❌ הורדה נכשלה עבור {source_id}")
            return []

        print(f"✅ הורדה הושלמה ({len(response.content)} bytes)")

        products = processor.process_gz(response.content)

        saved = 0
        for p in products:
            # שמירת מוצר
            upsert_product(p)

            # שמירת מחיר (אם קיים)
            if p.get("price") is not None:
                insert_price({
                    "chain_id": source_id,
                    "store_id": "000",
                    "barcode": p["barcode"],
                    "price": p["price"],
                    "updated_at": p["updated_at"]
                })

            saved += 1

        print(f"✅ {source_id}: נשמרו {saved} מוצרים ל‑DB")
        return products

    except Exception as e:
        print(f"❌ שגיאה ב-{source_id}: {e}")
        return []


# -----------------------------
# API — מוצרים מה‑DB
# -----------------------------
@app.get("/api/products")
async def api_products(search: str = "", limit: int = 100):
    try:
        rows = search_products_from_db(search=search, limit=limit)
        return {
            "success": True,
            "products": rows,
            "returned": len(rows),
            "search": search,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )


# -----------------------------
# עדכון כל המקורות
# -----------------------------
@app.get("/update-all")
async def update_all():
    results = {}
    for source in SOURCES.keys():
        print(f"🚀 מעבד {source}...")
        products = await fetch_and_process(source)
        results[source] = len(products)

    return {"success": True, "results": results}


# -----------------------------
# Startup — יצירת טבלאות
# -----------------------------
@app.on_event("startup")
async def startup_event():
    print("🔧 Initializing database...")
    init_db()
    print("✅ Database ready")


# -----------------------------
# הפעלת השרת
# -----------------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    print("🚀 SmartMarket API Server")
    uvicorn.run(app, host="0.0.0.0", port=port)