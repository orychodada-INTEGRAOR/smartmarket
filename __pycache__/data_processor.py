import requests
import gzip
import xml.etree.ElementTree as ET
from io import BytesIO

class DataProcessor:
    def get_real_data_streaming(self, url: str):
        # משיכה חכמה בזרם למניעת קריסת זיכרון
        response = requests.get(url, stream=True)
        response.raise_for_status()

        with gzip.GzipFile(fileobj=response.raw) as gz:
            products = []
            context = ET.iterparse(gz, events=("end",))
            
            count = 0
            for event, elem in context:
                if elem.tag == "Item":
                    product = {
                        "name": elem.findtext("ItemName") or "ללא שם",
                        "price": elem.findtext("ItemPrice") or "0",
                        "store": "שופרסל"
                    }
                    products.append(product)
                    count += 1
                    elem.clear() # פינוי זיכרון מיידי
                    if count >= 100:
                        break
            return products