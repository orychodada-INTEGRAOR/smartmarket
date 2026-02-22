import gzip
import xml.etree.ElementTree as ET
from datetime import datetime

class DataProcessor:

    def process_gz(self, gz_bytes):
        xml_data = gzip.decompress(gz_bytes)
        root = ET.fromstring(xml_data)

        products = []
        prices = []

        chain_id = root.attrib.get("ChainId")
        store_id = root.attrib.get("StoreId")

        for item in root.findall(".//Item"):
            barcode = item.findtext("ItemCode")
            name = item.findtext("ItemName")
            manufacturer = item.findtext("ManufacturerName")
            quantity = item.findtext("Quantity")
            price = item.findtext("ItemPrice")

            products.append({
                "barcode": barcode,
                "name": name,
                "manufacturer": manufacturer,
                "unit_quantity": quantity
            })

            prices.append({
                "chain_id": chain_id,
                "store_id": store_id,
                "barcode": barcode,
                "price": price,
                "updated_at": datetime.utcnow()
            })

        return products, prices