from fastapi import FastAPI
from data_sources import get_latest_file_url
from fetcher import fetch_with_headers
from data_processor import DataProcessor
from db import bulk_upsert_products, bulk_insert_prices

app = FastAPI()

# רשימת הרשתות שהצייד יודע לטפל בהן
TARGETS = [
    "good_pharm",
    "laib",
    "zol_vebegadol",
    "hazi_hinam"
]


@app.get("/update-all")
async def update_all():
    """
    מפעיל את הצייד על כל הרשתות, מוריד את הקובץ הכי חדש,
    מפענח, ומכניס ל-DB.
    """
    processor = DataProcessor()
    results = {}
    total_products = 0

    for source_id in TARGETS:
        print(f"\n🚀 מחפש קובץ עבור {source_id}...")

        # 1) מציאת קובץ הכי חדש
        url = await get_latest_file_url(source_id)
        if not url:
            results[source_id] = "לא נמצא קובץ"
            continue

        try:
            # 2) הורדה עם headers (עוקף חסימות)
            print(f"📡 מוריד קובץ מ-{source_id}...")
            content = await fetch_with_headers(url)

            # 3) פענוח GZ/XML
            products, prices = processor.process_gz(content)

            # 4) הזרקה ל-DB
            if products:
                # הוספת chain_id ו-store_id (אם תרצה נבנה לוגיקה חכמה)
                for p in products:
                    p["chain_id"] = source_id
                    p["store_id"] = "000"

                bulk_upsert_products(products)
                bulk_insert_prices(prices)

                total_products += len(products)
                results[source_id] = f"OK — {len(products)} מוצרים"
            else:
                results[source_id] = "לא נמצאו מוצרים בקובץ"

        except Exception as e:
            results[source_id] = f"שגיאה: {str(e)}"

    return {
        "status": "complete",
        "total_products": total_products,
        "results": results
    }