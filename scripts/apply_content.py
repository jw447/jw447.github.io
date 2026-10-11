#!/usr/bin/env python3
"""Apply a downloaded editor draft after validating and rebuilding the site."""
import argparse
import json
from editor_server import Editor, EditorError, ROOT

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('draft', help='Path to HPDi-content-updates.json')
args = parser.parse_args()
try:
    with open(args.draft) as source: payload = json.load(source)
    result = Editor(ROOT).save(payload)
    print('Saved and checked: ' + (', '.join(result['changed']) or 'no changes'))
except (EditorError, ValueError, OSError) as error:
    parser.exit(1, str(error) + '\n')
