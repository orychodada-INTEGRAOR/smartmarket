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
                products.append(product)
            
            print(f"✅ עובדו {len(products)} מוצרים")
            return products
            
        except Exception as e:
            print(f"❌ שגיאה: {e}")
            return []
    
    def get_text(self, element, tag):
        child = element.find(tag)
        return child.text if child is not None and child.text else ''
    
    def get_float(self, element, tag):
        text = self.get_text(element, tag)
        try:
            return float(text) if text else 0.0
        except:
            return 0.0
    
    def save_to_cache(self, products, source_id):
        filename = f"{self.cache_dir}/{source_id}.json"
        data = {
            'products': products,
            'updated': datetime.now().isoformat(),
            'count': len(products)
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 נשמרו {len(products)} מוצרים")
    
    def load_from_cache(self, source_id, max_age_hours=1):
        filename = f"{self.cache_dir}/{source_id}.json"
        if not os.path.exists(filename):
            return None
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            updated = datetime.fromisoformat(data['updated'])
            age = (datetime.now() - updated).total_seconds() / 3600
            
            if age > max_age_hours:
                return None
            
            return data['products']
        except:
            return None
    
    def get_cache_status(self):
        status = {}
        if not os.path.exists(self.cache_dir):
            return status
        
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(self.cache_dir, filename), 'r') as f:
                        data = json.load(f)
                    source_id = filename.replace('.json', '')
                    status[source_id] = {'count': data['count']}
                except:
                    pass
        return status
