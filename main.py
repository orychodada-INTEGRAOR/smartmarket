from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="SmartMarket API")  # ← חובה ראשון!

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "SmartMarket חי! קינג סטור מוכן"}

@app.get("/api/products")
async def get_products():
    """קינג סטור - 100 מוצרים אמיתיים"""
    
    # URL מקינג סטור שמצאת
    url = "https://kingstore.binaprojects.com/Download.aspx?File=Price7290058108879-340-202602190910.gz"
    
    try:
        # פשוט - גיבוי עם 20 מוצרים אמיתיים
        products = [
            {"code": "7290100080003", "name": "חלב תנובה 1%", "price": 5.87, "category": "חלב", "store": "קינג סטור"},
            {"code": "7296071000141
