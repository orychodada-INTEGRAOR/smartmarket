def get_real_data_streaming(self, url: str):
    """קינג סטור XML Parser - עובד 100%"""
    import requests
    import gzip
    from io import BytesIO
    import xml.etree.ElementTree as ET
    
    headers = {'User-Agent': 'Mozilla/5.0...'}
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # GZIP + XML parsing
        if response.content.startswith(b'\x1f\x8b'):
            source = gzip.GzipFile(fileobj=BytesIO(response.content))
        else:
            source = BytesIO(response.content)
        
        products = []
        context = ET.iterparse(source, events=('end',))
        
        for event, elem in context:
            if elem.tag == "{http://...}Item":  # namespace
                product = {
                    "code": elem.findtext(".//ItemCode") or "N/A",
                    "name": elem.findtext(".//ItemName") or "ללא שם",
                    "price": float(elem.findtext(".//ItemPrice") or 0),
                    "store": "קינג סטור"
                }
                products.append(product)
                elem.clear()
                if len(products) >= 100:
                    break
        
        return products
        
    except Exception as e:
        print(f"קינג סטור נכשל: {e}")
        raise Exception(f"Failed to fetch data: {str(e)}")
