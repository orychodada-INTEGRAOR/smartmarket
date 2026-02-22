import httpx

async def fetch_with_headers(url: str):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "*/*",
        "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8"
    }

    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=60.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.content