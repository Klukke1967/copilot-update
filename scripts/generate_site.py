#!/usr/bin/env python3
"""
AI Intelligence Hub - Site Generator
Henter nyheder og videoer for Microsoft Copilot, Claude (Anthropic) og ChatGPT (OpenAI).
Genererer updates.json og opdaterer version.json.
"""

import json
import re
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
import feedparser

ROOT = Path(__file__).resolve().parent.parent
SOURCES_FILE = ROOT / "sources.json"
UPDATES_FILE = ROOT / "updates.json"
VERSION_FILE = ROOT / "version.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

DANISH_MONTHS = ["jan.", "feb.", "mar.", "apr.", "maj", "jun.", "jul.", "aug.", "sep.", "okt.", "nov.", "dec."]

TAG_RULES = {
    'm365': {
        'label': 'Copilot & M365',
        'keywords': ['excel', 'word', 'powerpoint', 'teams', 'sharepoint', 'outlook', 'office', 'productivity', 'data in excel', 'spreadsheet', 'workspace', 'crm', 'copilot dashboard']
    },
    'leadership': {
        'label': 'Ledelse & Strategi',
        'keywords': ['enterprise', 'business', 'governance', 'security', 'compliance', 'company', 'organization', 'roi', 'policy', 'strategy', 'leadership', 'management', 'adoption', 'risk', 'trust', 'cyber', 'vulnerabilit', 'safety', 'threat']
    },
    'developer': {
        'label': 'Udvikling & Agenter',
        'keywords': ['code', 'coding', 'agent', 'api', 'sdk', 'developer', 'engineer', 'python', 'computer use', 'automation', 'hacktron', 'software', 'graduates']
    },
    'research': {
        'label': 'Forskning & Modeller',
        'keywords': ['research', 'biology', 'science', 'reasoning', 'benchmark', 'paper', 'eval', 'laboratory', 'frontier', 'particle', 'experiment', 'wet-lab', 'scientific']
    }
}

def classify_tags(title: str, summary: str, category: str, source: str) -> list:
    text = f"{title} {summary}".lower()
    tags = []
    for tag_id, tag_data in TAG_RULES.items():
        if any(kw in text for kw in tag_data['keywords']):
            tags.append(tag_id)
    if not tags:
        if category == 'copilot':
            tags.append('m365')
        elif 'research' in source.lower():
            tags.append('research')
        elif 'blog' in source.lower():
            tags.append('developer')
        else:
            tags.append('leadership')
    return tags

def clean_text(html_text: str, max_len: int = 180) -> str:
    if not html_text:
        return ""
    text = re.sub(r"<[^>]+>", " ", html_text)
    text = " ".join(text.split())
    if len(text) > max_len:
        return text[:max_len].rstrip() + "..."
    return text

def extract_youtube_thumb(url: str) -> str:
    if not url:
        return ""
    # Check v= parameter
    m = re.search(r"[?&]v=([a-zA-Z0-9_-]+)", url)
    if m:
        return f"https://img.youtube.com/vi/{m.group(1)}/hqdefault.jpg"
    # Check shorts or embed
    m2 = re.search(r"/(?:shorts|embed|v)/([a-zA-Z0-9_-]+)", url)
    if m2:
        return f"https://img.youtube.com/vi/{m2.group(1)}/hqdefault.jpg"
    return ""

def format_date_da(dt: datetime) -> str:
    month_str = DANISH_MONTHS[dt.month - 1]
    return f"{dt.day}. {month_str} {dt.year}"

def main():
    if not SOURCES_FILE.exists():
        print(f"Error: {SOURCES_FILE} not found.")
        return

    data = json.loads(SOURCES_FILE.read_text(encoding="utf-8"))
    sources = data.get("sources", [])

    all_items = []
    seen_links = set()

    for s in sources:
        name = s.get("name", "Ukendt kilde")
        cat = s.get("category", "copilot").lower()
        feed_url = s.get("feedUrl", "")
        item_type = s.get("type", "article")

        print(f"Henter {name} ({cat})...")
        try:
            req = urllib.request.Request(feed_url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=12) as resp:
                content = resp.read()
                feed = feedparser.parse(content)

                entries = feed.entries[:15]
                for e in entries:
                    link = getattr(e, "link", "").strip()
                    title = getattr(e, "title", "").strip()
                    if not link or not title:
                        continue

                    # Deduplication
                    norm_link = link.split("?")[0].rstrip("/")
                    if norm_link in seen_links:
                        continue
                    seen_links.add(norm_link)

                    # Date parsing
                    parsed_time = getattr(e, "published_parsed", None) or getattr(e, "updated_parsed", None)
                    if parsed_time:
                        dt = datetime.fromtimestamp(time.mktime(parsed_time), tz=timezone.utc)
                    else:
                        dt = datetime.now(timezone.utc)

                    iso_date = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
                    formatted_date = format_date_da(dt)

                    # Summary & thumbnail
                    raw_summary = getattr(e, "summary", "") or getattr(e, "description", "")
                    summary = clean_text(raw_summary)

                    is_youtube = ("youtube.com" in link) or ("youtu.be" in link) or (item_type == "youtube")
                    thumb = extract_youtube_thumb(link) if is_youtube else ""
                    tags = classify_tags(title, summary, cat, name)

                    all_items.append({
                        "id": f"{cat}_{abs(hash(norm_link)) % 10000000}",
                        "title": title,
                        "link": link,
                        "category": cat,
                        "tags": tags,
                        "source": name,
                        "type": "youtube" if is_youtube else "article",
                        "published_at": iso_date,
                        "display_date": formatted_date,
                        "summary": summary,
                        "thumbnail": thumb
                    })
        except Exception as ex:
            print(f"Fejl ved {name} ({feed_url}): {ex}")

    # Sort descending by published_at
    all_items.sort(key=lambda x: x["published_at"], reverse=True)

    print(f"Total unikke artikler/videoer indsamlet: {len(all_items)}")

    # Gem updates.json
    UPDATES_FILE.write_text(json.dumps(all_items, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Gemt i {UPDATES_FILE}")

    # Opdater version.json
    now = datetime.now(timezone.utc)
    version_payload = {
        "version": now.strftime("%Y.%m.%d.%H%M%S"),
        "timestamp": now.isoformat(),
        "item_count": len(all_items)
    }
    VERSION_FILE.write_text(json.dumps(version_payload, indent=2), encoding="utf-8")
    print(f"Opdateret version: {version_payload['version']}")

    # Synkroniser til dist/ hvis mappen findes
    dist_dir = ROOT / "dist"
    if dist_dir.exists():
        import shutil
        for fname in ["updates.json", "version.json", "index.html", "manifest.json", "icon.svg", "sw.js", "CNAME"]:
            src = ROOT / fname
            if src.exists():
                shutil.copy2(src, dist_dir / fname)
        print("Synkroniseret filer til dist/")

if __name__ == "__main__":
    main()
