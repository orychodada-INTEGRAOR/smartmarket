from fastapi import FastAPI
import requests
import gzip
import xml.etree.ElementTree as ET
import json
import os

app = FastAPI()

PROMO_URL = "https://kingstore.binaprojects.com/Download.aspx?File=Promo7290058108879-340-202602191114.gz"

@app.get("/update-promo")
async def update_promo():
    try:
        # 1. הורד מבצעים
        print("📥 מוריד מבצעים...")
        r = requests.get(PROMO_URL)
        with open("promo.gz", "wb") as f:
            f.write(r.content)
        
        # 2. פתח XML
        with gzip.open("promo.gz", 'rt', encoding='utf-8') as f:
            xml_content = f.read()
        
        # 3. חלץ מבצעים
        root = ET.fromstring(xml_content)
        promotions = []
        
        for promotion in root.findall('.//Promotion'):
            promo_data = {
                'תיאור': promotion.find('PromotionDescription').text if promotion.find('PromotionDescription') else '',
                'תאריך': promotion.find('PromotionUpdateDate').text if promotion.find('PromotionUpdateDate') else '',
                'מחיר_מבצע': promotion.find('DiscountedPrice').text if promotion.find('DiscountedPrice') else '',
                'מינימום_כמות': promotion.find('MinQty').text if promotion.find('MinQty') else '',
                'מוצרים': []
            }
            
            # חלץ קודי מוצרים
            for item in promotion.findall('.//PromotionItems/Item'):
                code = item.find('ItemCode').text if item.find('ItemCode') else ''
                if code:
                    promo_data['מוצרים'].append(code)
            
            promotions.append(promo_data)
        
        # שמור JSON
        with open("promotions.json", "w", encoding='utf-8') as f:
            json.dump(promotions, f, ensure_ascii=False, indent=2)
        
        return {"status": "✅ מבצעים עודכנו!", "מבצעים": len(promotions)}
        
    except Exception as e:
        return {"status": "❌ שגיאה", "error": str(e)}

@app.get("/api/promo")
async def get_promo(search: str = ""):
    try:
        with open("promotions.json", "r", encoding='utf-8') as f:
            promos = json.load(f)
        
        if search:
            promos = [p for p in promos if search.lower() in str(p.get('תיאור', '')).lower()]
        
        return promos[:10]
    except:
        return []

@app.get("/")
async def root():
    return {"SmartMarket": "מבצעים! קרא /update-promo"}
