from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from data_processor import DataProcessor
import os

app = FastAPI(title="SmartMarket API")

# הגדרות CORS לחיבור Glide ו-Google Sheets
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

processor = DataProcessor()

@app.get("/")
async def root():
    return {"message": "SmartMarket API חי ובועט! 🚀"}

@app.get("/api/products")
async def get_products():
    """שליפת מחירים אמיתיים משופרסל ל-Google Sheets ו-Glide"""
    
    # URL מעודכן להיום (18.02.2026) של סניף שופרסל
    url = "https://prices.shufersal.co.il/FileObject/DownloadFile?FileName=Price7290027600007-001-202602181100.gz&FileType=gz"
    
    try:
        # כאן אנחנו מפעילים את פונקציית ה-Streaming שחוסכת זיכרון
        products = processor.get_real_data_streaming(url)
        
        return {
            "status": "success",
            "updated": "2026-02-18",
            "source": "שופרסל סניף 001",
            "products": products  # מחזיר את 100 המוצרים שהגדרנו במעבד
        }
    except Exception as e:
        # אם יש בעיה בקישור של שופרסל, השרת לא יקרוס ויחזיר נתוני גיבוי
        return {
            "status": "partial_success",
            "message": f"סריקה נכשלה: {str(e)}",
            "products": [
                {"name": "חלב תנובה 1% (גיבוי)", "price": "5.87", "store": "שופרסל"},
                {"name": "לחם קליה (גיבוי)", "price": "4.99", "store": "שופרסל"}
            ]
        }

if __name__ == "__main__":
    import uvicorn
    # הגדרות קריטיות ל-Railway
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)