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
import hashlib
from datetime import datetime, timezone
from pathlib import Path
import feedparser

ROOT = Path(__file__).resolve().parent.parent
SOURCES_FILE = ROOT / "sources.json"
UPDATES_FILE = ROOT / "updates.json"
VERSION_FILE = ROOT / "version.json"
SUMMARIES_CACHE_FILE = ROOT / "summaries_cache.json"

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

def normalize_link(link: str) -> str:
    if not link:
        return ""
    m = re.search(r"[?&]v=([a-zA-Z0-9_-]+)", link)
    if m:
        return f"https://www.youtube.com/watch?v={m.group(1)}"
    m2 = re.search(r"/(?:shorts|embed|v)/([a-zA-Z0-9_-]+)", link)
    if m2:
        return f"https://www.youtube.com/shorts/{m2.group(1)}"
    return link.split("?")[0].rstrip("/")

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

def fetch_url_with_retry(url: str, max_retries: int = 5) -> bytes:
    last_err = None
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    return resp.read()
        except Exception as e:
            last_err = e
            time.sleep(0.4 * (attempt + 1))
    raise last_err or Exception(f"Kunne ikke hente {url}")

def build_fallback_tldr(title: str, summary: str, cat: str, source: str, tags: list) -> str:
    t_lower = title.lower()
    s_lower = summary.lower()
    
    if "excel" in t_lower or "excel" in s_lower:
        return f"Praktisk vejledning fra {source} med fokus på Copilot i Excel til dataanalyse, formler og tidsbesparelse."
    elif "dashboard" in t_lower or "powerpoint" in t_lower:
        return f"Vejledning fra {source} om opbygning af dashboards og præsentationer med Microsoft Copilot."
    elif "copilot" in t_lower or cat == "copilot":
        return f"Gennemgang fra {source} af nye Copilot-funktioner, modelindstillinger og praktisk udrulning i M365."
    elif "claude" in t_lower or cat == "claude":
        if "research" in source.lower() or "research" in tags:
            return f"Forskningsopdatering fra Anthropic om modelkapacitet, videnskabelige benchmarks og AI-sikkerhed."
        return f"Seneste annoncering fra Anthropic om Claude og praktiske forretningsmuligheder."
    elif cat == "chatgpt":
        if "video" in source.lower() or "youtube" in source.lower():
            return f"Videodemonstration fra OpenAI med fokus på nye modelfunktioner og problemløsning med ChatGPT."
        return f"Officiel opdatering fra OpenAI om modeludvikling, systemopgraderinger og AI-agenter."
    return f"Væsentlig opdatering fra {source} om de seneste fremskridt inden for kunstig intelligens."

def check_llm_available() -> bool:
    try:
        req = urllib.request.Request("http://192.168.68.62:11434/api/tags")
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            return resp.status == 200
    except Exception:
        return False

def get_danish_tldr(item: dict, cache: dict, allow_llm: bool = True) -> str:
    item_id = item["id"]
    if item_id in cache and cache[item_id] and len(cache[item_id]) > 15:
        return cache[item_id]

    title = item["title"]
    summary = item.get("summary", "")
    source = item.get("source", "")
    cat = item.get("category", "")
    tags = item.get("tags", [])

    if allow_llm:
        try:
            prompt = (
                f"Du er en skarp dansk AI-redaktør for ledere og specialister.\n"
                f"Giv en ultrakort og præcis opsummering på 1-2 linjer på naturligt dansk af følgende:\n"
                f"Titel: {title}\n"
                f"Kilde: {source}\n"
                f"Uddrag: {summary}\n\n"
                f"Svar KUN med opsummeringen på dansk, uden overskrifter eller citationstegn:"
            )
            req_data = {
                "model": "qwen2.5:14b",
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.2, "num_predict": 85}
            }
            req = urllib.request.Request(
                "http://192.168.68.62:11434/api/generate",
                data=json.dumps(req_data).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                ans = data.get("response", "").strip()
                if ans and len(ans) > 20 and not re.search(r'[\u4e00-\u9fff]', ans):
                    clean_ans = re.sub(r'^(TL;DR|Opsummering|Resum[eé]):\s*', '', ans, flags=re.I)
                    cache[item_id] = clean_ans
                    return clean_ans
        except Exception:
            pass

    fallback = build_fallback_tldr(title, summary, cat, source, tags)
    cache[item_id] = fallback
    return fallback

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
            content = fetch_url_with_retry(feed_url, max_retries=5)
            feed = feedparser.parse(content)

            entries = feed.entries[:15]
            for e in entries:
                link = getattr(e, "link", "").strip()
                title = getattr(e, "title", "").strip()
                if not link or not title:
                    continue

                # Deduplication
                norm_link = normalize_link(link)
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
                item_hash = hashlib.md5(norm_link.encode("utf-8")).hexdigest()[:8]

                all_items.append({
                    "id": f"{cat}_{item_hash}",
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

    # Indlæs eksisterende nyheder, så vi aldrig mister historik hvis et feed fejler midlertidigt
    existing_items_map = {}
    if UPDATES_FILE.exists():
        try:
            prev_data = json.loads(UPDATES_FILE.read_text(encoding="utf-8"))
            for item in prev_data:
                existing_items_map[item["id"]] = item
        except Exception:
            pass

    # Flet nye items ind
    for item in all_items:
        existing_items_map[item["id"]] = item

    merged_items = list(existing_items_map.values())
    merged_items.sort(key=lambda x: x["published_at"], reverse=True)
    all_items = merged_items[:200]

    # Hent eller opret resumé-cache
    cache = {}
    if SUMMARIES_CACHE_FILE.exists():
        try:
            cache = json.loads(SUMMARIES_CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:
            cache = {}

    llm_online = check_llm_available()
    print(f"Lokal LLM (Qwen2.5) status: {'Online' if llm_online else 'Offline/Fjern'}")
    print(f"Genererer/tilknytter danske TL;DR opsummeringer (tidligere cachet: {len(cache)})...")
    for idx, item in enumerate(all_items):
        allow_llm = llm_online and ((idx < 35) or (item["id"] not in cache))
        item["tldr_da"] = get_danish_tldr(item, cache, allow_llm=allow_llm)

    SUMMARIES_CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Gemt {len(cache)} resuméer i {SUMMARIES_CACHE_FILE}")

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
        for fname in ["updates.json", "version.json", "prompts.json", "index.html", "manifest.json", "icon.svg", "sw.js", "CNAME"]:
            src = ROOT / fname
            if src.exists():
                shutil.copy2(src, dist_dir / fname)
        print("Synkroniseret filer til dist/")

if __name__ == "__main__":
    main()
