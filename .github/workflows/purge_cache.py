import json
import subprocess
import sys
import tarfile

for bundle_path in sys.argv[1:]:
    if not bundle_path.endswith('.klyx'):
        continue
    with tarfile.open(bundle_path, 'r:gz') as t:
        meta = json.loads(t.extractfile('plugin.json').read())
    pid = meta['id']
    ver = meta['version']
    paths = [
        f'{pid}/{ver}.klyx',
        f'{pid}/metadata.json',
        f'{pid}/icon.png',
        f'{pid}/readme.md',
        f'{pid}/changelog.md',
    ]
    for path in paths:
        url = f'https://purge.jsdelivr.net/gh/klyx-dev/plugins@main/plugins/{path}'
        subprocess.run(['curl', '-s', url], capture_output=True)
