import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import datetime

# דפי שקיפות מחירים אמיתיים
CHAIN_PAGES = {
    "good_pharm": "https://goodpharm.binaprojects.com/Main.aspx",
    "zol_vebegadol": "https://zolvebegadol.binaprojects.com/Main.aspx",
    "hazi_hinam": "https://shop.hazi-hinam.co.il/Prices"
}

# אילו סוגי קבצים אנחנו מחפשים
VALID_KEYWORDS = ["PriceFull", "PriceUpdate", "Promo", "Price", "Full", "Update"]
VALID_EXTENSIONS = [".gz", ".zip", ".xml"]


async def fetch_html(url: str):
    """מוריד HTML עם headers כדי לעקוף חסימות."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "*/*",
        "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8"
    }
    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.text


async def get_latest_file_url(source_id: str):
    """
    סורק דף שקיפות מחירים ומחזיר את הקובץ הכי חדש.
    מותאם ל-GoodPharm / Zolvebegadol / HaziHinam.
    """
    base_url = CHAIN_PAGES.get(source_id)
    if not base_url:
        print(f"⚠️ אין דף מוגדר עבור {source_id}")
        return None

    try:
        html = await fetch_html(base_url)
        soup = BeautifulSoup(html, "html.parser")

        links = []

        # חיפוש בכל הלינקים בעמוד
        for a in soup.find_all("a", href=True):
            href = a["href"]

            # בדיקה אם הלינק מכיל מילות מפתח של קבצי מחירון
            if any(key in href for key in VALID_KEYWORDS) and any(ext in href for ext in VALID_EXTENSIONS):
                full_url = urljoin(base_url, href)
                links.append(full_url)

        # חצי חינם — דורש תאריך
        if source_id == "hazi_hinam" and not links:
            today = datetime.date.today().strftime("%Y-%m-%d")
            dated_url = f"https://shop.hazi-hinam.co.il/Prices?date={today}"
            print(f"📅 חצי חינם — טוען דף עם תאריך: {dated_url}")

            html = await fetch_html(dated_url)
            soup = BeautifulSoup(html, "html.parser")

            for a in soup.find_all("a", href=True):
                href = a["href"]
                if any(key in href for key in VALID_KEYWORDS) and any(ext in href for ext in VALID_EXTENSIONS):
                    full_url = urljoin(dated_url, href)
                    links.append(full_url)

        if not links:
            print(f"⚠️ לא נמצאו קבצי מחירון ב-{source_id}")
            return None

        # מיון לפי שם הקובץ (שבד"כ מכיל תאריך)
        links.sort(reverse=True)
        latest = links[0]

        print(f"🎯 Hunter: נמצא קובץ טרי עבור {source_id}: {latest}")
        return latest

    except Exception as e:
        print(f"❌ שגיאה בסריקת {source_id}: {e}")
        return None