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

# יצירת האפליקציה
app = FastAPI(
    title="SmartMarket API",
    description="API לניהול מחירי קמעונאות בזמן אמת",
    version="1.0.0"
)

# יצירת המעבד
processor = DataProcessor()

# הגדרת CORS (כדי שהאפליקציה תוכל לגשת)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # בייצור - הגבל רק לדומיין שלך
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================================
# הגדרת מקורות נתונים
# ========================================
# כאן תוסיף את ה-URLs של המחירונים
SOURCES = {
    'kingstore': 'https://kingstore.binaprojects.com/Download.aspx?File=Price7290058108879-340-202602190910.gz',
}

# ========================================
# נקודות קצה (Endpoints)
# ========================================

@app.get("/")
async def root():
    """דף הבית - מידע בסיסי"""
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
async def get_products(
    search: str = "",
    source: str = "all",
    limit: int = 100
):
    """
    מחזיר רשימת מוצרים
    
    Parameters:
        search: טקסט לחיפוש (אופציונלי)
        source: מקור ספציפי או 'all' (ברירת מחדל)
        limit: מספר מוצרים מקסימלי (ברירת מחדל: 100)
    
    Example:
        /api/products?search=חלב&limit=20
    """
    try:
        all_products = []
        
        # קביעת אילו מקורות לטעון
        if source == "all":
            sources_to_load = SOURCES.keys()
        elif source in SOURCES:
            sources_to_load = [source]
        else:
            raise HTTPException(status_code=400, detail=f"מקור לא קיים: {source}")
        
        # טעינה מכל המקורות
        for src in sources_to_load:
            # נסה cache קודם (טרי עד שעה)
            products = processor.load_from_cache(src, max_age_hours=1)
            
            if products is None:
                # אין cache או ישן - נסה לעדכן
                print(f"📥 מוריד נתונים טריים עבור {src}...")
                products = await fetch_and_process(src)
            
            if products:
                all_products.extend(products)
        
        # חיפוש אם יש
        if search:
            search_lower = search.lower()
            all_products = [
                p for p in all_products 
                if search_lower in p.get('name', '').lower() or
                   search_lower in p.get('manufacturer', '').lower()
            ]
        
        # הגבלה
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
            content={
                "success": False,
                "error": str(e),
                "products": []
            }
        )

@app.get("/update-all")
async def update_all(background_tasks: BackgroundTasks):
    """
    מעדכן את כל מקורות הנתונים ברקע
    
    זה לא חוסם - מחזיר תשובה מיד ומעדכן ברקע
    """
    # הוספת משימות רקע
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

@app.get("/update/{source_id}")
async def update_source(source_id: str, background_tasks: BackgroundTasks):
    """עדכון מקור בודד"""
    if source_id not in SOURCES:
        raise HTTPException(status_code=404, detail=f"מקור לא קיים: {source_id}")
    
    background_tasks.add_task(fetch_and_process, source_id)
    
    return {
        "success": True,
        "message": f"⏳ מעדכן {source_id} ברקע...",
        "source": source_id
    }

@app.get("/status")
async def status():
    """
    מחזיר סטטוס של כל המערכת
    
    כולל מידע על cache, מקורות, ועדכונים אחרונים
    """
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
        "system": {
            "status": "🟢 פעיל",
            "time": datetime.now().isoformat()
        },
        "sources": sources_info,
        "cache": {
            "location": processor.cache_dir,
            "files": len(cache_status)
        }
    }

# ========================================
# פונקציות עזר
# ========================================

async def fetch_and_process(source_id: str):
    """
    מוריד ומעבד מקור נתונים בודד
    
    Args:
        source_id: מזהה המקור
        
    Returns:
        list: רשימת מוצרים או רשימה ריקה אם נכשל
    """
    try:
        url = SOURCES.get(source_id)
        if not url:
            print(f"❌ מקור לא קיים: {source_id}")
            return []
        
        print(f"📡 מוריד מ-{source_id}...")
        
        # הורדה עם retry
        response = await download_with_retry(url, max_retries=3)
        
        if response is None:
            print(f"❌ הורדה נכשלה עבור {source_id}")
            return []
        
        print(f"✅ הורדה הושלמה ({len(response.content)} bytes)")
        
        # עיבוד
        products = processor.process_gz(response.content)
        
        if products:
            # שמירה ל-cache
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
    """
    מוריד קובץ עם ניסיונות חוזרים
    
    Args:
        url: כתובת ההורדה
        max_retries: מספר ניסיונות מקסימלי
        
    Returns:
        Response object או None
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for attempt in range(max_retries):
        try:
            print(f"📥 ניסיון {attempt + 1}/{max_retries}...")
            
            response = requests.get(
                url,
                headers=headers,
                timeout=30,
                allow_redirects=True
            )
            
            response.raise_for_status()  # יזרוק שגיאה אם לא 200
            return response
            
        except requests.RequestException as e:
            print(f"⚠️ ניסיון {attempt + 1} נכשל: {e}")
            
            if attempt < max_retries - 1:
                # המתנה לפני ניסיון הבא (exponential backoff)
                wait_time = 2 ** attempt
                print(f"⏳ ממתין {wait_time} שניות...")
                await asyncio.sleep(wait_time)
            else:
                print(f"❌ כל הניסיונות נכשלו")
                return None
    
    return None

# ========================================
# הפעלה
# ========================================

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.environ.get("PORT", 8000))
    
    print("=" * 60)
    print("🚀 SmartMarket API Server")
    print("=" * 60)
    print(f"🌐 Port: {port}")
    print(f"📂 Cache: {processor.cache_dir}")
    print(f"🔗 Sources: {len(SOURCES)}")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
