class VictoryScraper:
    def fetch_prices(self):
        return {
            "status": "Ready",
            "source": "Victory",
            "data": [
                {"שם_מוצר": "חלב תנובה 3% (דגימה)", "מחיר": "6.23", "ברקוד": "729000004321"},
                {"שם_מוצר": "לחם אחיד (דגימה)", "מחיר": "5.12", "ברקוד": "729000001111"}
            ],
            "note": "System is in Lean Mode to ensure stability"
        }