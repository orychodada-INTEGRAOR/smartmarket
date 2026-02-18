import requests
import gzip
from io import BytesIO
from lxml import etree
import json
from typing import List, Dict, Any

class DataProcessor:
    def get_real_data_streaming(self, url: str) -> List[Dict[str, Any]]:
        """קורא XML ענק שורה אחר שורה - לא קורס על 512MB"""
        
        # הורדת הקובץ
        print(f"מושך נתונים מ-{url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # פתיחת GZIP ישירות ל-streaming
        gz_stream = gzip.GzipFile(fileobj=BytesIO(response.content))
        
        # STREAMING PARSER - הקסם שחוסך זיכרון
        context = etree.iterparse(
            gz_stream, 
            events=('end',), 
            tag='Item',  # רק אלמנטים בשם Item
            huge_tree=True
        )
        
        products = []
        for event, elem in context:
            try:
                # חילוץ נתונים ממוצר בודד (זיכרון מינימלי)
                product = {
                    "code": elem.findtext("ItemCode") or "N/A",
                    "name": elem.findtext("ItemName") or "ללא שם",
                    "price": float(elem.findtext("ItemPrice") or 0),
                    "category": elem.findtext("Category") or "כללי",
                    "store": elem.get("StoreId", "לא ידוע")  # אם יש
                }
                
                # סינון מוצרים תקינים בלבד
                if product["name"] != "ללא שם" and product["price"] > 0:
                    products.append(product)
                
                # 🔥 משחרר זיכרון מיד אחרי שימוש
                elem.clear()
                while elem.getprevious() is not None:
                    del elem.getparent()[0]
                    
            except Exception as e:
                print(f"שגיאה במוצר: {e}")
                elem.clear()
                continue
        
        print(f"סיים! נמצאו {len(products)} מוצרים")
        return products[:1000]  # מגביל ל-1000 לבדיקה (Render Free)
