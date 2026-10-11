# Jinzhen Wang / HPDi Lab website

## Checkout and authentication

Use the local-design branch of jwang-hpc/jwang-hpc.github.io. Use your existing
GitHub authentication; credentials are never stored in website source.

```bash
git fetch origin
git switch local-design
git pull --ff-only origin local-design
python3 edit.py
```

Pull manually with a clean checkout. Saved edits on local-design can be reopened
without committing or publishing.

## Daily content editing

Run `python3 edit.py` (Python 3.9+). It fetches GitHub and opens `local-design`.
Clean checkouts pull that branch with a fast-forward. Saved local edits are
preserved and skip automatic pulling; you can close and reopen without publishing.
If the network is unavailable or branch histories diverge, the editor opens
local files and prints a notice. Resolve divergent histories before publishing.
Dirty checkouts on another branch and unfinished merges require manual resolution.
Startup never merges `main`; you manage upstream merges and deployment yourself.
No forced pushes, automatic stashes, discarded files, or main-branch pushes.
Git name/email and authentication must already be configured for publishing.

After synchronization, the current website is rebuilt and checked and the editor
opens at http://127.0.0.1:8765/admin/. If the port is occupied, use
`python3 edit.py --port 8766`. Ctrl+C stops the server.

1. Edit profile, news, papers, teaching, projects, people, lab or sponsors.
2. Preview the draft through the actual website build; choose Personal or Lab.
3. Save files to write checked content locally, or Publish to save, commit, and
   push to `local-design`. Commit messages summarize affected sections,
   added/removed records, and updated fields.
4. Review the branch/PR, then merge into main to update the public site.

Publish is a review-branch push, not a live deployment. The included workflow
publishes `dist/` after changes reach main. Save files alone does not commit;
saved changes remain available when reopening the editor. An interrupted
push can be retried with Publish without creating a duplicate commit. Code edits
outside content must be committed separately before Publish.

Browser drafts are retained and protected against stale source revisions. Download
an unsaved draft before loading current content. Imports preserve the current
design; design values in an old content draft are not applied by this editor.
Exact draft preview needs the local service. The hosted editor supports forms
and JSON import/export, without browser-side design controls or a duplicate page
renderer. Embedded previews disable scripts; test interactive features on the
saved website at http://127.0.0.1:8765/.

## Design changes

There are no design sliders, palettes, or layout presets in the content editor.
Use a design XML file or ask your assistant to change the source templates/styles.
XML must use the supported HPDi version-1 design schema, not arbitrary XML from
another application. Export a reference schema for a third-party tool:

```bash
python3 scripts/design_xml.py export HPDi-design.xml
python3 scripts/design_xml.py import /path/to/updated-design.xml
```

The importer validates the file, backs up changed design settings and rebuilds.
Commit and push these design changes manually. Content editing preserves them.

## Direct edits and deployment

`content/*.json` is authoritative content; `content/design.json` holds design
settings. `build.py` and renderer modules generate pages, `assets/` contains
styles, scripts, fonts and images. Never edit generated `dist/` files.

```bash
python3 build.py
python3 scripts/check_site.py
```

The Pages workflow belongs in `.github/workflows/pages.yml`. Settings → Pages →
Source must be GitHub Actions. Keep `dist/`, caches and `.editor-state/` ignored.
The build removes previous dist output before generating the current pages, so
retired demo pages and assets cannot remain in deployment.

## CV, update date and citations

In Profile, choose a PDF under Curriculum vitae (maximum 10 MB). Upload writes
`assets/cv/jinzhen-wang.pdf` locally; Save or Publish applies the link. Publish
includes the PDF. The public CV button opens the PDF in an on-page viewer.
The existing CV link remains until you upload a replacement.

Publish sets the Last update label to the push day in America/New_York. Manual
pushes to local-design are also stamped by stamp-updated.yml (a bot commit may
appear; pull it before your next push). Merging main later preserves that date.

Papers support a DOI and optional publisher BibTeX. Fetch publisher BibTeX uses
publisher-deposited Crossref metadata; review it before saving. Google Scholar,
IEEE and ACM BibTeX exports can also be pasted into the same field. The build
uses that BibTeX, then verified DOI metadata, then a minimal local fallback.
Only the current design is built; compact.json and retired demo assets are removed.
