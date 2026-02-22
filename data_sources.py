import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# דפי שקיפות מחירים אמיתיים
CHAIN_PAGES = {
    "good_pharm": "https://goodpharm.binaprojects.com/Main.aspx",
    "laib": "https://laibcatalog.co.il/",
    "zol_vebegadol": "https://zolvebegadol.binaprojects.com/Main.aspx",
    "hazi_hinam": "https://shop.hazi-hinam.co.il/Prices"
}

# אילו סוגי קבצים אנחנו מחפשים
VALID_KEYWORDS = ["PriceFull", "PriceUpdate", "Promo", "Price", "Full", "Update"]
VALID_EXTENSIONS = [".gz", ".zip", ".xml"]


async def get_latest_file_url(source_id: str):
    """
    סורק דף שקיפות מחירים ומחזיר את הקובץ הכי חדש.
    מותאם לדפים כמו GoodPharm / זול ובגדול / חצי חינם.
    """
    base_url = CHAIN_PAGES.get(source_id)
    if not base_url:
        print(f"⚠️ אין דף מוגדר עבור {source_id}")
        return None

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "*/*",
        "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8"
    }

    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=30.0) as client:
        try:
            response = await client.get(base_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            links = []

            # חיפוש בכל הלינקים בעמוד
            for a in soup.find_all("a", href=True):
                href = a["href"]

                # בדיקה אם הלינק מכיל מילות מפתח של קבצי מחירון
                if any(key in href for key in VALID_KEYWORDS) and any(ext in href for ext in VALID_EXTENSIONS):
                    full_url = urljoin(base_url, href)
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