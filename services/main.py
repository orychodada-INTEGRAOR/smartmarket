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