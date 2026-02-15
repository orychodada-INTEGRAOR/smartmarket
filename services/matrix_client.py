import requests
from fastapi import HTTPException

class MatrixClient:
    def __init__(self):
        # הגדרת דפדפן וירטואלי כדי שהאתרים לא יחסמו אותנו
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def get_html(self, url: str) -> str:
        """פונקציה שמושכת את תוכן האתר (HTML)"""
        try: 
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status() # בדיקה שהדף נטען בהצלחה
            return response.text
        except requests.RequestException as e:
            # אם יש שגיאה (כמו אתר שקרס), המערכת תדווח לנו
            raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {str(e)}")

    def download_file(self, file_url: str, save_path: str):
        """פונקציה שמורידה את קובץ המחירים הכבד (XML) למחשב/לשרת"""
        try:
            with requests.get(file_url, headers=self.headers, stream=True) as r:
                r.raise_for_status()
                with open(save_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            return save_path
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")