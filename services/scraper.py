import requests
from bs4 import BeautifulSoup
import gzip
import xml.etree.ElementTree as ET
from io import BytesIO

class VictoryScraper:
    def __init__(self):
        self.base_url = "https://matrixcatalog.co.il/Victory/"

    def get_latest_price_file(self):
        response = requests.get(self.base_url)
        # שימוש ב-html.parser במקום lxml
        soup = BeautifulSoup(response.text, "html.parser") 
        links = [a['href'] for a in soup.find_all('a', href=True) if "PriceFull" in a['href'] and a['href'].endswith(".gz")]
        return self.base_url + links[-1] if links else None

    def fetch_prices(self):
        url = self.get_latest_price_file()
        if not url: return {"error": "No file found"}
        
        # הורדה ופתיחה בזיכרון (0 עלויות אחסון!)
        response = requests.get(url)
        with gzip.GzipFile(fileobj=BytesIO(response.content)) as f:
            tree = ET.parse(f)
            root = tree.getroot()
            
            products = []
            # לוקחים רק את 5 המוצרים הראשונים לבדיקה ראשונית
            for item in root.findall('.//Product')[:5]:
                products.append({
                    "שם_מוצר": item.find('ItemName').text if item.find('ItemName') is not None else "לא ידוע",
                    "מחיר": item.find('ItemPrice').text if item.find('ItemPrice') is not None else "0",
                    "ברקוד": item.find('ItemCode').text if item.find('ItemCode') is not None else "0"
                })
            return {"source": "Victory", "data": products}