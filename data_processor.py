import requests
import gzip
import xml.etree.ElementTree as ET
from io import BytesIO

class DataProcessor:
    def get_real_data_streaming(self, url: str):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        }

        try:
            # הורדת הקובץ
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # פתיחת ה-GZIP בזיכרון (כמו שעשית עם 7-Zip, רק אוטומטי)
            if response.content.startswith(b'\x1f\x8b'):
                source = gzip.GzipFile(fileobj=BytesIO(response.content))
                xml_content = source.read()
            else:
                xml_content = response.content

            # פיענוח ה-XML
            root = ET.fromstring(xml_content)
            
            products = []
            # שליפת המידע המפורט בדיוק לפי ה-Converter שלך
            for item in root.findall('.//Item'):
                product = {
                    "code": item.findtext('ItemCode') or '',
                    "name": item.findtext('ItemNm') or '', # שימוש ב-ItemNm כפי שמופיע בקובץ שלך
                    "manufacturer": item.findtext('ManufacturerName') or 'לא ידוע',
                    "price": item.findtext('ItemPrice') or '0',
                    "unit_measure": item.findtext('UnitOfMeasure') or '',
                    "quantity": item.findtext('Quantity') or '',
                    "unit_price": item.findtext('UnitOfMeasurePrice') or '',
                    "country": item.findtext('ManufactureCountry') or '',
                    "store": "קינג סטור"
                }
                products.append(product)
                
                # הגבלה ל-100 מוצרים ראשונים לבדיקה מהירה
                if len(products) >= 100:
                    break
            
            return products

        except Exception as e:
            raise Exception(f"שגיאה בעיבוד הנתונים המקצועי: {str(e)}")