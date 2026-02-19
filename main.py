from fastapi import FastAPI
import requests
import gzip
import xml.etree.ElementTree as ET
import json
import os

app = FastAPI()

@app.get("/update-all")
async def update_all():
    try:
        # 1. הורד רשימת קישורים
        list_url = "https://kingstore.binaprojects.com/Download.aspx?File=Promo7290058108879-340-202602191114.gz"
        r = requests.get(list_url)
        with open("list.json", "wb") as f:
            f.write(r.content)
        
        # 2. קרא רשימת קישורים
        content = ""
        try:
            with gzip.open("list.json", 'rt') as f:
                content = f.read()
        except:
            with open("list.json", 'r') as f:
                content = f.read()
        
        links = json.loads(content)
        all_products = []
        
        # 3. הורד כל קובץ ברשימה
        for link_data in links:
            spath = link_data.get('SPath', '')
            if 'kingstore.binaprojects.com/Download/' in spath:
                print(f"📥 מוריד: {spath}")
                try:
                    file_r = requests.get(spath)
                    filename = spath.split('/')[-1]
                    with open(filename, "wb") as f:
                        f.write(file_r.content)
                    
                    # 4. פרס XML
                    xml_content = ""
                    try:
                        with gzip.open(filename, 'rt') as f:
                            xml_content = f.read()
                    except:
                        with open(filename, 'r') as f:
                            xml_content = f.read()
                    
                    root = ET.fromstring(xml_content)
                    for item in root.findall('.//Item'):
                        product = {
                            'קוד': item.find('ItemCode').text if item.find('ItemCode') else '',
                            'שם': item.find('ItemNm').text if item.find('ItemNm') else '',
                            'מחיר': item.find('ItemPrice').text if item.find('ItemPrice') else ''
                        }
                        if product['שם']:  # רק מוצרים עם שם
                            all_products.append(product)
                            
                except Exception as file_error:
                    print(f"❌ שגיאה בקובץ {spath}: {file_error}")
                    continue
        
        # 5. שמור הכל
        with open("products.json", "w", encoding='utf-8') as f:
            json.dump(all_products, f, ensure_ascii=False, indent=2)
        
        return {
            "status": "✅ הושלם!", 
            "מוצרים": len(all_products),
            "קישורים": len(links)
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
    return {"SmartMarket": "קרא /update-all"}
