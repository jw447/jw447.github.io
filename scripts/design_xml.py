#!/usr/bin/env python3
"""Export current design XML or safely import XML and rebuild the website."""
import argparse
from pathlib import Path
from editor_server import Editor, EditorError, ROOT
from editor.content import bundle
from editor.design_xml import MAX_XML_BYTES, from_xml, to_xml


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['export', 'import'])
    parser.add_argument('file', type=Path)
    args = parser.parse_args()
    try:
        payload = bundle(ROOT)
        if args.action == 'export':
            args.file.write_text(to_xml(payload['content']['design']), encoding='utf-8')
            print(f'Exported current design to {args.file}')
        else:
            if args.file.stat().st_size > MAX_XML_BYTES:
                raise ValueError('Choose a design XML file smaller than 64 KiB.')
            payload['content']['design'] = from_xml(args.file.read_text(encoding='utf-8-sig'))
            result = Editor(ROOT).save(payload)
            print('Saved and checked: ' + (', '.join(result['changed']) or 'no changes'))
    except (EditorError, ValueError, OSError) as error:
        parser.exit(1, str(error) + '\n')


if __name__ == '__main__':
    main()
