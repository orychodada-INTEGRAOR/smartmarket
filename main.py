from fastapi import FastAPI
import requests
import gzip
import xml.etree.ElementTree as ET
import json
import os

app = FastAPI()

PROMO_URL = "https://kingstore.binaprojects.com/Download.aspx?File=Promo7290058108879-340-202602191114.gz"

def read_file_smart(filename):
    """קורא gz, XML, או JSON - חכם!"""
    try:
        # נסה gz קודם
        with gzip.open(filename, 'rt', encoding='utf-8') as f:
            return f.read()
    except:
        # אם לא gz - קרא רגיל
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return None

@app.get("/update-promo")
async def update_promo():
    try:
        # 1. הורד קובץ
        r = requests.get(PROMO_URL)
        with open("promo.gz", "wb") as f:
            f.write(r.content)
        
        # 2. קרא חכם (gz/XML/JSON)
        content = read_file_smart("promo.gz")
        if not content:
            return {"status": "❌ קובץ ריק"}
        
        # 3. נסה XML
        try:
            root = ET.fromstring(content)
            promotions = []
            
            for promotion in root.findall('.//Promotion'):
                promo_data = {
                    'תיאור': promotion.find('PromotionDescription').text or '',
                    'תאריך': promotion.find('PromotionUpdateDate').text or '',
                    'מחיר': promotion.find('DiscountedPrice').text or '',
                    'מינימום': promotion.find('MinQty').text or '',
                    'מוצרים': [item.find('ItemCode').text for item in promotion.findall('.//Item') if item.find('ItemCode')]
                }
                promotions.append(promo_data)
            
            # שמור JSON
            with open("promotions.json", "w", encoding='utf-8') as f:
                json.dump(promotions, f, ensure_ascii=False, indent=2)
            
            return {"status": "✅ מבצעים!", "מבצעים": len(promotions)}
            
        except:
            # אם לא XML - החזר תוכן גולמי
            return {"status": "ℹ️ לא XML", "תוכן": content[:500]}
            
    except Exception as e:
        return {"status": "❌ שגיאה", "error": str(e)}

@app.get("/api/promo")
async def get_promo(search: str = ""):
    try:
        with open("promotions.json", "r", encoding='utf-8') as f:
            promos = json.load(f)
        if search:
            promos = [p for p in promos if search in str(p.get('תיאור', ''))]
        return promos[:10]
    except:
        return []

@app.get("/")
async def root():
    return {"SmartMarket": "קרא /update-promo"}
