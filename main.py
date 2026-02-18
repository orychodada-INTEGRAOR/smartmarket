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
    url = "https://example-shufersal.com/prices.xml.gz"  
    # או URL אמיתי שתמצא באתר הרשת
    
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
    uvicorn.run(app, host="0.0.0.1", port=8000)
