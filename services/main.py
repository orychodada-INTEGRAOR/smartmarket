from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SmartMarket API")

# הגדרות CORS כדי שהאפליקציה תוכל לדבר עם השרת
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "SmartMarket API is Live", "version": "1.0.0"}

@app.get("/matrix")
def get_matrix():
    return {
        "engine": "Matrix Engine",
        "status": "Active",
        "message": "Welcome to SmartMarket Infrastructure"
    }
from fastapi import FastAPI
from services.data_sources import DataSources # הייבוא של הקוד החדש

app = FastAPI(title="SmartMarket - S&M")

@app.get("/")
def read_root():
    return {"status": "SmartMarket is Online"}

@app.get("/chains")
def get_chains():
    ds = DataSources()
    try:
        data = ds.get_data_sources()
        return {"count": len(data), "chains": data}
    except Exception as e:
        return {"error": str(e)}
    from services.scraper import VictoryScraper # תוסיף למעלה עם שאר הייבואים

@app.get("/test-prices")
def test_prices():
    scraper = VictoryScraper()
    return scraper.fetch_prices()