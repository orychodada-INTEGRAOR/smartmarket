"""
מעבד נתונים - Data Processor
מטפל בהורדה, פענוח ושמירה של מחירונים
"""

import gzip
import xml.etree.ElementTree as ET
from datetime import datetime
import json
import os
from pathlib import Path

class DataProcessor:
    """מחלקה לעיבוד מחירונים"""
    
    def __init__(self, cache_dir='cache'):
        self.cache_dir = cache_dir
        Path(cache_dir).mkdir(exist_ok=True)
    
    def process_gz(self, gz_content):
        try:
            # בדיקה אם זה JSON
            if gz_content.startswith(b'[{') or gz_content.startswith(b'{'):
                data = json.loads(gz_content.decode('utf-8'))
                
                if isinstance(data, list):
                    products = []
                    for item in data:
                        product = {
                            'id': str(item.get('ItemCode', '')),
                            'name': str(item.get('ItemNm', '')),
                            'price': float(item.get('ItemPrice', 0)) if item.get('ItemPrice') else 0.0,
                            'manufacturer': str(item.get('ManufacturerName', '')),
                            'unit_measure': str(item.get('UnitOfMeasure', '')),
                            'timestamp': datetime.now().isoformat()
                        }
                        products.append(product)
                    
                    print(f"✅ עובדו {len(products)} מוצרים מ-JSON")
                    return products
            
            # נסה GZ
            xml_content = gzip.decompress(gz_content).decode('utf-8')
            root = ET.fromstring(xml_content)
            
            products = []
            for item in root.findall('.//Item'):
                product = {
                    'id': self.get_text(item, 'ItemCode'),
                    'name': self.get_text(item, 'ItemNm'),
                    'price': self.get_float(item, 'ItemPrice'),
                    'manufacturer': self.get_text(item, 'ManufacturerName'),
                    'timestamp': datetime.now().isoformat()
                }
                pro