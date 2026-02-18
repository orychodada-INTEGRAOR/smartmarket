from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from data_processor import DataProcessor
import logging

# הגדרת לוגים למעקב ב-Railway
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# הגדרת CORS כדי ש-Google Sheets ו-Glide יוכלו למשוך נתונים
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "SmartMarket API is Live", "status": "Online"}

@app.get("/api/products")
def get_products():
    # הלינק המעודכן שסיפקת (תקף ל-18/02/2026 שעה 17:00)
    url = "https://prices.shufersal.co.il/FileObject/DownloadFile?FileName=Price7290027600007-003-202602181800.gz&FileType=gz"
    
    processor = DataProcessor()
    try:
        logger.info(f"Attempting to fetch data from: {url}")
        products = processor.get_real_data_streaming(url)
        return {
            "status": "success",
            "source": "Shufersal Real-time",
            "count": len(products),
            "products": products
        }
    except Exception as e:
        logger.error(f"Error fetching real data: {e}")
        # מנגנון גיבוי (Fallback) כדי שהאפליקציה לא תציג דף ריק
        return {
            "status": "partial_success",
            "message": f"סריקה נכשלה: {str(e)}",
            "products": [
                {"name": "חלב תנובה 1% (גיבוי)", "price": "5.87", "store": "שופרסל"},
                {"name": "לחם קליה (גיבוי)", "price": "4.99", "store": "שופרסל"},
                {"name": "גבינה לבנה 5% (גיבוי)", "price": "5.20", "store": "שופרסל"}
            ]
        }

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)