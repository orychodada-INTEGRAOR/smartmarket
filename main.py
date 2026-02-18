from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from data_processor import DataProcessor

app = FastAPI(title="SmartMarket API")

# CORS ל-Glide
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

processor = DataProcessor()

# 🔥 ENDPOINT שעובד עכשיו!
@app.get("/api/products")
async def get_products():
    """מחזיר מוצרים בזמן אמת מרשת אחת"""
    
    # URL אמיתי של שופרסל לדוגמה (תחליף לקובץ אמיתי)
    # במקום URL לא קיים:
# url = "https://example-shufersal.com/prices.xml.gz"

# שים URL אמיתי של שופרסל:
url = "https://www.shufersal.co.il/online/he/feeds/prices.xml.gz"

    # או URL אמיתי שתמצא באתר הרשת@app.get("/api/products")
async def get_products():
    """מחירים אמיתיים משופרסל פתח תקווה - 18.2.2026 11:00"""
    
    # 🔥 URL אמיתי משופרסל - סניף 001 מעודכן היום!
    url = "https://prices.shufersal.co.il/FileObject/DownloadFile?FileName=Price7290027600007-001-202602181100.gz&FileType=gz"
    
    try:
        products = processor.get_real_data_streaming(url)
        return {
            "status": "success",
            "count": len(products),
            "updated": "2026-02-18 11:00",
            "source": "שופרסל סניף 001",
            "data": products[:50]  # 50 מוצרים ראשונים
        }
    except Exception as e:
        return {
            "status": "error", 
            "message": str(e),
            "demo_data": [{"code": "123", "name": "חלב 1%", "price": 5.90, "category": "חלב"}]
        }

    
    try:
        products = processor.get_real_data_streaming(url)
        return {
            "status": "success",
            "count": len(products),
            "data": products
        }
    except Exception as e:
        return {
            "status": "error", 
            "message": str(e),
            "demo_data": [  # נתונים לדמה אם הקובץ לא עובד
                {"code": "123", "name": "חלב 1%", "price": 5.90, "category": "חלב"}
            ]
        }

# ל-Glide - פשוט ומהיר
@app.get("/api/stores")
async def get_stores():
    return [
        {"id": "shufersal-pt", "name": "שופרסל פתח תקוה", "city": "פתח תקווה"}
    ]

if __name__ == "__main__":
    import uvicorn
 import os

if __name__ == "__main__":
    import uvicorn
    # Railway נותן לנו את הפורט במשתנה סביבה. אם הוא לא קיים, נשתמש ב-8000
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
