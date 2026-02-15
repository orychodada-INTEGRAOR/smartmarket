from fastapi import APIRouter, Query
from services.matrix_parser import MatrixParser
from services.matrix_client import MatrixClient

router = APIRouter(prefix="/matrix", tags=["Matrix Engine"])

@router.get("/latest")
async def get_latest_price_file(url: str = Query(..., description="The URL of the supermarket price page")):
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