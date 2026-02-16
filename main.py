from fastapi import FastAPI
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
def get_latest_file(chain_url: str):
    """
    מקבל URL של רשת (לדוגמה: https://matrixcatalog.co.il/shufersal/)
    ומחזיר את קובץ המחיר העדכני ביותר
    """
    return parser.get_latest_price_file(chain_url)


@app.get("/get-products")
def get_products(chain_url: str = None):
    """
    מוצא את קובץ המחיר העדכני ביותר ומחזיר מוצרים מעובדים
    """
    latest_file = parser.get_latest_price_file(chain_url)

    if not latest_file:
        return {"error": "לא נמצא קובץ מחיר לרשת"}

    return processor.get_products(latest_file)


@app.get("/view-products")
def view_products(chain_url: str = None):
    """
    קורא קובץ מחיר אמיתי מהאינטרנט ומחזיר מוצרים אמיתיים
    """
    # אם לא הבאנו לינק, השרת לוקח את של ויקטורי כברירת מחדל
    target_url = chain_url or "https://priece.victory.co.il/PriceFull7290696200003-010-202602160400.gz"

    products = processor.get_real_data(target_url)
    return {"items": products}