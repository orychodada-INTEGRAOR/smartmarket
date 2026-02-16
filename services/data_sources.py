import requests
from bs4 import BeautifulSoup

class DataSources:
    def __init__(self):
        self.url = "https://www.gov.il/he/pages/cpfta_prices_regulations"
        # הוספת Headers כדי שהאתר יחשוב שאנחנו דפדפן אמיתי
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        }

    def get_data_sources(self):
        try:
            response = requests.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            results = []
            
            # חיפוש קישורים בתוך הטבלאות או הרשימות בדף
            for link in soup.find_all("a", href=True):
                href = link["href"]
                text = link.get_text(strip=True)
                
                # אנחנו מחפשים קישורים שמובילים לאתרי המחירים
                if any(word in href.lower() for word in ["price", "market", "matrix", "xml"]):
                    results.append({
                        "name": text if text else "קישור חיצוני",
                        "url": href if href.startswith("http") else f"https://www.gov.il{href}"
                    })
            
            return results
        except Exception as e:
            return [{"error": f"Failed to fetch data: {str(e)}"}]