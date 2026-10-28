
import json, urllib.request, xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path('.')
DIST = ROOT / 'dist'
M6_URL = "http://192.168.68.62:11434/v1/chat/completions"
API_KEY = "Ollama"

def get_summary(text):
    data = {
        "model": "qwen2.5:14b",
        "messages": [{"role": "user", "content": f"Opsummer dette på dansk (max 3 linjer, teknisk dybde, kun GA): {text}"}]
    }
    req = urllib.request.Request(M6_URL, data=json.dumps(data).encode(), headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())['choices'][0]['message']['content']
    except: return text[:150]

def main():
    DIST.mkdir(exist_ok=True)
    items = []
    xml = urllib.request.urlopen("https://www.microsoft.com/en-us/copilot/blog/feed/", timeout=15).read()
    root = ET.fromstring(xml)
    for item in root.findall('.//item')[:3]:
        items.append({
            'title': item.find('title').text,
            'summary': get_summary(item.find('description').text),
            'link': item.find('link').text
        })
    (DIST / 'updates.json').write_text(json.dumps(items), encoding='utf-8')

main()
