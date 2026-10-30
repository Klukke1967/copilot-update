
import json, feedparser
from pathlib import Path

# AI-delen fjernes for at gøre deployment robust på GitHub Pages
ROOT = Path('/Users/agenten/copilot-dashboard')

def main():
    sources = json.loads((ROOT / 'sources.json').read_text())['sources']
    all_items = []
    for s in sources:
        feed = feedparser.parse(s['feedUrl'])
        for entry in feed.entries[:5]:
            # Brug kildens faste kategori - dette er stabilt og kræver ingen AI-modeller
            all_items.append({'title': entry.title, 'link': entry.link, 'category': s['category']})
    (ROOT / 'updates.json').write_text(json.dumps(all_items), encoding='utf-8')

main()
