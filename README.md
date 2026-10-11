# Academic website demos

Four designs share the same content, generator, and brand assets.

Updated design direction: Classic A uses one scrolling homepage for biography, news, all papers, and teaching. `lab.html` is the dedicated HPDi Lab page for its overview, research, projects, people, recruitment, and sponsors. News stays on the personal page. Six typography previews are available at `fonts.html`, with a full-site font chooser at `index.html?preview=fonts`.

- **Classic academic:** `dist/index.html`. One main reading column with the portrait, name, links, and contact details grouped at the top. Google Scholar and CV use compact Charlotte-green buttons; the email address and room use small inline chips without repeated labels. Repeated department/university labels and the uppercase research tagline have been removed from the profile introduction.
- **Modern editorial:** `dist/editorial/index.html`. Wider editorial layout with the profile on the right.
- **Simple Claude-inspired:** `dist/simple/index.html`. Compact header, one reading column, portrait beside the introductory text, Pagella throughout, dated news, and year-grouped papers. Adapted from the owner-supplied `hpdil-website.zip`. It keeps news, all papers, and teaching on one homepage with a separate `simple/lab.html`. Standalone Publications, Teaching, and About pages are also available. The supplied provisional mark and refinement illustration are retained as review assets, not final lab branding.

All designs use static HTML and CSS. JavaScript adds citation copying, font previews, and a mobile menu. Content remains readable without JavaScript. No npm packages, remote fonts, trackers, database, or paid services are required.

- **Compact PiComp-inspired:** `dist/compact/index.html` and `dist/compact/lab.html`. A wide reading column, portrait on the right, 16px body text with 1.5 line height, closer paragraph spacing, small green section bars, compact news rows, and abbreviated biography/project summaries. Personal-page sections stay together; the separate lab page has research, projects, people and sponsors. Dark mode and student-author highlighting are shared with the other demos.

## Maintenance

Edit the relevant file in `content/`, then run `python3 build.py`. On GitHub, commit the content edit and the included workflow builds the site automatically.

Codex and Claude share maintenance instructions in `AGENTS.md`. `CLAUDE.md` points to those same instructions. Ask either assistant to add supplied news or publication metadata, then run `python3 build.py` and `python3 scripts/check_site.py`. Layout assets live in `assets/`; generated copies in `dist/` should not be edited directly. The simple and compact layouts are rendered by `simple_layout.py` and styled by `assets/simple.css`. It uses the same JSON records and brand configuration as the other demos, so routine content edits update every version. No Ruby, Jekyll, YAML conversion, or added build dependency is needed.

| File | Content |
| --- | --- |
| `profile.json` | English/Chinese names, biography, contact details; retained education/service records are not rendered |
| `news.json` | Dated news items, newest first automatically |
| `publications.json` | Papers, authors, year, venue, links, selected flag |
| `projects.json` | Project summaries and resources |
| `people.json` | Confirmed student/alumni profiles, approval flags, bios, and source URLs |
| `lab.json` | Lab overview, research descriptions, recruitment, sponsors, and navigation |
| `teaching.json` | Courses and terms |
| `site.json` | Default font, student-author names, navigation, and optional extra pages |
| `compact.json` | Shorter biography and project descriptions for the compact demo |
| `brand.json` | Original Charlotte palette and source provenance |
| `design.json` | Active shared typography, spacing, layout, and light/dark palettes |

### Navigation and extra pages

Edit `content/site.json`. A section item looks like `{"label":"Papers","kind":"section","target":"papers"}` and scrolls to the homepage section. A page item looks like `{"label":"Demos","kind":"page","target":"demos.html"}`. Add a matching entry in `extra_pages` to generate the page, or provide a custom page generator. Starter Demos and Seminars pages exist but are omitted from navigation until you want to show them. Extra-page items use `title`, `description`, and optional `url` fields.

### Colors

The owner selected UNC Charlotte colors. The [official university palette](https://brand.charlotte.edu/visual-identity/color-palette/), verified October 9, 2026, specifies Charlotte Green `#005035`, Niner Gold `#A49665`, and Quartz White `#FFFFFF`. Green is used for links, navigation, and the top rule. Gold is limited to small section markers and the active-navigation underline. Body text stays charcoal on white.

The original verified brand palette remains in `content/brand.json`. Active colors are now maintained in `content/design.json` through the Design tab. It also contains interface neutrals and a pale green tint; those are chosen site colors, not additional official brand colors. The generator creates `dist/assets/colors.css`, the browser theme color, and the temporary favicon from the active design settings. Both layouts use the same palette. Reuse these tokens when designing the logo and slides.

### Dark mode

Every demo has a Dark mode / Light mode button in the header. It follows the device color preference until you choose a mode, then remembers your choice in this browser across the personal and lab pages. The control is hidden when JavaScript is unavailable; CSS still follows the device preference. Active dark-mode colors are in `content/design.json` under `dark`. The selected dark palette uses neutral charcoal (`#1B1B1B`), warm off-white text (`#E8E4DC`), muted green (`#8FB9A0`), restrained gold (`#C3B387`), and neutral gray secondary surfaces (`#262626`). Text and links retain contrast on both surfaces. `assets/theme.js` applies the preference before styles load and `assets/theme.css` styles the button. Print output stays light.

### Typography

The Design tab now controls the active body, heading, and navigation typefaces independently. The older review-only `font` setting accepts `optima`, `source-sans`, `inter`, `plex`, `serif`, or `palatino`. The current trial is `optima`: installed Optima for body text and headings, followed by Candara and locally hosted Source Sans 3. The prior `palatino` option uses locally hosted **TeX Gyre Pagella**, with Palatino as fallback. Compare live previews with `?font=inter&preview=fonts`, for example. The font comparison controls appear only in review mode. `serif` pairs Source Serif 4 headings with Source Sans 3 body text. `palatino` includes regular, bold, italic, and bold italic faces so publication venues and emphasis use actual font styles. Navigation and small interface labels use Source Sans 3. Bundled fonts are self-hosted with licenses in `assets/fonts/`. Pagella was obtained from [CTAN](https://ctan.org/pkg/tex-gyre-pagella) and losslessly packaged as WOFF from the original OpenType fonts. The GUST Font License and original README are included. Font conversion is a one-time asset preparation step; routine builds still require only the Python standard library.

The owner authorized importing the current student/alumni information from the existing public team page. Additional profiles remain deferred. The student section now lives on `lab.html#people`. Entries in `people.json` require `approved: true` before they are rendered. Groups supported by the generator are `Students`, `Alumni`, and `Collaborators`. Each profile contains `name`, `role`, `group`, optional `topic`, `joined`, `url`, and the explicit `approved` flag. The PI profile comes from `profile.json`. Do not infer missing student information. The old People route links to the lab directory.

### Add news

Add an object to `content/news.json`:

```json
{"date":"2026-10","kind":"Paper","text":"A new paper announcement.","url":"https://example.org/paper"}
```

Dates use YYYY-MM. All news items appear in a bounded, vertically scrollable panel on the homepage. Readers can scroll with a mouse, touch, or keyboard; there is no expandable older-news section. The existing News route also preserves the full archive.

### Publication author highlighting

Publication lists use bold for Jinzhen Wang and a thin underline for HPDi Lab student authors. The legend explains this above the papers on the homepage and standalone Publications page. Maintain the `student_authors` list in `content/site.json`, using the exact spelling from `publications.json`; highlighting matches whole author names. Khondoker Mirazul Mumenin is included because the owner's supplied design reference underlines that name in the DeepCQ and QualityNet entries. Add other names only when confirmed by the owner. This author annotation is independent of the deferred student profiles in `people.json`. Publication and BibTeX metadata are unchanged.

Publication labels follow `[venue'YY]`, for example `[Cluster'26]`, `[BigData'24]`, and `[TPDS'19]`. The shared `publication_format.py` uses the venue abbreviation in `short`, omits an `IEEE ` prefix, and appends the last two year digits. Stable record IDs and BibTeX keys remain unchanged.

### Add a paper

Add an object to `content/publications.json` with `id`, `year`, `title`, `authors`, `venue`, `short`, `selected`, and `links`. All papers now appear on the homepage. The `selected` field is preserved for future highlighting. Authors are separated by comma and space. Generated BibTeX includes the supplied metadata only. Add DOI, pagination, and publisher metadata if needed before using it in manuscripts.

### GitHub Pages

This package is prepared for `jw447/jw447.github.io`. Review the demos before replacing the existing site. The existing repository was inspected but has not been modified.

1. Copy these files into the repository on a review branch, preserving old files such as course pages and PDFs that you still need.
2. In the repository's **Settings → Pages**, choose **GitHub Actions** as the source.
3. Merge the review branch to `main`. The included workflow builds and deploys `dist/`.
4. For the editorial design as the primary site, change the generator's primary design mapping and rebuild, or copy the editorial page structure into the primary route. Do not merely move generated HTML without correcting asset paths.

All page links are relative. A custom domain can be configured separately. `.openai/` is preview-host metadata and is not needed for GitHub Pages.

## Content provenance and remaining review

Migrated from the user's public Google Sites About PI, News, Publications and Projects pages, retrieved October 9, 2026. NeurLZ metadata was updated from arXiv:2409.05785. DeepCQ uses the Cluster 2026 title from the lab's current project page, while its linked arXiv preprint has an earlier title. The portrait comes from `jw447/jw447.github.io/imgs/profile.jpg`.

The current site spells the lab's full name **High-Performance Data Intensive Lab**. That existing public name is retained. Confirm the preferred full name before finalizing a logo or slide master. Teaching terms are migrated from the public page, not inferred to be current. The existing CV link is preserved and may require appropriate Google Drive sharing settings. GWLZ and the layer-freezing preprint were not added to the bibliography because their complete current metadata was not confirmed.

## Design suite direction

Once a website direction is selected, use its accent color and typography hierarchy across the slide template and future logo. Keep the slide canvas white, use one accent for headings and key findings, and reserve multiple colors for data series. The text label HPDi Lab is a temporary identifier, not a new logo. Logos and slide masters are deferred while the website demos are reviewed.

The October 9 reference `https://wdong5.github.io/` informed the separate personal/lab structure, compact news rows, restrained section markers, and an additional Palatino-style font preview. The reference's orange palette and biography were not reused.

The Simple demo recreates the visual approach of the owner-supplied Claude example. Its reference CSS and two SVG assets were adapted; its unconfirmed roster details and placeholder links were not imported. It uses the existing confirmed content and student-author annotations. The illustration represents progressively tighter approximations and is not a measured research result. Active Design settings apply to the comparison layout; the font review controls remain in the other demos.

### Lab sponsors

Maintain the `sponsors` list in `content/lab.json`. NSF, DOE, and UNC Charlotte have official logos stored in `assets/logos/`; that folder's README records their original sources. Each sponsor has `name`, `label`, `logo`, `url`, and a `programs` list of `title`, `year`, and `url` fields. Every lab demo renders only the three linked logos on transparent backgrounds, with original colors and proportions. Descriptions, sponsor labels, and project/program lists are not displayed. Program metadata remains in the source for future maintenance. UNC Charlotte was added at the owner's request and has no inferred award metadata.

### Compact demo maintenance

The compact demo reuses the shared renderer and records. Its shorter biography and project summaries live in `content/compact.json`; project summaries are keyed by stable project ID. Update these summaries alongside factual changes to the main biography or projects. The build leaves the Classic, Editorial, and Simple copy unchanged. `assets/compact.css` overrides the shared Simple styles only for `/compact/`. No new framework or build dependency is added.

The owner reference [PiComp Lab](https://picomp-lab.github.io/) informed its wide reading column, right-hand portrait, close paragraph spacing, compact dated rows, and section bars. The reference HTML/CSS was inspected on October 9, 2026; its lab content and branding were not imported.

### Chinese name typography

王金震 uses 行楷, preferring installed STXingkai/华文行楷. `assets/fonts/hpdi-name-xingkai.woff` provides a locally hosted running-script fallback: Zhi Mang Xing, subsetted to these three characters with its original metadata and OFL license retained. It loads only 2.6 KB and needs no external font service. If the Chinese name changes, regenerate this subset. English text uses the active Design font settings.

The owner removed Education and Professional Service sections from the demos and their standalone About/Teaching pages. Service is also removed from navigation. Existing education/service source records remain available but are not displayed as sections.

### Readability

News uses 16px text, and no site text is smaller than that minimum. Main body copy stays at 16px or larger across the four demos. Preserve this minimum for navigation, publication labels, author lists, contact chips, captions, and mobile layouts. The Chinese name scales with its large heading and remains above the minimum.

## Browser content editor

Open `/admin/` to edit profile, news, papers, teaching, projects, people, lab information, and sponsors through forms. Drafts save in this browser. Content preview shows the compact personal or lab layout. The Design tab previews the current site content in any of the four layouts. Import and **Download updates** transfer a complete JSON content package. Existing paper and project IDs are preserved; new entries receive IDs automatically. People remain hidden until their display checkbox is enabled.

The hosted demo supports drafts, preview, import, and export. **Direct publishing from the hosted editor is not connected.** To write files and publish, use the optional local editor from this codebase:

```bash
python3 scripts/editor_server.py
```

Open `http://127.0.0.1:8765/admin/` and import your downloaded draft. **Save files** validates the content, builds all demos, checks links, backs up changed JSON files under `.editor-state/backups/`, and writes the files locally. The local preview uses the actual generator. Source changes made after a draft was loaded are protected by a content revision hash; export an old draft before loading current content and ask Codex or Claude to merge it if necessary.

**Publish** is available when the codebase is installed in a GitHub repository with `origin` pointing to GitHub, on `main`, with Git authentication and name/email already configured. It requires the local branch to match `origin/main`, excludes unrelated layout/code edits, creates a content commit, and pushes it. The Pages workflow then deploys. A failed push retains the commit for retry. This implementation was tested against an isolated local Git remote; the actual `jw447/jw447.github.io` repository has not been changed or tested for publishing.

You can also apply an exported draft without opening the editor:

```bash
python3 scripts/apply_content.py /path/to/HPDi-content-updates.json
```

The server uses the Python standard library, binds only to `127.0.0.1`, and checks request origin and a per-session token before writes. It is not deployed as a public server. The public academic pages remain static, and builds require no new dependencies. Source: `editor/`, `assets/editor*`, and `scripts/editor_server.py`.

Run editor regression checks with `python3 -m unittest discover -s tests -p 'test_*.py' -v` and `node --test tests/editor-model.test.cjs` after building. Node is needed only for these developer tests, not site generation or the local editor.

## Tune the design yourself

Open `/admin/?tab=design`. The Design tab includes typeface selectors, size sliders with numeric inputs, line height, paragraph/section/publication spacing, page width, portrait size and desktop position, news-panel height, and separate light/dark color pickers with editable hex values. Settings live in `content/design.json`; generated tokens and `assets/design.css` apply them to every personal and lab demo. Original logo artwork is unaffected.

Choose Classic, Compact, Simple, or Editorial, and the personal or lab page. Desktop preview uses a 1100px viewport, mobile uses 390px, and the iframe scales to fit the editor. **Enlarge preview** gives more room. The design preview uses current site content; content drafts have their own Preview flow. Styles update immediately after valid changes without resetting the preview scroll position. Theme selection here changes the preview only.

Three starter presets are included: Charlotte defaults, Compact reading, and Comfortable reading. Name your design and click **Save preset** to keep it in this browser; select it and click **Apply preset** to reuse it. **Charlotte defaults** resets only the design draft. **Download updates** includes the current design with your content, so it can be imported elsewhere or applied through the local editor. Named preset collections themselves stay browser-local.

Text stays at least 16px. Increasing the minimum raises news, author lists, navigation, labels, and other small text together. Text/link contrast is checked against both background surfaces in each theme, with a minimum of 4.5:1. Invalid settings remain visible for correction; the live preview keeps the last valid design, and invalid designs cannot be saved or published. Settings accept bounded numbers, bundled fonts, and six-digit colors rather than arbitrary CSS.

Hosted changes remain drafts until exported. The local **Save files** and **Publish** flows also include `design.json`, with the same backup, revision protection, and GitHub setup requirements described above. Older content-only editor drafts are recognized and given current design settings; their original revision is retained to protect newer source changes.

## Design XML and Optima trial

The Design tab now offers **Export design XML** and **Import design XML**. Export downloads the current draft; import changes only design settings, preserving news, papers, and other content. Preview the imported design, then choose **Save files** in the local editor. `content/design.json` remains the active source, and each build exports the published design to `/assets/design.xml`.

Current snapshots are `assets/design-examples/design-palatino.xml` (previous design) and `assets/design-examples/design-optima.xml` (current trial). Optima is preferred for body text and headings, with Candara and locally hosted Source Sans 3 as fallbacks when unavailable. Navigation keeps Source Sans 3; 王金震 uses 行楷. Optima is not bundled.

```bash
python3 scripts/design_xml.py export my-design.xml
python3 scripts/design_xml.py import my-design.xml
```

CLI import validates, backs up changed source, and rebuilds/checks before saving. Commit and push afterward. See `assets/design-examples/README.md` for the XML format. All groups/attributes are required; numeric values have no units, colors use six-digit hex values, and the editor's existing size and contrast limits apply.

### Header controls

Header logos align to the left; navigation and theme controls align to the right. The moon switches to dark mode; the sun switches to light mode. The icon button retains an accessible action label and tooltip, with the same theme persistence and device-preference behavior.

### Footer and Chinese name previews

The footer date comes from `content/profile.json` → `updated` and is displayed as `Last update: (date)`. The extra email link in the personal homepage recruiting sentence is removed. Open `/fonts.html#chinese-fonts` to compare 楷体, 行楷, and 草书, then follow a homepage preview link. These query-based previews do not save settings; 行楷 remains the default. All three name fonts are local, three-character subsets, with preserved licenses.

### Confirmed team profiles

On October 10, 2026, the owner requested profiles from https://sites.google.com/charlotte.edu/hpdilab/team. The lab roster lists Ph.D. students Khondoker Mirazul Mumenin and Jiaxiang Zhang, plus Raivat Alwar under Alumni, following that page's grouping and stated M.S. role. Background and research summaries are compact; no joining or graduation dates are inferred. Bios and research topics can be edited in the People form. Each record stores its source URL. Original portraits are now available for Mumenin, Jiaxiang, and Raivat; Aagat and Adelina have labeled placeholders. The lab header shows `HPDi Lab` and the mission only.

The UNC Charlotte sponsor uses the supplied horizontal logo. All sponsor artwork keeps its proportions at a shared display height, with a smaller equal height on mobile.

The header displays only the official CCI logo, left aligned; navigation and theme controls remain right aligned. The horizontal UNC Charlotte logo remains in Sponsors.

The current lab directory uses matching responsive columns without profile dividers. Aagat Pokhrel is included under Students; Adelina Zheng is an Alumni summer REU student from Brown University. No additional degree or date is inferred. The Join section is removed. Lab overview text remains editable in `content/lab.json` under `mission`. Homepage and lab browser titles use the owner-requested names; the CCI header logo has no extra inset padding.

Sponsor alignment uses three equal-width columns, each with a centered 240×96px image box. Preserve this even distribution and equal image dimensions; do not restore a flex group aligned to one side. On phones, use evenly centered rows with the same image-box size.

## Portrait directory and course update

The owner requested portrait/name modules, visible research keywords, and detailed information on portrait hover or keyboard focus, with a Details disclosure for touch and keyboard users. Faculty and Students share one grid without category headings; Alumni remains separate. Original local photos are used when available; unavailable portraits show honest initials and Photo forthcoming, never generated substitute faces. Portrait selections, keywords, biography, sponsor thank-you text, and course links are editable through the content forms. Broad default keywords High-performance Computing and Data Compression follow the owner's requested lab themes and can be refined per member. Aagat is a Ph.D. student, Computer Science, as confirmed by the owner. Parallel Computing spans Fall 2024–Fall 2026; AI System Design is ITCS 6010/8010, Fall 2026, verified from the supplied course page. Sponsor logos retain equal columns and identical image boxes beneath the shared thank-you sentence.

Original portraits for Mumenin, Jiaxiang, and Raivat are in `assets/people/`, with source provenance in its README. Add owner-supplied `aagat.jpg` and `adelina.jpg` to replace the remaining placeholders automatically. Portraits retain original bytes; no synthetic identities or photo edits are used.
