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
        """
        אתחול המעבד
        
        Args:
            cache_dir: תיקייה לשמירת נתונים זמניים
        """
        self.cache_dir = cache_dir
        # יצירת תיקיית cache אם לא קיימת
        Path(cache_dir).mkdir(exist_ok=True)
    
  def process_gz(self, gz_content):
    """
    מעבד קובץ GZ או JSON ומחזיר רשימת מוצרים
    """
    try:
        # בדיקה אם זה JSON (kingstore מחזיר JSON ישירות)
        if gz_content.startswith(b'[{') or gz_content.startswith(b'{'):
            # זה JSON - פרסור ישיר
            import json
            data = json.loads(gz_content.decode('utf-8'))
            
            # אם זה רשימה - זה כבר המוצרים
            if isinstance(data, list):
                products = []
                for item in data:
                    product = {
                        'id': item.get('ItemCode', ''),
                        'name': item.get('ItemNm', ''),
                        'price': float(item.get('ItemPrice', 0)),
                        'manufacturer': item.get('ManufacturerName', ''),
                        'unit_measure': item.get('UnitOfMeasure', ''),
                        'quantity': item.get('Quantity', ''),
                        'unit_price': float(item.get('UnitOfMeasurePrice', 0)),
                        'country': item.get('ManufactureCountry', ''),
                        'allow_discount': item.get('AllowDiscount') == '1',
                        'update_date': item.get('PriceUpdateDate', ''),
                        'chain_id': item.get('ChainId', ''),
                        'store_id': item.get('StoreId', ''),
                        'timestamp': datetime.now().isoformat()
                    }
                    products.append(product)
                
                print(f"✅ עובדו {len(products)} מוצרים מ-JSON")
                return products
        
        # אם זה לא JSON - נסה כ-GZ רגיל
        # שלב 1: פתיחת הדחיסה
        xml_content = gzip.decompress(gz_content).decode('utf-8')
            
            # שלב 2: פרסור XML
            root = ET.fromstring(xml_content)
            
            # שלב 3: חילוץ מידע על החנות
            chain_id = self.get_text(root, 'ChainId')
            store_id = self.get_text(root, 'StoreId')
            
            # שלב 4: עיבוד המוצרים
            products = []
            for item in root.findall('.//Item'):
                product = {
                    'id': self.get_text(item, 'ItemCode'),
                    'name': self.get_text(item, 'ItemNm'),
                    'price': self.get_float(item, 'ItemPrice'),
                    'manufacturer': self.get_text(item, 'ManufacturerName'),
                    'unit_measure': self.get_text(item, 'UnitOfMeasure'),
                    'quantity': self.get_text(item, 'Quantity'),
                    'unit_price': self.get_float(item, 'UnitOfMeasurePrice'),
                    'country': self.get_text(item, 'ManufactureCountry'),
                    'allow_discount': self.get_text(item, 'AllowDiscount') == '1',
                    'update_date': self.get_text(item, 'PriceUpdateDate'),
                    'chain_id': chain_id,
                    'store_id': store_id,
                    'timestamp': datetime.now().isoformat()
                }
                products.append(product)
            
            print(f"✅ עובדו {len(products)} מוצרים מחנות {store_id}")
            return products
            
        except Exception as e:
            print(f"❌ שגיאה בעיבוד: {e}")
            return []
    
    def get_text(self, element, tag, default=''):
        """מחזיר טקסט מתגית XML או ערך ברירת מחדל"""
        child = element.find(tag)
        return child.text if child is not None and child.text else default
    
    def get_float(self, element, tag, default=0.0):
        """מחזיר מספר מתגית XML או 0"""
        text = self.get_text(element, tag)
        try:
            return float(text) if text else default
        except ValueError:
            return default
    
    def save_to_cache(self, products, source_id):
        """
        שומר מוצרים לקובץ JSON
        
        Args:
            products: רשימת מוצרים
            source_id: מזהה המקור (למשל 'store1')
        """
        filename = f"{self.cache_dir}/{source_id}.json"
        
        data = {
            'products': products,
            'updated': datetime.now().isoformat(),
            'count': len(products),
            'source': source_id
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 נשמרו {len(products)} מוצרים ב-{filename}")
    
    def load_from_cache(self, source_id, max_age_hours=1):
        """
        טוען מוצרים מקובץ JSON אם לא ישן מדי
        
        Args:
            source_id: מזהה המקור
            max_age_hours: גיל מקסימלי בשעות (ברירת מחדל: 1 שעה)
            
        Returns:
            list or None: רשימת מוצרים או None אם אין/ישן
        """
        filename = f"{self.cache_dir}/{source_id}.json"
        
        # בדיקה אם הקובץ קיים
        if not os.path.exists(filename):
            print(f"⚠️ אין cache עבור {source_id}")
            return None
        
        try:
            # קריאת הקובץ
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # בדיקת גיל
            updated = datetime.fromisoformat(data['updated'])
            age_hours = (datetime.now() - updated).total_seconds() / 3600
            
            if age_hours > max_age_hours:
                print(f"⏰ Cache ישן ({age_hours:.1f} שעות) עבור {source_id}")
                return None
            
            print(f"✅ נטען cache טרי ({age_hours:.0f} דקות) עבור {source_id}")
            return data['products']
            
        except Exception as e:
            print(f"❌ שגיאה בקריאת cache: {e}")
            return None
    
    def get_cache_status(self):
        """מחזיר סטטוס של כל קבצי ה-cache"""
        status = {}
        
        if not os.path.exists(self.cache_dir):
            return status
        
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.cache_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    source_id = filename.replace('.json', '')
                    updated = datetime.fromisoformat(data['updated'])
                    age_hours = (datetime.now() - updated).total_seconds() / 3600
                    
                    status[source_id] = {
                        'count': data['count'],
                        'updated': data['updated'],
                        'age_hours': round(age_hours, 1),
                        'fresh': age_hours < 1
                    }
                except:
                    pass
        
        return status
