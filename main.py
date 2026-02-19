from fastapi import FastAPI
import requests
import re
import gzip
import xml.etree.ElementTree as ET
import json
import os
from bs4 import BeautifulSoup

app = FastAPI()

MAIN_URL = "https://kingstore.binaprojects.com/Main.aspx"

@app.get("/scan-all")
async def scan_all():
    try:
        # 1. סרוק את הדף הראשי
        r = requests.get(MAIN_URL)
        soup = BeautifulSoup(r.text, 'html.parser')
        all_links = []
        
        # 2. חפש כל קישור עם Download.aspx?File=
        for link in soup.find_all('a', href=True):
            href = link['href']
            if 'Download.aspx?File=' in href and '.gz' in href:
                full_url = href if href.startswith('http') else f"https://kingstore.binaprojects.com/{href}"
                all_links.append(full_url)
        
        print(f"📡 נמצאו {len(all_links)} קישורים")
        
        products = []
        for i, url in enumerate(all_links[:10]):  # 10 קבצים מקס
            print(f"📥 {i+1}/10: {url}")
            
            try:
                file_r = requests.get(url, timeout=15)
                if file_r.status_code == 200:
                    filename = f"file_{i}.gz"
                    with open(filename, "wb") as f:
                        f.write(file_r.content)
                    
                    # קרא תוכן
                    content = ""
                    try:
                        with gzip.open(filename, 'rt', encoding='utf-8') as f:
                            content = f.read()
                    except:
                        with open(filename, 'r', encoding='utf-8') as f:
                            content = f.read()
                    
                    # אם XML → חלץ מוצרים
                    if content.strip().startswith('<'):
                        root = ET.fromstring(content)
                        items = root.findall('.//Item')
                        print(f"✅ {filename}: {len(items)} מוצרים")
                        
                        for item in items[:50]:  # 50 מוצרים מקס לקובץ
                            name = item.find('ItemNm')
                            price = item.find('ItemPrice')
                            if name is not None and price is not None:
                                products.append({
                                    'שם': name.text or '',
                                    'מחיר': price.text or '',
                                    'מקור': url
                                })
                        
            except Exception as e:
                print(f"❌ {url}: {e}")
                continue
        
        # שמור
        with open("products.json", "w", encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
        
        return {
            "status": "✅ סריקה הושלמה!",
            "קישורים": len(all_links),
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
        return products[:20]
    except:
        return []

@app.get("/")
async def root():
    return {"SmartMarket": "קרא /scan-all (משופר עם BeautifulSoup)"}
