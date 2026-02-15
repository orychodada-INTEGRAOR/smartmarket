import re

class MatrixParser:
    def __init__(self):
        # מחפש קבצים שכתוב בהם Price (מחיר)
        self.file_pattern = re.compile(r'PriceFull|Price')

    def extract_links(self, html_content: str):
        # מוציא את כל הקישורים מהדף
        links = re.findall(r'href=[\'"]?([^\'" >]+)', html_content)
        return [link for link in links if self.file_pattern.search(link)]

    def pick_latest(self, links: list):
        if not links: return None
        # ממיין כדי לקחת את הקובץ עם התאריך הכי חדש
        links.sort(reverse=True)
        return links[0]