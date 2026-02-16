import requests
from bs4 import BeautifulSoup

class MatrixParser:
    def get_latest_price_file(self, catalog_url):
        try:
            # שליפת רשימת הקבצים מהקטלוג של הרשת
            response = requests.get(catalog_url, timeout=10)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a')
            
            # סינון: אנחנו מחפשים קובץ "PriceFull" (מחירים מלאים)
            price_files = []
            for link in links:
                href = link.get('href', '')
                # מחפשים קבצים שמכילים PriceFull וסיומת xml או gz
                if "PriceFull" in href and (href.endswith('.xml') or href.endswith('.gz')):
                    price_files.append(href)
            
            # מיון: לוקחים את הקובץ האחרון ברשימה (בדרך כלל החדש ביותר)
            if price_files:
                # וודא שהקישור מלא
                latest_file = price_files[-1]
                if not latest_file.startswith('http'):
                    base_url = catalog_url.rsplit('/', 1)[0]
                    latest_file = f"{base_url}/{latest_file}"
                return latest_file
                
            return None
        except Exception as e:
            print(f"Error parsing Matrix: {e}")
            return None