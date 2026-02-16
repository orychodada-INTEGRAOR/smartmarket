from fastapi import FastAPI
from matrix_parser import MatrixParser
from data_processor import DataProcessor

app = FastAPI()
parser = MatrixParser()
processor = DataProcessor()

@app.get("/")
def home():
    return {"status": "SmartMarket Online", "msg": "Ready for Glide"}

@app.get("/view-products")
def view_products():
    # 1. מוצאים את הלינק העדכני
    link = parser.get_latest_price_file()
    
    # 2. מעבדים את המוצרים מתוך הלינק
    products = processor.get_products(link)
    
    return {
        "chain": "Victory",
        "total_items": len(products) if isinstance(products, list) else 0,
        "items": products
    }