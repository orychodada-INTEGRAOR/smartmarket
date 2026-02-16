import requests
from bs4 import BeautifulSoup

class MatrixParser:
    """
    מקבל URL של רשת (לדוגמה: https://matrixcatalog.co.il/shufersal/)
    ומחזיר את קובץ המחיר העדכני ביותר.
    """

    def __init__(self):
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0 Safari/537.36"
            )
        }

    def fetch_html(self, url):
        """מוריד HTML של דף הרשת במטריקס"""
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.text

    def find_latest_file(self, html):
        """
        מוצא את קובץ המחיר העדכני ביותר מתוך רשימת הקבצים.
        מחפש קבצי:
        - PriceFull
        - PriceUpdate
        - PromoFull
        - PromoUpdate
        """
        soup = BeautifulSoup(html, "html.parser")
        links = soup.find_all("a", href=True)

        candidates = []

        for link in links:
            href = link["href"].lower()

            if any(key in href for key in ["pricefull", "priceupdate", "promofull", "promoupdate"]):
                candidates.append(href)

        if not candidates:
            return None

        candidates.sort()
        return candidates[-1]

    def get_latest_price_file(self, chain_url):
        """
        פונקציה ראשית:
        מקבלת URL של רשת
        מחזירה URL מלא של קובץ המחיר העדכני ביותר
        """
        html = self.fetch_html(chain_url)
        latest = self.find_latest_file(html)

        if not latest:
            return None

        if latest.startswith("http"):
            return latest
        else:
            return chain_url.rstrip("/") + "/" + latest.lstrip("/")