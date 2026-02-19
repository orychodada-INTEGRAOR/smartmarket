from fastapi import FastAPI
import requests
import gzip
import xml.etree.ElementTree as ET
import json
import os
import re

app = FastAPI()

MAIN_PAGE = "https://kingstore.binaprojects.com/Main.aspx"

@app.get("/scan-all")
async def scan_all():
    try:
        # 1. סרוק דף ראשי - חפש כל קבצי .gz
        print("🔍 סורק kingstore...")
        r = requests.get(MAIN_PAGE)
        page_content = r.text
        
        # חפש קישורים ל-Price*.gz
        price_links = re.findall(r'href=[\'"]Download\.aspx\?File=Price[^\'"]*gz[\'"]', page_content)
        promo_links = re.findall(r'href=[\'"]Download\.aspx\?File=Promo[^\'"]*gz[\'"]', page_content)
        
        all_links = list(set(price_links + promo_links))
        products = []
        
        # 2. הורד + פרס כל קובץ
        for link in all_links[:5]:  # 5 קבצים מקסימום
            full_url = f"https://kingstore.binaprojects.com/{link.split('href=')[1].strip('\"')}"
            print(f"📥 מנסה: {full_url}")
            
            try:
                file_r = requests.get(full_url, timeout=10)
                if file_r.status_code == 200:
                    filename = full_url.split('File=')[-1].replace('.gz', '.txt')
                    with open(filename, "wb") as f:
                        f.write(file_r.content)
                    
                    # 3. נסה לקרוא כXML
                    content = ""
                    try:
                        with gzip.open(filename, 'rt', encoding='utf-8') as f:
                            content = f.read()
                    except:
                        with open(filename, 'r', encoding='utf-8') as f:
                            content = f.read()
                    
                    # 4. בדוק אם XML תקין
                    if content.strip().startswith('<'):
                        root = ET.fromstring(content)
                        for item in root.findall('.//Item'):
                            name = item.find('ItemNm')
                            price = item.find('ItemPrice')
                            if name is not None and price is not None:
                                products.append({
                                    'שם': name.text or '',
                                    'מחיר': price.text or '',
                                    'מקור': filename
                                })
                    else:
                        print(f"ℹ️ {filename}: לא XML")
                        
            except Exception as e:
                print(f"❌ {full_url}: {e}")
                continue
        
        # 5. שמור
        with open("products.json", "w", encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        
        return {
            "status": "✅ סריקה הושלמה!",
            "קישורים_נמצאו": len(all_links),
            "מוצרים": len(products),
            "דוגמאות": products[:3]
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
    return {"SmartMarket": "קרא /scan-all - סריקת אתר"}
