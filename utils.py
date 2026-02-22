import re

def extract_store_id(filename: str):
    """
    מקבל שם קובץ כמו:
    Price7290700100008-000-203-20260222-151529.gz
    ומחזיר את מספר הסניף: 203
    """
    match = re.search(r"-\d{3,4}-", filename)
    if not match:
        return None
    return match.group(0).replace("-", "")