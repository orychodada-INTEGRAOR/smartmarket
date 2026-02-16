from fastapi import APIRouter, Query
from services.matrix_parser import MatrixParser
from services.matrix_client import MatrixClient

router = APIRouter(prefix="/matrix", tags=["Matrix Engine"])

@router.get("/latest")
async def import requests
from bs4 import BeautifulSoup

class MatrixParser:
    def get_latest_price_file(self, catalog_url):
        # הגדרת "זהות" של דפדפן רגיל כדי שלא יחסמו אותנו
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        try:
            # הוספת ה-headers לבקשה
            response = requests.get(catalog_url, headers=headers, timeout=15)
            if response.status_code != 200:
                print(f"Error: Status code {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            # מוצאים את כל הקישורים שמכילים את המילה PriceFull
            links = [a.get('href') for a in soup.find_all('a', href=True) if "PriceFull" in a.get('href')]
            
            if links:
                # לוקחים את האחרון (הכי מעודכן)
                latest_file = links[-1]
                # אם הקישור חלקי, נשלים אותו
                if not latest_file.startswith('http'):
                    latest_file = f"https://priece.victory.co.il/{latest_file.lstrip('/')}"
                return latest_file
                
            return "No links found"
        except Exception as e:
            return f"Error: {str(e)}"(url: str = Query(..., description="The URL of the supermarket price page")):
    client = MatrixClient()
    parser = MatrixParser()
    
    # 1. השליח (Client) מביא את ה-HTML מהאתר
    html = client.get_html(url)

    # 2. המוח (Parser) מוציא את כל הקישורים לקבצי המחירים
    links = parser.extract_links(html)
    
    # 3. המוח בוחר את הקובץ עם התאריך הכי עדכני
    latest = parser.pick_latest(links)
    
    if not latest:
        return {"status": "error", "message": "No price files found at this URL"}
        
    return {
        "status": "success", 
        "company": "SmartMarket - S&M",
        "latest_file_url": latest
    }