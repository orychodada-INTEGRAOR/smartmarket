import requests
import gzip
import xml.etree.ElementTree as ET
from io import BytesIO

class DataProcessor:
    def get_real_data_streaming(self, url: str):
        # מורידים את הקובץ כזרם (Stream) - לא תופס זיכרון
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # פתיחת ה-GZIP תוך כדי תנועה
        with gzip.GzipFile(fileobj=response.raw) as gz:
            products = []
            # iterparse סורק את ה-XML פריט אחרי פריט בלי לטעון את כולו
            context = ET.iterparse(gz, events=("end",))
            
            count = 0
            for event, elem in context:
                if elem.tag == "Item":
                    # שואבים רק את מה שצריך
                    product = {
                        "name": elem.findtext("ItemName") or "ללא שם",
                        "price": elem.findtext("ItemPrice") or "0",
                        "store": "שופרסל"
                    }
                    products.append(product)
                    count += 1
                    
                    # השורה הקריטית: מנקים את הזיכרון מהפריט שסיימנו
                    elem.clear()
                    
                    # הגבלה ל-100 מוצרים ראשונים - יציב ומהיר לגיליון
                    if count >= 100:
                        break
            
            return products