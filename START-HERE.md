# Website export — October 10, 2026

Current Sites source commit: aa0188e16eb5244dccbb90d31153d731daa6f461 (site version 47).

## What is included

- `source/`: complete editable source, including content/design editors, all four layouts, tests, and GitHub Actions workflow. Git history, caches, generated output, and Sites-specific hosting identity are omitted.
- `minimal-site/`: ready-to-serve static current Classic design, with personal page, lab, project detail pages, supporting standalone routes, theme switching, biography popups, CV preview and required assets. No build step or editor required. Alternate layouts and typography review UI are omitted. The bundled font stylesheet still defines all supported typefaces, so their referenced font files and licenses remain.
- `EXCLUDED-FILES.txt`: exact generated files omitted from the minimal package.

The CV dialog still embeds the existing Google Drive preview; the PDF is not bundled. Optima uses an installed font with bundled fallback. Existing course files and PDFs from your GitHub repository are not in this export.

## Local edits (recommended: source)

Install Python 3; Node is needed only for the optional JavaScript tests. No pip/npm installation is required.

```bash
cd source
python3 build.py
python3 scripts/check_site.py
python3 -m http.server 8000 --directory dist
```

Open http://localhost:8000. Stop the server with Ctrl+C. Edit source files, rebuild, then refresh. Do not edit `dist/` directly.

| Edit | Source file |
| --- | --- |
| Biography, contact/CV link, update date | content/profile.json |
| News | content/news.json |
| Papers and paper links | content/publications.json |
| Lab projects and detailed introductions | content/projects.json |
| Students, alumni, biographies | content/people.json |
| Lab research, sponsors, navigation | content/lab.json |
| Courses | content/teaching.json |
| Colors, typography, spacing | content/design.json |
| Navigation and optional pages | content/site.json |
| Main page HTML structure | build.py |
| People / project rendering | person_cards.py / project_portfolio.py |
| Styles / interactions | assets/*.css / assets/*.js |
| Header logos and portraits | assets/logos/ / assets/people/ |

An optional form editor is available via `python3 scripts/editor_server.py`; follow its printed local address. Read `source/README.md` for editor import/export and design XML controls. Its existing Publish button is intended for synchronized main; use the manual review-branch workflow below while reviewing.

For direct static editing instead, run `python3 -m http.server 8000 --directory minimal-site` from this export folder and edit its HTML/CSS directly. Those changes do not propagate back into `source/`.

## Push to GitHub and replace jw447.github.io

This export does not push or replace your live GitHub site.

1. Clone your existing repository (or use your existing local checkout). Preserve its history and old resources.

```bash
git clone https://github.com/jw447/jw447.github.io.git
cd jw447.github.io
git switch -c website-export-review
```

2. Copy the **contents** of `source/` into this checkout, including `.github/` and `.gitignore`. Copy with Finder showing hidden files (Command+Shift+period), or:

```bash
rsync -av /absolute/path/to/website-export/source/ ./
```

Do not use `--delete`: existing course pages, PDFs and other legacy resources must be reviewed and preserved. Check `git diff` for collisions, especially README, scripts, assets and existing Actions workflows. Disable an older deployment workflow if it competes with the supplied Pages workflow.

3. Legacy files must also enter the deployed `dist/`, not merely remain in the repository. Add explicit copies for each needed legacy directory/file to the workflow after the build and before `upload-pages-artifact`. For example, if your repository contains `courses/` and `papers/`, add a run step:

```yaml
      - run: |
          cp -R courses dist/courses
          cp -R papers dist/papers
```

Use your actual paths; these names are examples, not verified inventory. Preserve nested paths so existing URLs work, and add redirect pages where URLs change. If a custom domain is configured, retain its Pages settings and ensure any required CNAME is copied into dist. An existing root index.html will be superseded by the generated dist/index.html; retain a backup if needed.

4. Build, check, inspect locally, then push:

```bash
python3 build.py
python3 scripts/check_site.py
git status --short
git add content assets editor scripts tests build.py simple_layout.py person_cards.py project_portfolio.py publication_format.py .github .gitignore README.md AGENTS.md CLAUDE.md
git diff --cached --stat
git commit -m "Update academic website design"
git push -u origin website-export-review
```

Stage any deliberate legacy-copy/workflow adjustments too. If this branch name already exists, use a new name or update the existing review branch intentionally. Normal local GitHub authentication applies.

5. Create a pull request to your publishing branch. The included workflow deploys on `main`; if your repository uses another publishing branch, change its `on.push.branches` first.
6. In the repository's **Settings → Pages → Build and deployment → Source**, choose **GitHub Actions**. Merge the reviewed PR to `main`, then check the Actions run. It builds source and publishes `dist/` to https://jw447.github.io/.
7. Test the homepage, lab, project, CV popup, dark mode, and retained old course/PDF URLs after deployment.

Future edits: `git pull`, edit content/assets, run the build/checks, commit, and `git push`. A push to main triggers the supplied deployment workflow. Keep review branches for changes you want to inspect before publishing.

## Files outside the current design

`editorial/`, `simple/`, `compact/` are alternate generated layouts; `fonts.html` is a review page; `admin/` is the optional editor. Their dedicated styles/illustrations and editor scripts are excluded from minimal-site when unreferenced. `content/compact.json`, `simple_layout.py`, editor modules and tests remain in full source because its multi-layout builder uses them. `.openai/` is unnecessary for GitHub Pages. Caches and Git internals are not website source. See the exact exclusions list.

Do not delete old GitHub files just because they are absent here: this export does not inventory the existing GitHub checkout. Old course pages and downloadable papers may still have incoming links.

Official GitHub instructions: https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site
