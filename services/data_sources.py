# services/data_sources.py

import requests
from bs4 import BeautifulSoup

GOV_URL = "https://www.gov.il/he/pages/cpfta_prices_regulations"

class DataSources:
    """
    שואב את רשימת הרשתות מהדף הממשלתי של חוק המזון.
    מחזיר רשימה של:
    {
        "name": "Shufersal",
        "url": "https://url-to-price-files/"
    }
    """

    def __init__(self):
        self.url = GOV_URL
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0 Safari/537.36"
            )
        }

    def fetch_html(self):
        """מוריד את ה-HTML של הדף הממשלתי"""
        response = requests.get(self.url, headers=self.headers)
        response.raise_for_status()
        return response.text

    def extract_links(self, html):
        """
        מוצא את כל הקישורים לרשתות מתוך הדף.
        מחזיר רשימה של dicts.
        """
        soup = BeautifulSoup(html, "html.parser")
        links = soup.find_all("a", href=True)

        results = []

        for link in links:
            href = link["href"]
            text = link.get_text(strip=True)

            # סינון קישורים רלוונטיים בלבד
            if "price" in href.lower() or "matrix" in href.lower():
                results.append({
                    "name": text,
                    "url": href
                })

        return results

    def get_data_sources(self):
        """פונקציה ראשית — מחזירה את רשימת הרשתות"""
        html = self.fetch_html()
        return self.extract_links(html)