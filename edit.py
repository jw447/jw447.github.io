#!/usr/bin/env python3
"""Pull GitHub/main, then open the content editor on local-design."""
from pathlib import Path
import subprocess
import sys
root = Path(__file__).resolve().parent
print('Synchronizing GitHub before opening the editor…', flush=True)
result = subprocess.call([sys.executable, str(root / 'scripts/sync_editor.py')], cwd=root)
if result: raise SystemExit(result)
raise SystemExit(subprocess.call([sys.executable, str(root / 'scripts/editor_server.py'), '--open', *sys.argv[1:]], cwd=root))
