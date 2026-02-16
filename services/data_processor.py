import requests
import gzip
import xmltodict
import io

class DataProcessor:
    def get_products(self, file_url):
        try:
            # 1. הורדת הקובץ המכווץ
            response = requests.get(file_url, timeout=30)
            if response.status_code != 200:
                return {"error": "Failed to download file"}

            # 2. פתיחת הכיווץ (GZIP) בזיכרון
            with gzip.GzipFile(fileobj=io.BytesIO(response.content)) as f:
                xml_content = f.read()

            # 3. המרה מ-XML למילון Python
            data_dict = xmltodict.parse(xml_content)
            
            # 4. שליפת רשימת המוצרים (המבנה משתנה בין רשתות, זה מותאם לויקטורי/יוחננוף)
            products_raw = data_dict.get('root', {}).get('Items', {}).get('Item', [])
            
            processed_products = []
            # לוקחים רק את ה-50 הראשונים כדי שהשרת לא יקרוס בחינם
            for p in products_raw[:50]:
                processed_products.append({
                    "name": p.get('ItemName'),
                    "price": p.get('ItemPrice'),
                    "unit": p.get('UnitOfMeasure'),
                    "barcode": p.get('ItemCode')
                })
            
            return processed_products

        except Exception as e:
            return {"error": str(e)}