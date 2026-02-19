from fastapi import FastAPI
import requests
import gzip
import xml.etree.ElementTree as ET
import json
import os

app = FastAPI()

# הקובץ החי שנתת!
PRICE_URL = "https://kingstore.binaprojects.com/Download.aspx?File=Price7290058108879-340-202602191110.gz"

@app.get("/update-prices")
async def update_prices():
    try:
        print("📥 מוריד מחירון...")
        r = requests.get(PRICE_URL)
        with open("price.gz", "wb") as f:
            f.write(r.content)
        
        # קרא חכם (gz או רגיל)
        content = ""
        try:
            with gzip.open("price.gz", 'rt', encoding='utf-8') as f:
                content = f.read()
        except:
            with open("price.gz", 'r', encoding='utf-8') as f:
                content = f.read()
        
        # פרס XML
        root = ET.fromstring(content)
        products = []
        
        print(f"מטפל ב-{len(root.findall('.//Item'))} מוצרים...")
        
        for item in root.findall('.//Item'):
            product = {
                'קוד': item.find('ItemCode').text if item.find('ItemCode') else '',
                'שם': item.find('ItemNm').text if item.find('ItemNm') else '',
                'יצרן': item.find('ManufacturerName').text if item.find('ManufacturerName') else '',
                'מחיר': item.find('ItemPrice').text if item.find('ItemPrice') else '',
                'יחידה': item.find('UnitOfMeasure').text if item.find('UnitOfMeasure') else ''
            }
            # רק מוצרים עם שם
            if product['שם']:
                products.append(product)
        
        # שמור JSON
        with open("products.json", "w", encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        
        return {
            "status": "✅ מחירון עודכן!", 
            "מוצרים": len(products),
            "דוגמה": products[:3] if products else []
        }
        
    except Exception as e:
        return {"status": "❌ שגיאה", "error": str(e)}

@app.get("/api/products")
async def get_products(search: str = ""):
    try:
        with open("products.json", "r", encoding='utf-8') as f:
            products = json.load(f)
        if search:
            products = [p for p in products if search.lower() in str(p.get('שם', '')).lower()]
        return products[:50]
    except:
        return []

@app.get("/")
async def root():
    return {"SmartMarket": "קרא /update-prices"}
