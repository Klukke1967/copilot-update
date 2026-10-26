
import json, time, urllib.request, xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path('.')
DIST = ROOT / 'dist'

def fetch_feed(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=20) as res:
            return res.read().decode('utf-8', errors='replace')
    except: return None

def main():
    items = []
    # Kilde: Microsoft 365 GA nyheder (den vi ved virker)
    xml = fetch_feed('https://www.microsoft.com/en-us/microsoft-365/blog/feed/')
    if xml:
        root = ET.fromstring(xml)
        for item in root.findall('.//item')[:10]:
            items.append({
                'title': item.find('title').text,
                'link': item.find('link').text,
                'category': 'Copilot'
            })
    
    # Gem direkte
    (DIST / 'updates.json').write_text(json.dumps(items), encoding='utf-8')

if __name__ == '__main__':
    main()
