import requests
import gzip
from lxml import etree

class DataProcessor:
    """
    קורא קובצי מחיר אמיתיים מהמדינה ב-STREAM
    ומחזיר רשימה של מוצרים.
    """

    def get_products(self, file_url):
        """
        מקבל URL של קובץ מחיר (PriceFull / PriceUpdate)
        ומחזיר רשימת מוצרים.
        """

        products = []

        try:
            # הורדה בזרימה - לא טוען את כל הקובץ לזיכרון
            response = requests.get(file_url, stream=True, timeout=60)
            response.raise_for_status()

            # פתיחת קובץ GZIP תוך כדי קריאה
            with gzip.GzipFile(fileobj=response.raw) as gz:
                # קריאת XML ב-iterparse (יעיל מאוד)
                context = etree.iterparse(gz, events=("end",), tag="Item")

                for event, elem in context:
                    name = elem.findtext("ItemName")
                    price = elem.findtext("ItemPrice")
                    unit = elem.findtext("UnitQty")
                    category = elem.findtext("ItemType")

                    if name and price:
                        products.append({
                            "name": name,
                            "price": price,
                            "unit": unit or "",
                            "category": category or ""
                        })

                    # כדי לא להפיל את Render — עוצרים אחרי 30 מוצרים
                    if len(products) >= 30:
                        break

                    # ניקוי זיכרון
                    elem.clear()
                    while elem.getprevious() is not None:
                        del elem.getparent()[0]

            return products

        except Exception as e:
            return [{"error": f"שגיאה בקריאת קובץ המחיר: {str(e)}"}]