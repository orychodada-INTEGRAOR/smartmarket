from fastapi import FastAPI

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