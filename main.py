from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
import re
import gzip
import xml.etree.ElementTree as ET
import json
import os

app = FastAPI()

@app.get("/scan-pro")
async def scan_pro():
    # 1. סרוק Main.aspx - כל הקישורים
    r = requests.get("https://kingstore.binaprojects.com/Main.aspx")
    soup = BeautifulSoup(r.text, 'html.parser')
    
    links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if 'Download.aspx?File=' in href and ('.gz' in href or 'Price' in href or 'Promo' in href):
            url = f"https://kingstore.binaprojects.com/{href}" if not href.startswith('http') else href
            links.append(url)
    
    products = []
    
    # 2. נסה כל קישור
    for url in links[:8]:
        try:
            print(f"📥 {url}")
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                # שמור + קרא
                name = url.split('File=')[-1].split('&')[0].replace('.gz','')
                with open(f"{name}.gz", "wb") as f:
                    f.write(resp.content)
                
                # XML parsing
                content = ""
                try:
                    with gzip.open(f"{name}.gz", 'rt', encoding='utf-8') as f:
                        content = f.read()
                except:
                    with open(f"{name}.gz", 'r', encoding='utf-8') as f:
                        content = f.read()
                
                if content.startswith('<'):
                    root = ET.fromstring(content)
                    for item in root.findall('.//Item')[:30]:
                        name_el = item.find('ItemNm')
                        price_el = item.find('ItemPrice')
                        if name_el is not None and price_el is not None:
                            products.append({
                                'שם': name_el.text or '',
                                'מחיר': price_el.text or '',
                                'קוד': item.find('ItemCode').text or '',
                                'מקור': name
                            })
        except:
            continue
    
    # שמור JSON
    with open("products.json", "w", encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False)
    
    return {
        "status": "✅ סריקה מקצועית!",
        "קישורים": len(links),
        "מוצרים": len(products),
        "דוגמאות": products[:5]
    }

@app.get("/api/products")
async def api_products(search: str = ""):
    try:
        with open("products.json", "r", encoding='utf-8') as f:
            all_products = json.load(f)
        if search:
            results = [p for p in all_products if search.lower() in str(p.get('שם','')).lower()]
        else:
            results = all_products
        return results[:30]
    except:
        return []

@app.get("/")
async def root():
    return {"SmartMarket": "מוכן! /scan-pro → /api/products?search=חלב"}
