SOURCES = {
    "gov_full": "https://next.obudget.org/sijui_utp/utp_prices_full.json.gz",
    "gov_updates": "https://next.obudget.org/sijui_utp/utp_prices_updates.json.gz",
    "gov_promotions": "https://next.obudget.org/sijui_utp/utp_prices_promotions.json.gz",
}
import gzip
import json
import httpx

async def fetch_gov_file(url: str):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }
    async with httpx.AsyncClient(headers=headers, timeout=60) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        data = gzip.decompress(resp.content)
        return json.loads(data)