import requests
import gzip
import xml.etree.ElementTree as ET
from io import BytesIO

class DataProcessor:
    def get_real_data_streaming(self, url: str):
        # הורדת הקובץ בזרם (Stream) כדי לא לחנוק את השרת
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # פתיחת ה-GZIP בזרם
        with gzip.GzipFile(fileobj=response.raw) as gz:
            products = []
            # שימוש ב-iterparse מאפשר לעבור על ה-XML פריט פריט
            context = ET.iterparse(gz, events=("end",))
            
            count = 0
            for event, elem in context:
                if elem.tag == "Item":
                    # שליפת הנתונים מהפריט הנוכחי בלבד
                    product = {
                        "code": elem.findtext("ItemCode"),
                        "name": elem.findtext("ItemName"),
                        "price": elem.findtext("ItemPrice"),
                        "category": elem.findtext("CategoryName") or "כללי",
                        "store": "שופרסל"
                    }
                    products.append(product)
                    count += 1
                    
                    # מנקים את הזיכרון מהאלמנט שסיימנו לעבוד עליו
                    elem.clear()
                    
                    # הגבלה ל-100 מוצרים כדי שהגיליון וה-API יגיבו מהר
                    if count >= 100:
                        break
            
            return products