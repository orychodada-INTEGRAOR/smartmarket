from fastapi import FastAPI
from routers import matrix  # כאן אנחנו אומרים למערכת להשתמש בתיקיית הראוטרים שלנו

app = FastAPI(
    title="SmartMarket - S&M Core API",
    description="The engine behind SmartMarket application",
    version="1.0.0"
)

# השורה הזו היא ה"דבק" שמחבר את המנוע של המטריקס ל-API
app.include_router(matrix.router)
  
@app.get("/")
def home():
    return {
        "status": "Online",
        "company": "SmartMarket - S&M",
        "message": "System is running smoothly"
    }# test