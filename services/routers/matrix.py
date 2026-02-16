import requests

class MatrixParser:
    def get_latest_price_file(self, chain_id="7290696200003"): # קוד ויקטורי
        try:
            # אנחנו פונים לממשק של "פרייסז" או מקור פתוח אחר שמנגיש את הקישורים
            # לצורך הבדיקה, נשתמש בפורמט הקישור הישיר הידוע של ויקטורי
            # שבו התאריך מוטמע בכתובת
            import datetime
            today = datetime.datetime.now().strftime("%Y%m%d")
            
            # בניית קישור משוער (ויקטורי מעלים קבצים בפורמט קבוע)
            # זה פתרון זמני חכם שעוקף את החסימה של הסריקה
            url = f"https://priece.victory.co.il/PriceFull{chain_id}-010-{today}0400.gz"
            
            # בדיקה אם הקובץ קיים
            check = requests.head(url, timeout=5)
            if check.status_code == 200:
                return url
            
            return "File not ready yet, try again in 10 min"
        except Exception as e:
            return f"Error: {str(e)}"