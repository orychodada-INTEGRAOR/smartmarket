import requests
import gzip
import xml.etree.ElementTree as ET
from io import BytesIO

class DataProcessor:

    def get_real_data(self, url: str):
        # הורדת קובץ המחיר
        response = requests.get(url)
        response.raise_for_status()

        # פתיחת GZIP
        gz = gzip.GzipFile(fileobj=BytesIO(response.content))
        xml_data = gz.read()

        # ניתוח XML
        root = ET.fromstring(xml_data)

        products = []
        for item in root.findall(".//Item"):
            products.append({
                "code": item.findtext("ItemCode"),
                "name": item.findtext("ItemName"),
                "price": item.findtext("ItemPrice"),
                "category": item.findtext("Category"),
            })

        return products