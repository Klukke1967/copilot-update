
import json, time, shutil, urllib.request, xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path('.')
DIST = ROOT / 'dist'

def fetch_feed(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=20) as res:
            return res.read().decode('utf-8', errors='replace')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def main():
    DIST.mkdir(exist_ok=True)
    sources_data = json.loads((ROOT / 'sources.json').read_text())
    
    all_items = []
    for s in sources_data['sources']:
        xml = fetch_feed(s['feedUrl'])
        if xml:
            try:
                root = ET.fromstring(xml)
                nodes = root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry')
                for item in nodes:
                    title = (item.find('title') if item.find('title') is not None else item.find('{http://www.w3.org/2005/Atom}title')).text
                    link = (item.find('link').attrib.get('href') if item.find('link') is not None and 'href' in item.find('link').attrib else item.find('link').text)
                    all_items.append({'title': title, 'link': link, 'source': s['name']})
            except Exception as e:
                print(f"Parsing error for {s['name']}: {e}")
    
    (DIST / 'updates.json').write_text(json.dumps(all_items), encoding='utf-8')
    (DIST / 'sources.json').write_text(json.dumps(sources_data), encoding='utf-8')
    (DIST / 'version.json').write_text(json.dumps({'version': '1.0.0', 'buildTime': int(time.time() * 1000)}), encoding='utf-8')
    
    for name in ['index.html', 'app.js', 'manifest.json', 'icon.svg', 'CNAME']:
        if (ROOT / name).exists(): shutil.copy2(ROOT / name, DIST / name)

main()
