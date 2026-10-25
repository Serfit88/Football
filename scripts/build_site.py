"""Package only public site files and record the source commit."""
from pathlib import Path
from datetime import datetime, timezone
import json
import os
import shutil

root = Path(__file__).resolve().parents[1]
out = root / '_site'
out.mkdir(exist_ok=True)
for name in ['index.html', 'style.css', 'main.js', 'accessibility.css', '.nojekyll', 'IMAGE_SOURCES.md']:
    shutil.copy2(root / name, out / name)
for name in ['images', 'assets']:
    if (root / name).is_dir():
        shutil.copytree(root / name, out / name, dirs_exist_ok=True)
info = {'commit': os.environ.get('GITHUB_SHA', 'local'),
        'run_id': os.environ.get('GITHUB_RUN_ID', 'local'),
        'built_at': datetime.now(timezone.utc).isoformat()}
(out / 'build-info.json').write_text(json.dumps(info, indent=2), encoding='utf-8')
print('Packaged site in _site; source commit:', info['commit'])
