import requests
import gzip
import xml.etree.ElementTree as ET
import io

class DataProcessor:
    def get_products(self, file_url):
        processed_products = []
        try:
            # הורדה בשיטת Stream (לא טוען הכל לזיכרון)
            response = requests.get(file_url, stream=True, timeout=30)
            if response.status_code != 200:
                return {"error": "Failed to download file"}

            # פתיחת ה-GZIP
            with gzip.GzipFile(fileobj=response.raw) as f:
                # שימוש ב-iterparse למציאת מוצרים תוך כדי קריאה
                context = ET.iterparse(f, events=('end',))
                for event, elem in context:
                    if elem.tag == 'Item':
                        # שליפת הנתונים מהאלמנט
                        name = elem.findtext('ItemName')
                        price = elem.findtext('ItemPrice')
                        unit = elem.findtext('UnitOfMeasure')
                        
                        processed_products.append({
                            "name": name,
                            "price": price,
                            "unit": unit
                        })
                        
                        # עוצרים אחרי 20 מוצרים כדי להיות בטוחים שהשרת לא יקרוס
                        if len(processed_products) >= 20:
                            break
                        
                        # ניקוי הזיכרון תוך כדי עבודה
                        elem.clear()
            
            return processed_products

        except Exception as e:
            return {"error": f"Processing error: {str(e)}"}