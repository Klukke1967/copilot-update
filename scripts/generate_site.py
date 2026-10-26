#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
SOURCES = ROOT / 'sources.json'


def load_sources():
    with SOURCES.open('r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('sources', [])


def parse_dt(value: str | None):
    if not value:
        return None
    try:
        return parsedate_to_datetime(value).astimezone(timezone.utc)
    except Exception:
        try:
            return datetime.fromisoformat(value.replace('Z', '+00:00')).astimezone(timezone.utc)
        except Exception:
            return None


def fetch_xml(url: str) -> str:
    req = urllib.request.Request(url, headers={'User-Agent': 'CopilotDashboard/1.0'})
    with urllib.request.urlopen(req, timeout=25) as res:
        return res.read().decode('utf-8', errors='replace')


def text(node, path, default=''):
    found = node.find(path)
    return (found.text or '').strip() if found is not None and found.text else default


def parse_feed(source):
    xml = fetch_xml(source['feedUrl'])
    root = ET.fromstring(xml)
    items = []

    channel = root.find('channel')
    if channel is not None:
        for item in channel.findall('item'):
            title = text(item, 'title')
            link = text(item, 'link')
            summary = text(item, 'description') or text(item, '{http://www.w3.org/2005/Atom}summary')
            published = text(item, 'pubDate')
            dt = parse_dt(published)
            items.append({
                'source': source['name'],
                'title': title,
                'link': link,
                'summary': summary,
                'published': dt.isoformat() if dt else published,
                'fetchedAt': datetime.now(timezone.utc).isoformat(),
            })
        return items

    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    for entry in root.findall('atom:entry', ns):
        title = text(entry, 'atom:title')
        link_el = entry.find('atom:link', ns)
        link = link_el.attrib.get('href', '') if link_el is not None else ''
        summary = text(entry, 'atom:summary') or text(entry, 'atom:content')
        published = text(entry, 'atom:published') or text(entry, 'atom:updated')
        dt = parse_dt(published)
        items.append({
            'source': source['name'],
            'title': title,
            'link': link,
            'summary': summary,
            'published': dt.isoformat() if dt else published,
            'fetchedAt': datetime.now(timezone.utc).isoformat(),
        })
    return items


def main():
    DIST.mkdir(exist_ok=True)
    sources = load_sources()
    all_items = []
    statuses = []
    now = datetime.now(timezone.utc).isoformat()

    for source in sources:
        try:
            items = parse_feed(source)
            all_items.extend(items[:8])
            statuses.append({
                'name': source['name'],
                'feedUrl': source['feedUrl'],
                'homepage': source.get('homepage', source['feedUrl']),
                'ok': True,
                'count': len(items),
            })
        except Exception as exc:
            statuses.append({
                'name': source['name'],
                'feedUrl': source['feedUrl'],
                'homepage': source.get('homepage', source['feedUrl']),
                'ok': False,
                'error': str(exc),
            })

    def item_sort_key(item):
        dt = parse_dt(item.get('published') or item.get('fetchedAt'))
        return dt or datetime.min.replace(tzinfo=timezone.utc)

    all_items.sort(key=item_sort_key, reverse=True)

    payload = {
        'generatedAt': now,
        'sources': statuses,
        'items': all_items[:20],
    }

    (DIST / 'updates.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    (DIST / 'version.json').write_text(json.dumps({'version': '1.0.0', 'buildTime': int(time.time() * 1000), 'generatedAt': now}, ensure_ascii=False, indent=2), encoding='utf-8')

    for name in ['index.html', 'app.js', 'manifest.json', 'sw.js', 'icon.svg', 'CNAME']:
        shutil.copy2(ROOT / name, DIST / name)

    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
