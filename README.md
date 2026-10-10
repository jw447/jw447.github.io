# Start editing locally

Requirements: Git and Python 3.9 or newer. The website and local editor use the Python standard library. No Node, npm, Jekyll, or database is required for routine editing.

```bash
git clone --branch website-redesign https://github.com/jw447/jw447.github.io.git
cd jw447.github.io
python3 build.py
python3 scripts/check_site.py
python3 scripts/editor_server.py
```

Open http://127.0.0.1:8765/admin/?tab=design for design controls, or http://127.0.0.1:8765/admin/ for content forms. The local server also serves all generated pages, including `/`, `/compact/`, `/simple/`, `/editorial/`, and each lab page. Stop it with Ctrl+C.

Your workflow is **edit source or use the forms → build and check → preview locally → commit and push**. `Save files` writes form changes into `content/` and rebuilds every demo. For direct code edits, rerun the build and check commands, then refresh the page. Source at `content/*.json` holds text and design settings; `assets/*.css` controls detailed styles; `build.py` and `simple_layout.py` control page structure. `dist/` is generated and ignored by Git.

Commit edits to this review branch with:

```bash
git add content assets editor scripts tests build.py simple_layout.py publication_format.py README.md AGENTS.md CLAUDE.md .github .gitignore
git commit -m "Tune academic website"
git push origin website-redesign
```

Run `git pull --ff-only` before starting a new editing session so local work and assistant updates stay synchronized. These pushes update the review branch. Once ready to launch, set **Settings → Pages → Source → GitHub Actions** and merge the redesign into `main`. Thereafter a push to `main` builds and deploys `dist/` automatically. The local editor's Publish button requires synchronized `main`; code/layout edits are committed with Git directly.

The root `index.html` is the old Google Sites redirect. It is retained as legacy source; the new homepage is generated at `dist/index.html`. Existing underscore HTML routes, old CSS, PDFs in `files/`, and images in `imgs/` are copied into the Pages output at their original paths. `content/legacy.json` lists these passthrough resources. Their bytes are checked, but the old HTML's pre-existing broken links/metadata are not silently rewritten.

The public GitHub source starts with an empty student roster, as student information is deferred. The private ChatGPT-hosted demo and this GitHub repository are separate deployments: edits pushed here do not automatically update the ChatGPT demo.

---

# jw447.github.io
personal website

## Design XML and Optima trial

The Design tab now offers **Export design XML** and **Import design XML**. Export downloads the current draft; import changes only design settings, preserving news, papers, and other content. Preview the imported design, then choose **Save files** in the local editor. `content/design.json` remains the active source, and each build exports the published design to `/assets/design.xml`.

Current snapshots are `assets/design-examples/design-palatino.xml` (previous design) and `assets/design-examples/design-optima.xml` (current trial). Optima is preferred for body text and headings, with Candara and locally hosted Source Sans 3 as fallbacks when unavailable. Navigation keeps Source Sans 3; 王金震 keeps Kai. Optima is not bundled.

```bash
python3 scripts/design_xml.py export my-design.xml
python3 scripts/design_xml.py import my-design.xml
```

CLI import validates, backs up changed source, and rebuilds/checks before saving. Commit and push afterward. See `assets/design-examples/README.md` for the XML format. All groups/attributes are required; numeric values have no units, colors use six-digit hex values, and the editor's existing size and contrast limits apply.
