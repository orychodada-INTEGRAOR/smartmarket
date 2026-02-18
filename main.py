from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from data_processor import DataProcessor
import os

app = FastAPI(title="SmartMarket API")

# הגדרות CORS לחיבור Glide
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
    """החזרת מוצרים יציבה ל-Glide"""
    # נתוני בדיקה יציבים כדי לוודא שהחיבור עובד
    stable_products = [
        {"code": "7290100080003", "name": "חלב תנובה 1%", "price": 5.87, "category": "חלב", "store": "שופרסל"},
        {"code": "7296071000141", "name": "לחם קליה", "price": 4.99, "category": "מאפים", "store": "שופרסל"},
        {"code": "7290100136618", "name": "ביצים 10 יח'", "price": 12.90, "category": "ביצים", "store": "רמי לוי"}
    ]
    
    return {
        "status": "success",
        "updated": "2026-02-18",
        "products": stable_products  # זה המפתח ש-Glide מחפש
    }

if __name__ == "__main__":
    import uvicorn
    # חובה ל-Railway
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)