
import json, time, shutil
from pathlib import Path
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path('.')
DIST = ROOT / 'dist'

def fetch_feed(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as res:
            return res.read().decode('utf-8', errors='replace')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def parse_rss(xml_string, category):
    items = []
    try:
        root = ET.fromstring(xml_string)
        # Prøv både item (RSS) og entry (Atom)
        nodes = root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry')
        for item in nodes:
            title = (item.find('title') if item.find('title') is not None else item.find('{http://www.w3.org/2005/Atom}title')).text
            link = (item.find('link').attrib.get('href') if item.find('link') is not None and 'href' in item.find('link').attrib else item.find('link').text)
            items.append({'title': title, 'link': link, 'category': category})
    except Exception as e:
        print(f"Parsing error: {e}")
    return items

def main():
    DIST.mkdir(exist_ok=True)
    sources = json.loads((ROOT / 'sources.json').read_text())['sources']
    all_items = []
    for s in sources:
        xml = fetch_feed(s['feedUrl'])
        if xml:
            all_items.extend(parse_rss(xml, s['category']))
    
    (DIST / 'updates.json').write_text(json.dumps(all_items), encoding='utf-8')
    for name in ['index.html', 'app.js', 'manifest.json', 'icon.svg', 'CNAME']:
        shutil.copy2(ROOT / name, DIST / name)

main()
