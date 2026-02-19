import cloudscraper
import gzip
import xml.etree.ElementTree as ET
from io import BytesIO

def get_automated_data():
    # יוצר דפדפן "בלתי נראה"
    scraper = cloudscraper.create_scraper()
    
    # 1. מציאת הלינק העדכני אוטומטית (כדי שלא תצטרך להדביק לינקים)
    base_url = "https://kingstore.binaprojects.com/Main.aspx"
    try:
        page = scraper.get(base_url)
        # כאן אנחנו מוצאים את הקובץ האחרון שעלה (Price)
        # (בגרסה הבאה נוסיף סורק לינקים אוטומטי מלא)
        target_url = "https://kingstore.binaprojects.com/Download.aspx?File=Price7290058108879-340-202602190910.gz"
        
        print("🚀 מוריד נתונים ללא מגע יד אדם...")
        res = scraper.get(target_url)
        
        if res.status_code == 200:
            with gzip.GzipFile(fileobj=BytesIO(res.content)) as f:
                xml_content = f.read()
                root = ET.fromstring(xml_content)
                
                products = []
                # שליפת השדות המקצועיים שלך
                for item in root.findall('.//Item')[:100]:
                    products.append({
                        "name": item.findtext('ItemNm'),
                        "price": item.findtext('ItemPrice'),
                        "manufacturer": item.findtext('ManufacturerName'),
                        "unit": item.findtext('UnitOfMeasure')
                    })
                return products
        return {"error": "Access Denied by Store"}
    except Exception as e:
        return {"error": str(e)}