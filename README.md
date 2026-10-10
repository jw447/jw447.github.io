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

The public GitHub source includes the three student/alumni profiles confirmed from the owner’s public team page; additional profiles remain deferred. The private ChatGPT-hosted demo and this GitHub repository are separate deployments: edits pushed here do not automatically update the ChatGPT demo.

---

# jw447.github.io
personal website

## Design XML and Optima trial

The Design tab now offers **Export design XML** and **Import design XML**. Export downloads the current draft; import changes only design settings, preserving news, papers, and other content. Preview the imported design, then choose **Save files** in the local editor. `content/design.json` remains the active source, and each build exports the published design to `/assets/design.xml`.

Current snapshots are `assets/design-examples/design-palatino.xml` (previous design) and `assets/design-examples/design-optima.xml` (current trial). Optima is preferred for body text and headings, with Candara and locally hosted Source Sans 3 as fallbacks when unavailable. Navigation keeps Source Sans 3; 王金震 uses 行楷. Optima is not bundled.

```bash
python3 scripts/design_xml.py export my-design.xml
python3 scripts/design_xml.py import my-design.xml
```

CLI import validates, backs up changed source, and rebuilds/checks before saving. Commit and push afterward. See `assets/design-examples/README.md` for the XML format. All groups/attributes are required; numeric values have no units, colors use six-digit hex values, and the editor's existing size and contrast limits apply.

### Chinese name typography

王金震 uses 行楷, preferring installed STXingkai/华文行楷. `assets/fonts/hpdi-name-xingkai.woff` provides a locally hosted running-script fallback: Zhi Mang Xing, subsetted to these three characters with its original metadata and OFL license retained. It loads only 2.6 KB and needs no external font service. If the Chinese name changes, regenerate this subset. English text uses the active Design font settings.

### Header controls

Header logos align to the left; navigation and theme controls align to the right. The moon switches to dark mode; the sun switches to light mode. The icon button retains an accessible action label and tooltip, with the same theme persistence and device-preference behavior.

### Sponsor presentation

Every lab demo renders only the three linked logos on transparent backgrounds, with original colors and proportions. Descriptions, sponsor labels, and project/program lists are not displayed. Program metadata remains in the source for future maintenance.

### Footer and Chinese name previews

The footer date comes from `content/profile.json` → `updated` and is displayed as `Last update: (date)`. The extra email link in the personal homepage recruiting sentence is removed. Open `/fonts.html#chinese-fonts` to compare 楷体, 行楷, and 草书, then follow a homepage preview link. These query-based previews do not save settings; 行楷 remains the default. All three name fonts are local, three-character subsets, with preserved licenses.

### Confirmed team profiles

On October 10, 2026, the owner requested profiles from https://sites.google.com/charlotte.edu/hpdilab/team. The lab roster lists Ph.D. students Khondoker Mirazul Mumenin and Jiaxiang Zhang, plus Raivat Alwar under Alumni, following that page's grouping and stated M.S. role. Background and research summaries are compact; no joining or graduation dates are inferred. Bios and research topics can be edited in the People form. Each record stores its source URL. Team photos were unavailable, so these profiles use text. The lab header shows `HPDi Lab` and the mission only.

The UNC Charlotte sponsor uses the supplied horizontal logo. All sponsor artwork keeps its proportions at a shared display height, with a smaller equal height on mobile.

The header displays only the official CCI logo, left aligned; navigation and theme controls remain right aligned. The horizontal UNC Charlotte logo remains in Sponsors.

The current lab directory uses matching responsive columns without profile dividers. Aagat Pokhrel is included under Students; Adelina Zheng is an Alumni summer REU student from Brown University. No additional degree or date is inferred. The Join section is removed. Lab overview text remains editable in `content/lab.json` under `mission`. Homepage and lab browser titles use the owner-requested names; the CCI header logo has no extra inset padding.

Sponsor alignment uses three equal-width columns, each with a centered 240×96px image box. Preserve this even distribution and equal image dimensions; do not restore a flex group aligned to one side. On phones, use evenly centered rows with the same image-box size.
