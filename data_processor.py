import requests
import gzip
import xml.etree.ElementTree as ET
from io import BytesIO

class DataProcessor:
    def get_real_data_streaming(self, url: str):
        # הגדרת "זהות" של דפדפן כדי לעקוף חסימות (User-Agent)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7',
        }

        try:
            # בקשה עם Headers ו-Timeout של 30 שניות
            response = requests.get(url, stream=True, headers=headers, timeout=30)
            response.raise_for_status()

            # פתיחת ה-GZIP בזרם
            with gzip.GzipFile(fileobj=response.raw) as gz:
                products = []
                # סריקה פריט-פריט לחסכון בזיכרון
                context = ET.iterparse(gz, events=("end",))
                
                count = 0
                for event, elem in context:
                    if elem.tag == "Item":
                        product = {
                            "code": elem.findtext("ItemCode") or "N/A",
                            "name": elem.findtext("ItemName") or "ללא שם",
                            "price": elem.findtext("ItemPrice") or "0",
                            "category": elem.findtext("CategoryName") or "כללי",
                            "store": "שופרסל"
                        }
                        products.append(product)
                        count += 1
                        
                        # ניקוי זיכרון מיידי
                        elem.clear()
                        
                        # הגבלה ל-100 מוצרים ראשונים ליציבות מקסימלית ב-Railway
                        if count >= 100:
                            break
                
                return products

        except Exception as e:
            # אם גם זה נכשל, נזרוק את השגיאה ל-main כדי שיפעיל את הגיבוי
            raise Exception(f"Failed to fetch data: {str(e)}")