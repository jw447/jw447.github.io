# Jinzhen Wang / HPDi Lab website

## Install this complete source package

Merge the contents of this folder into your existing Git checkout. Preserve its
`.git/` directory. On macOS, use `rsync -av /path/to/extracted/jwang-hpc.github.io/ ./`
from your repository root; do not use `--delete`.

For the first installation, review and commit the changed source before starting
the editor, because startup refuses to pull over uncommitted changes:

```bash
git switch local-design
git status --short
git add edit.py scripts editor assets tests README.md AGENTS.md
git commit -m "Simplify content editor and sync GitHub review branch"
git push -u origin local-design
python3 edit.py
```

Use your existing GitHub authentication. No credentials are stored in website
source. The origin URL should be
`https://github.com/jwang-hpc/jwang-hpc.github.io.git`.

## Daily content editing

Run `python3 edit.py` (Python 3.9+). It checks for a clean Git checkout, fetches
GitHub, switches to `local-design`, pulls review updates with a fast-forward,
and merges the newest `origin/main`. A divergence between local and remote review
history stops startup; a conflict with main aborts that merge and stops startup.
No forced pushes, automatic stashes, discarded files, or main-branch pushes.
An ordinary merge commit may be created to combine main and unmerged review work.
Git name/email and authentication must already be configured.

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
publish those changes before restarting, or commit them manually. An interrupted
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
`content/legacy.json` preserves only listed older resources; do not list deleted
files there. This package retains your uploaded content and website templates.
GitHub and the separate ChatGPT demo do not automatically synchronize.
