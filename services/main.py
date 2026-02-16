from fastapi import FastAPI
from matrix_parser import MatrixParser
app = FastAPI()

@app.get("/")
def home():
    return {"status": "SmartMarket Online", "msg": "S&M System is Live"}

@app.get("/chains")
def get_chains():
    return [
        {"name": "Victory", "url": "https://priece.victory.co.il"},
        {"name": "Yohananof", "url": "https://yohananof.co.il"}
    ]

@app.get("/test-prices")
def test_prices():
    return {
        "status": "Online",
        "source": "Victory",
        "data": [
            {"item": "חלב תנובה 3%", "price": "6.23"},
            {"item": "לחם פרוס", "price": "7.10"}
        ]
    }
@app.get("/get-latest-link")
def get_latest_link():
    parser = MatrixParser()
    # דוגמה על ויקטורי
    victory_catalog = "https://priece.victory.co.il/" 
    latest_url = parser.get_latest_price_file(victory_catalog)
    return {"chain": "Victory", "latest_price_file": latest_url}