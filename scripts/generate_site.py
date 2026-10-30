
import json, feedparser
from pathlib import Path
from llama_cpp import Llama

# Konfiguration
MODEL_PATH = "/Users/agenten/copilot-dashboard/models/Qwen2.5-7B-Instruct-Q4_K_M.gguf"
llm = Llama(model_path=MODEL_PATH, n_ctx=2048, verbose=False)

def analyze_headline(headline):
    prompt = f"Kategorisér følgende nyhedsoverskrift: '{headline}'. Svar kun med én kategori (fx AI, Tech, Finans)."
    res = llm.create_chat_completion(messages=[{"role": "user", "content": prompt}], max_tokens=20)
    return res['choices'][0]['message']['content'].strip()

ROOT = Path('/Users/agenten/copilot-dashboard')
def main():
    sources = json.loads((ROOT / 'sources.json').read_text())['sources']
    all_items = []
    for s in sources:
        feed = feedparser.parse(s['feedUrl'])
        for entry in feed.entries[:5]:
            # Brug kildens faste kategori - vi tvinger den nu igennem
            all_items.append({'title': entry.title, 'link': entry.link, 'category': s['category']})
    (ROOT / 'updates.json').write_text(json.dumps(all_items), encoding='utf-8')

main()
