
import json, time
from pathlib import Path
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone
import urllib.request
from xml.etree import ElementTree as ET

ROOT = Path('/Users/agenten/copilot-dashboard')

def load_sources():
    return json.loads((ROOT / 'sources.json').read_text())['sources']

def fetch_feed(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as res:
        return res.read().decode('utf-8', errors='replace')

def parse_feed(source):
    items = []
    xml = fetch_feed(source['feedUrl'])
    root = ET.fromstring(xml)
    for item in root.findall('.//item') or root.findall('.//entry'):
        title = (item.find('title') or item.find('{http://www.w3.org/2005/Atom}title')).text
        link = (item.find('link') or item.find('{http://www.w3.org/2005/Atom}link')).attrib.get('href') or (item.find('link').text if item.find('link') is not None else "")
        published = (item.find('pubDate') or item.find('{http://www.w3.org/2005/Atom}published') or item.find('{http://www.w3.org/2005/Atom}updated')).text
        items.append({'title': title, 'link': link, 'published': published, 'category': source['category']})
    return items

def main():
    sources = load_sources()
    all_items = []
    for s in sources:
        try:
            all_items.extend(parse_feed(s))
        except: pass
    
    # Gem resultatet DIREKTE i roden
    (ROOT / 'updates.json').write_text(json.dumps(all_items), encoding='utf-8')
    (ROOT / 'version.json').write_text(json.dumps({'version': '1.0.0', 'buildTime': int(time.time() * 1000)}), encoding='utf-8')

main()
