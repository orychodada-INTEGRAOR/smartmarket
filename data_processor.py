import requests
import gzip
import xml.etree.ElementTree as ET
from io import BytesIO

class DataProcessor:
    def get_real_data_streaming(self, url: str):
        # הגדרת דפדפן "אנושי" מזויף
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,all;q=0.8',
            'Accept-Language': 'he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://kingstore.binaprojects.com/Main.aspx',
            'Connection': 'keep-alive',
        }

        try:
            # שימוש ב-Session כדי לשמור על חיבור רציף
            session = requests.Session()
            # קודם כל "מבקרים" באתר כדי לקבל אישור (Cookie)
            session.get("https://kingstore.binaprojects.com/Main.aspx", headers=headers, timeout=15)
            
            # עכשיו מורידים את הקובץ עם האישור שקיבלנו
            response = session.get(url, headers=headers, timeout=30)
            
            if not response.content:
                raise Exception("The server returned an empty file (Blocked).")

            file_content = response.content
            
            # בדיקת GZIP
            if file_content.startswith(b'\x1f\x8b'):
                source = gzip.GzipFile(fileobj=BytesIO(file_content))
            else:
                source = BytesIO(file_content)

            products = []
            context = ET.iterparse(source, events=("end",))
            
            count = 0
            for event, elem in context:
                tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
                if tag == "Item":
                    product = {
                        "name": elem.findtext(".//ItemName") or "ללא שם",
                        "price": elem.findtext(".//ItemPrice") or "0",
                        "store": "קינג סטור"
                    }
                    products.append(product)
                    count += 1
                    elem.clear()
                    if count >= 100: break
            
            if not products:
                raise Exception("XML parsed but no items found.")
                
            return products

        except Exception as e:
            raise Exception(f"Failed to fetch data: {str(e)}")