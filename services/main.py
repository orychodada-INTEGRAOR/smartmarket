from fastapi import FastAPI
from services.data_sources import DataSources
from services.scraper import VictoryScraper

app = FastAPI()

@app.get("/")
def home():
    return {"status": "SmartMarket Online"}

@app.get("/chains")
def get_chains():
    return DataSources().get_data_sources()

@app.get("/test-prices")
def test_prices():
    return VictoryScraper().fetch_prices()