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
            response = requests.get(url, stream=True, headers=headers, timeout=30)
            response.raise_for_status()
            
            # בדיקה אם הקובץ באמת דחוס (GZIP מתחיל ב-1f 8b)
            content = response.raw.read(2)
            response.raw._fp.fp.seek(0) # חזרה לתחילת הקובץ
            
            if content.startswith(b'\x1f\x8b'):
                source = gzip.GzipFile(fileobj=response.raw)
            else:
                source = response.raw

            products = []
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
                    if count >= 100: break
            
            return products

        except Exception as e:
            raise Exception(f"Failed to fetch data: {str(e)}")