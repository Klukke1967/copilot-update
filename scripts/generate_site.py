import json, feedparser, time
from pathlib import Path

ROOT = Path('.')

def main():
    sources = json.loads((ROOT / 'sources.json').read_text())['sources']
    all_items = []
    for s in sources:
        feed = feedparser.parse(s['feedUrl'])
        for entry in feed.entries[:5]:
            all_items.append({
                'title': entry.get('title', 'Uden titel'),
                'summary': entry.get('summary', 'Ingen beskrivelse')[:200],
                'link': entry.get('link', '#'),
                'source': s['name']
            })
    (ROOT / 'updates.json').write_text(json.dumps(all_items), encoding='utf-8')
    (ROOT / 'version.json').write_text(json.dumps({'version': '1.0.0', 'buildTime': int(time.time() * 1000)}), encoding='utf-8')

if __name__ == '__main__':
    main()
