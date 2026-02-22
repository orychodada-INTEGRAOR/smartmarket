import httpx
import re
from datetime import datetime

GOV_API = "https://www.gov.il/api/DownloadFile?fileName=PriceFull"

PRICEFULL_PATTERN = re.compile(r"PriceFull.*?(\d{12})\.gz$")
PRICEUPDATE_PATTERN = re.compile(r"PriceUpdate.*?(\d{12})\.gz$")


async def fetch_gov_list():
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.get(GOV_API)
        response.raise_for_status()
        return response.json()


def extract_timestamp(filename):
    match = re.search(r"(\d{12})", filename)
    if not match:
        return None
    return datetime.strptime(match.group(1), "%Y%m%d%H%M")


def pick_latest(files, pattern):
    candidates = []
    for f in files:
        if pattern.search(f["FileName"]):
            ts = extract_timestamp(f["FileName"])
            if ts:
                candidates.append((ts, f["DownloadUrl"]))

    if not candidates:
        return None

    candidates.sort(reverse=True)
    return candidates[0][1]


async def get_latest_sources():
    print("📡 מוריד רשימת קבצים ממשרד הכלכלה...")
    files = await fetch_gov_list()

    sources = {}

    for f in files:
        chain_id = f.get("ChainId")
        if not chain_id:
            continue

        if chain_id not in sources:
            sources[chain_id] = {"full": None, "update": None}

    for chain_id in sources.keys():
        chain_files = [f for f in files if f.get("ChainId") == chain_id]

        latest_full = pick_latest(chain_files, PRICEFULL_PATTERN)
        latest_update = pick_latest(chain_files, PRICEUPDATE_PATTERN)

        sources[chain_id]["full"] = latest_full
        sources[chain_id]["update"] = latest_update

    print("✅ נמצא מידע עדכני לכל הרשתות")
    return sources