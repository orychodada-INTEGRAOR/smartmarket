from fastapi import FastAPI
from services.data_sources import DataSources
from services.scraper import VictoryScraper # וודא שהשורה הזו קיימת

app = FastAPI(title="SmartMarket API")

@app.get("/")
def read_root():
    return {"status": "SmartMarket is Online"}

@app.get("/chains")
def get_chains():
    ds = DataSources()
    return ds.get_data_sources()

# הוסף את הבלוק הזה בסוף הקובץ:
@app.get("/test-prices")
def test_prices():
    scraper = VictoryScraper()
    return scraper.fetch_prices()