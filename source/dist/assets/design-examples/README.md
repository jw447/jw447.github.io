# Design XML snapshots

`design-palatino.xml` preserves the design before the Optima trial. `design-optima.xml` exports the current trial. These are snapshots, not active sources. `content/design.json` remains authoritative; the build exports its current values to `/assets/design.xml`.

In `/admin/?tab=design`, choose **Import design XML**, preview the result, and use **Save files** in the local editor. **Export design XML** downloads the current draft, including unsaved design edits. Imports change design settings only and preserve website content.

The root must be `<website-design version="1">`. All five groups and their documented attributes are required. Numbers have no units; colors are six-digit hex values. Allowed font identifiers: `optima`, `palatino`, `source-sans`, `inter`, `plex`, `source-serif`. Layout, spacing, type sizes, and contrast use the same limits as the editor. Arbitrary HTML, CSS, document types, and entity declarations are rejected. Files must be at most 64 KiB.

Optima uses an installed system font, followed by Candara and the locally hosted Source Sans 3 fallback. It is not bundled. The Chinese name keeps its independent 行楷 font.

From the repository root:

```bash
python3 scripts/design_xml.py export my-design.xml
python3 scripts/design_xml.py import my-design.xml
```

CLI import validates the design, backs up changed source, and rebuilds/checks all demos before saving. Commit and push with your usual Git workflow afterward.
