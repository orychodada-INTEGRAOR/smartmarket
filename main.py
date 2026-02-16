from fastapi import FastAPI, HTTPException
from services.data_sources import DataSources
from services.matrix_parser import MatrixParser
from data_processor import DataProcessor

app = FastAPI()

ds = DataSources()
parser = MatrixParser()
processor = DataProcessor()


@app.get("/")
def root():
    return {"status": "SmartMarket API is running"}


@app.get("/chains")
def get_chains():
    return ds.get_data_sources()


@app.get("/latest-file")
def get_latest_file(chain_key: str):
    chain_url = ds.get_chain_url(chain_key)
    if not chain_url:
        raise HTTPException(status_code=404, detail="רשת לא נמצאה")

    return parser.get_latest_price_file(chain_url)


@app.get("/get-products")
def get_products(chain_key: str):
    chain_url = ds.get_chain_url(chain_key)
    if not chain_url:
        raise HTTPException(status_code=404, detail="רשת לא נמצאה")

    latest_file = parser.get_latest_price_file(chain_url)
    if not latest_file:
        return {"error": "לא נמצא קובץ מחיר לרשת"}

    return processor.get_products(latest_file)


@app.get("/view-products")
def view_products(chain_url: str = None):
    # ברירת מחדל: קובץ מחיר אמיתי של שופרסל
    target_url = chain_url or "https://matrixcatalog.co.il/shufersal/PriceFull7290027600007-001-202402010400.gz"

    products = processor.get_real_data(target_url)
    return {"items": products}