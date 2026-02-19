from fastapi import FastAPI
import requests
import subprocess
import pandas as pd
import json
import os
from datetime import datetime

app = FastAPI()

KINGSTORE_URL = "https://kingstore.binaprojects.com/Download.aspx?File=Price7290058108879-340-202602190910.gz"

@app.get("/update-prices")
async def update_prices():
    try:
        # 1. הורד קובץ gz
        print("📥 מוריד קובץ...")
        r = requests.get(KINGSTORE_URL)
        with open("temp.gz", "wb") as f:
            f.write(r.content)
        
        # 2. הרץ price_converter
        print("🔄 ממיר לאקסל...")
        subprocess.run(["python", "price_converter.py", "temp.gz"])
        
        # 3. חפש אקסל שנוצר
        excel_files = [f for f in os.listdir('.') if f.endswith('_מחירון.xlsx')]
        if excel_files:
            excel_file = excel_files[0]
            df = pd.read_excel(excel_file)
            products = df[['קוד מוצר', 'שם המוצר', 'מחיר (₪)']].to_dict('records')
            
            with open("products.json", "w", encoding='utf-8') as f:
                json.dump(products, f, ensure_ascii=False, indent=2)
            
            return {"status": "✅ עודכן!", "מוצרים": len(products), "קובץ": excel_file}
        else:
            return {"status": "❌ לא נמצא אקסל", "קבצים": os.listdir('.')}
            
    except Exception as e:
        return {"status": "❌ שגיאה", "error": str(e)}

@app.get("/api/products")
async def get_products(search: str = ""):
    try:
        with open("products.json", "r", encoding='utf-8') as f:
            products = json.load(f)
        if search:
            products = [p for p in products if search.lower() in str(p.get('שם המוצר', '')).lower()]
        return products[:50]
    except:
        return []

@app.get("/")
async def root():
    return {"SmartMarket": "מוכן! קרא /update-prices"}
