
import json, shutil, subprocess, os
from pathlib import Path

ROOT = Path('.')
DIST = ROOT / 'dist'

def main():
    DIST.mkdir(exist_ok=True)
    
    # Run blogwatcher scan (assumes it is installed in the runner)
    # If it fails, we write an empty list.
    try:
        subprocess.run(['blogwatcher-cli', 'scan'], check=True, capture_output=True)
        result = subprocess.run(['blogwatcher-cli', 'articles', '--json'], check=True, capture_output=True)
        items = json.loads(result.stdout)
    except Exception as e:
        print(f"Blogwatcher error: {e}")
        items = []

    (DIST / 'updates.json').write_text(json.dumps(items), encoding='utf-8')
    (DIST / 'version.json').write_text(json.dumps({'version': '1.0.0', 'buildTime': 123456789}), encoding='utf-8')
    
    for name in ['index.html', 'app.js', 'manifest.json', 'icon.svg', 'CNAME']:
        shutil.copy2(ROOT / name, DIST / name)

if __name__ == '__main__':
    main()
