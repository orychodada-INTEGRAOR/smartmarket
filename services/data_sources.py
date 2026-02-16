# services/data_sources.py

class DataSources:
    def __init__(self):
        # רשימת "מפת הדרכים" של רשתות השיווק בישראל
        self.chains_map = [
            {"name": "שופרסל", "url": "https://prices.shufersal.co.il/"},
            {"name": "רמי לוי", "url": "https://prices.ramilevy.co.il/"},
            {"name": "ויקטורי", "url": "https://matrixcatalog.co.il/Victory/"},
            {"name": "יוחננוף", "url": "https://publishprice.yohananof.co.il/"},
            {"name": "מחסני השוק", "url": "https://www.mck.co.il/prices/"},
            {"name": "יינות ביתן", "url": "https://prices.ybitan.co.il/"}
        ]

    def get_data_sources(self):
        return {
            "count": len(self.chains_map),
            "chains": self.chains_map
        }