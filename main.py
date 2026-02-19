from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from data_processor import DataProcessor
import uvicorn
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "SmartMarket API Online", "target": "King Store"}

@app.get("/api/products")
def get_products():
    # הלינק הישיר שמצאת הבוקר
    url = "https://kingstore.binaprojects.com/Download.aspx?File=Price7290058108879-340-202602190910.gz"
    
    processor = DataProcessor()
    try:
        products = processor.get_real_data_streaming(url)
        return {
            "status": "success",
            "source": "King Store Real-time",
            "count": len(products),
            "products": products
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "products": [{"name": "שגיאה בטעינה", "price": "0", "store": "קינג סטור"}]
        }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)