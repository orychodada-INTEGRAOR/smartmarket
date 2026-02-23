from fastapi import FastAPI
from gov_sources import process_gov_sources

app = FastAPI()

@app.get("/update-all")
async def update_all():
    gov_result = await process_gov_sources()

    return {
        "status": "complete",
        "gov_data": gov_result
    }