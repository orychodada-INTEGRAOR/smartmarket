"""
SmartMarket - Main API Server
שרת ראשי לניהול מחירים בזמן אמת
"""

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import requests
from data_processor import DataProcessor
import asyncio
from datetime import datetime
import os

app = FastAPI(
    title="SmartMarket API",
    description="API לניהול מחירי קמעונאות בזמן אמת",
    version="1.0.0"
)

processor = DataProcessor()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SOURCES = {
  SOURCES = {
    'shufersal_001': 'https://pricesprodpublic.blob.core.windows.net/price/Price7290027600007-001-202602220200.gz?sv=2014-02-14&sr=b&sig=Hff8zJRk%2FWnG1HcIwVoNR%2BTs5ETQfQ5c33uSct46otU%3D&se=2026-02-22T06%3A27%3A18Z&sp=r'
}
}

@app.get("/")
async def root():
    return {
        "app": "SmartMarket API",
        "status": "🟢 פעיל",
        "version": "1.0.0",
        "endpoints": {
            "/api/products": "קבלת מוצרים (עם חיפוש)",
            "/update-all": "עדכון כל המקורות",
            "/status": "סטטוס המערכת"
        }
    }

@app.get("/api/products")
async def get_products(search: str = "", source: str = "all", limit: int = 100):
    try:
        all_products = []
        
        if source == "all":
            sources_to_load = SOURCES.keys()
        elif source in SOURCES:
            sources_to_load = [source]
        else:
            raise HTTPException(status_code=400, detail=f"מקור לא קיים: {source}")
        
        for src in sources_to_load:
            products = processor.load_from_cache(src, max_age_hours=1)
            
            if products is None:
                print(f"📥 מוריד נתונים טריים עבור {src}...")
                products = await fetch_and_process(src)
            
            if products:
                all_products.extend(products)
        
        if search:
            search_lower = search.lower()
            all_products = [
                p for p in all_products 
                if search_lower in p.get('name', '').lower() or
                   search_lower in p.get('manufacturer', '').lower()
            ]
        
        limited_products = all_products[:limit]
        
        return {
            "success": True,
            "products": limited_products,
            "total_found": len(all_products),
            "returned": len(limited_products),
            "search": search if search else None,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ שגיאה: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e), "products": []}
        )

@app.get("/update-all")
async def update_all(background_tasks: BackgroundTasks):
    updated_sources = []
    for source_id in SOURCES.keys():
        background_tasks.add_task(fetch_and_process, source_id)
        updated_sources.append(source_id)
    
    return {
        "success": True,
        "message": "⏳ מעדכן ברקע...",
        "sources": updated_sources,
        "count": len(updated_sources),
        "note": "בדוק /status אחרי דקה"
    }

@app.get("/status")
async def status():
    cache_status = processor.get_cache_status()
    
    sources_info = {}
    for source_id in SOURCES.keys():
        if source_id in cache_status:
            sources_info[source_id] = {
                **cache_status[source_id],
                'url': SOURCES[source_id]
            }
        else:
            sources_info[source_id] = {
                'status': '⚠️ אין נתונים',
                'url': SOURCES[source_id]
            }
    
    return {
        "system": {"status": "🟢 פעיל", "time": datetime.now().isoformat()},
        "sources": sources_info,
        "cache": {"location": processor.cache_dir, "files": len(cache_status)}
    }

async def fetch_and_process(source_id: str):
    try:
        url = SOURCES.get(source_id)
        if not url:
            print(f"❌ מקור לא קיים: {source_id}")
            return []
        
        print(f"📡 מוריד מ-{source_id}...")
        
        # שלב 1: הורדת המטא-דאטה
        response = await download_with_retry(url, max_retries=3)
        
        if response is None:
            print(f"❌ הורדה נכשלה עבור {source_id}")
            return []
        
        # שלב 2: בדיקה אם זה JSON עם SPath
        try:
            meta_data = response.json()
            if isinstance(meta_data, list) and len(meta_data) > 0:
                if 'SPath' in meta_data[0]:
                    # זה kingstore - צריך לבנות את ה-URL המלא
                    base_path = meta_data[0]['SPath']
                    # חלץ את שם הקובץ מה-URL המקורי
                    filename = url.split('File=')[-1]
                    real_url = base_path + filename
                    print(f"🔗 בונה URL: {base_path} + {filename}")
                    print(f"🔗 URL מלא: {real_url}")
                    
                    # הורדת הקובץ האמיתי
                    real_response = await download_with_retry(real_url, max_retries=3)
                    if real_response is None:
                        print(f"❌ הורדת הקובץ האמיתי נכשלה")
                        return []
                    
                    response = real_response
                    print(f"✅ הורדה הושלמה ({len(response.content)} bytes)")
        except:
            # לא JSON או לא kingstore - נמשיך עם התוכן המקורי
            pass
        
        print(f"✅ הורדה הושלמה ({len(response.content)} bytes)")
        
        # עיבוד
        products = processor.process_gz(response.content)
        
        if products:
            processor.save_to_cache(products, source_id)
            print(f"✅ {source_id}: {len(products)} מוצרים עודכנו")
        else:
            print(f"⚠️ {source_id}: לא נמצאו מוצרים")
        
        return products
        
    except Exception as e:
        print(f"❌ שגיאה ב-{source_id}: {e}")
        import traceback
        traceback.print_exc()
        return []

async def download_with_retry(url: str, max_retries: int = 3):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for attempt in range(max_retries):
        try:
            print(f"📥 ניסיון {attempt + 1}/{max_retries}...")
            
            response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
            response.raise_for_status()
            return response
            
        except requests.RequestException as e:
            print(f"⚠️ ניסיון {attempt + 1} נכשל: {e}")
            
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"⏳ ממתין {wait_time} שניות...")
                await asyncio.sleep(wait_time)
            else:
                print(f"❌ כל הניסיונות נכשלו")
                return None
    
    return None

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print("🚀 SmartMarket API Server")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")