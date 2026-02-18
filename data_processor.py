import requests
import gzip
import xml.etree.ElementTree as ET
from io import BytesIO

class DataProcessor:
    def get_real_data_streaming(self, url: str):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }

        try:
            # הורדת כל התוכן לזיכרון כדי למנוע בעיות Seek
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            file_content = response.content
            
            # בדיקה אם הקובץ דחוס (GZIP מתחיל ב-1f 8b)
            if file_content.startswith(b'\x1f\x8b'):
                source = gzip.GzipFile(fileobj=BytesIO(file_content))
            else:
                source = BytesIO(file_content)

            products = []
            # סריקה של ה-XML
            context = ET.iterparse(source, events=("end",))
            
            count = 0
            for event, elem in context:
                if elem.tag == "Item":
                    product = {
                        "code": elem.findtext("ItemCode") or "N/A",
                        "name": elem.findtext("ItemName") or "ללא שם",
                        "price": elem.findtext("ItemPrice") or "0",
                        "store": "סופר ספיר"
                    }
                    products.append(product)
                    count += 1
                    elem.clear()
                    if count >= 100: # הגבלה לטעינה מהירה בבדיקה
                        break
            
            return products

        except Exception as e:
            raise Exception(f"Failed to fetch data: {str(e)}")