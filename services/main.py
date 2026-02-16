from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"status": "SmartMarket Online", "version": "1.1"}

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