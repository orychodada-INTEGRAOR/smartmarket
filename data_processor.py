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
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # בדיקה אם הקובץ דחוס
            if response.content.startswith(b'\x1f\x8b'):
                source = gzip.GzipFile(fileobj=BytesIO(response.content))
            else:
                source = BytesIO(response.content)

            products = []
            # בקינג סטור יש Namespace ב-XML, אנחנו מגדירים אותו כאן
            context = ET.iterparse(source, events=("end",))
            
            count = 0
            for event, elem in context:
                # הסרת ה-Namespace משם התגית כדי שיהיה קל לקרוא
                tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
                
                if tag == "Item":
                    product = {
                        "code": elem.findtext(".//ItemCode") or "N/A",
                        "name": elem.findtext(".//ItemName") or "ללא שם",
                        "price": elem.findtext(".//ItemPrice") or "0",
                        "store": "קינג סטור"
                    }
                    products.append(product)
                    count += 1
                    elem.clear()
                    if count >= 100: break
            
            return products

        except Exception as e:
            raise Exception(f"Error in DataProcessor: {str(e)}")