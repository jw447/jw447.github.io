# Maintenance instructions for Codex and other coding assistants

## Project purpose

An academic personal website for Jinzhen Wang, UNC Charlotte, and HPDi Lab. Preserve the restrained academic style, readable publication lists, accessibility, and simple maintenance. Four demos share the same data: classic at `/`, editorial at `/editorial/`, and the owner-requested simpler Claude-inspired layout at `/simple/`, and the PiComp-inspired compact layout at `/compact/`. The primary Classic route is preserved until the owner selects a replacement.

The owner favors Classic A and requested moving the profile sidebar into the main column. Keep the primary layout as one reading column: a portrait beside the name, role, compact resource buttons, and email/office chips at the top, followed by the biography. The introduction has only Google Scholar and CV resource buttons; the owner removed the Lab GitHub and HPDi Lab buttons. Contact chips show just the email address and room, without Email/Office labels. Use the shared Charlotte green palette and wrap cleanly on mobile. The uppercase research tagline was explicitly removed. The owner's Chinese name is 王金震, stored in `profile.json` as `name_chinese`; show it beside the English name in personal homepage headings with `lang="zh-Hans"`. The owner now specifically chose 行楷 for the Chinese name. Its `HPDi Name Xingkai` font face prefers installed STXingkai/华文行楷 and falls back to `assets/fonts/hpdi-name-xingkai.woff`, a locally hosted three-character subset of Zhi Mang Xing running script. Preserve its OFL license and original font metadata; regenerate the subset if these name characters change. Keep publication author names in their supplied English form. Do not repeat separate department/university labels beneath the role; the biography already gives the affiliation. The primary page contains About, News, all Publications, and Teaching. The owner removed the Education and Professional Service sections across all demos, including standalone About/Teaching pages and navigation. Do not reintroduce these sections during routine updates. Their existing records in `profile.json` are retained but are not rendered as sections. Main navigation scrolls to these sections and links to the dedicated HPDi Lab page at `lab.html`. Students belong on the lab page, not the personal homepage. The lab page contains its overview, research, projects, people and sponsors. News stays on the personal page; do not duplicate it on the lab page or add a lab News navigation item. The redundant PI/GitHub introduction line was removed; the PI profile remains in People. Optional Demos or Seminars may remain separate pages. The owner is trying Optima for body text and headings. The active `font` is `optima`, preferring installed Optima, then Candara and local Source Sans 3. Optima is not bundled. Pagella remains available as the prior serif design. Navigation uses Source Sans 3. Six presets remain available for review; preserve the current trial during routine updates.

## Repository map

- `content/compact.json`: shorter biography and project summaries for the PiComp-inspired comparison. Keep these factually aligned with `profile.json` and `projects.json` when updating either; paper metadata, news, teaching, people, sponsors, and brand tokens are shared directly.
- `content/*.json`: authoritative content. Edit these for routine news, papers, courses, biography, projects, and future people updates.
- `content/site.json`: default font, `student_authors` for underlined publication authors, navigation, and optional extra pages. Use `kind: section` and a section ID for homepage anchors, or `kind: page` and a filename for a separate page.
- `content/lab.json`: lab mission, research descriptions, recruiting copy, sponsors/program links, and its own section navigation. Sponsor support renders on all lab demos; keep NAIRR support described as research/teaching resources, and do not infer monetary awards or amounts.
- `content/people.json`: lab roster. Render entries only when their `approved` field is explicitly `true`, and use the supplied group, role, topic, and links without guessing. The PI comes from `profile.json` and should not be duplicated here.
- `assets/typography.css`: local font faces and six font presets. The font chooser is review UI, visible only with `preview=fonts` in the URL. `fonts.html` compares specimens.
- `assets/fonts/`: bundled open-source fonts and their licenses. They do not depend on Google Fonts or any other runtime service.
- `content/brand.json`: original verified palette and source provenance. Active settings now live in `content/design.json`, including both palettes. The builder generates `dist/assets/colors.css`, browser theme color, and the temporary favicon from it. Charlotte Green, Niner Gold, and white are official; the other tokens are interface neutrals and a derived green tint.
- `assets/style.css`: shared presentation and responsive layouts. Use palette variables instead of repeating color values. Editorial layout overrides are grouped near the end.
- `assets/site.js`: optional enhancements. Core content must work without JavaScript.
- `assets/theme.js` / `assets/theme.css`: shared dark-mode control on all demos. Follow the device preference initially; save explicit choices in browser local storage. Active dark palette tokens live in `content/design.json`; the original verified defaults remain in `content/brand.json`. The owner selected neutral charcoal: background `#1B1B1B`, warm off-white text `#E8E4DC`, muted green `#8FB9A0`, gold `#C3B387`, and neutral gray secondary surfaces `#262626`. Preserve this preference across all demos; the light palette remains the official Charlotte colors. Preserve keyboard access, usable colors on all surfaces, and light print output.
- `assets/jinzhen-wang.jpg`: approved portrait from the existing personal website.
- `build.py`: Python standard-library generator. No third-party Python or Node dependencies.
- `simple_layout.py`: alternate single-column renderer, adapted from the owner-supplied Claude example and using the same JSON content. Its stylesheet is `assets/simple.css`; its supplied provisional SVG assets are `assets/simple-mark.svg` and `assets/simple-refinement.svg`. Preserve the one-page personal sections and separate lab page. Active Design settings override its original Pagella styling.
- `assets/compact.css`: compact comparison overrides, loaded after the shared simple styles. Keep 16px body text, 1.5 line height, a right-hand portrait on desktop, small section bars, and compact list spacing. It uses the same `simple_layout.py` renderer with `variant="compact"`; do not fork the content pipeline.
- `scripts/check_site.py`: content and generated-link checks.
- `.github/workflows/pages.yml`: GitHub Pages build and deployment.
- `dist/`: generated website output. Do not directly edit generated HTML or copied assets. Change the source, then rebuild.
- `.openai/hosting.json`: private demo-host identity. Preserve its project ID. Not required for GitHub Pages.

## Routine workflow

1. Read this file and `README.md`.
2. Change only the relevant source files. For content updates, avoid redesigning the site.
3. Confirm the facts from materials supplied by the owner or authoritative current sources. Link paper PDFs or repositories only when their real URL is known.
4. Run `python3 build.py` and `python3 scripts/check_site.py`.
5. For layout changes, inspect desktop and mobile output if a browser preview is available. Report when visual verification is unavailable.
6. Describe the change and checks briefly. Follow the owner's current instructions for Git commits, PRs, and deployment.

## Content rules

- Do not invent student roles, start dates, alumni placements, award amounts, author lists, DOI values, acceptance status, or unpublished-project claims.
- The owner authorized importing the student profiles from https://sites.google.com/charlotte.edu/hpdilab/team on October 10, 2026. Current students are Khondoker Mirazul Mumenin and Jiaxiang Zhang; Raivat Alwar is listed under Alumni. Additional profiles remain deferred until supplied or confirmed by the owner. Existing roster entries with `approved: false` are withheld. Once the owner supplies or confirms a profile, update its accurate fields and mark it approved to show it on `lab.html#people`. The old `people.html` route points readers to the lab directory.
- Keep news dated as YYYY-MM. Sorting is automatic. All items render inside a bounded, keyboard-focusable vertical scroll panel. Do not reintroduce a five-item limit, folding, or expandable older-news section.
- All papers and teaching entries live on the homepage. Legacy standalone routes are retained for existing links.
- Publication author annotations use bold for the PI and thin underlines for names listed in `content/site.json` as `student_authors`. Khondoker Mirazul Mumenin was supplied as an underlined student author in the owner's reference image. Match whole names exactly, and add additional names only when confirmed. This does not authorize inventing student profiles or inferring roles for other coauthors. Keep the legend above all publication lists.
- Publication display labels use `[venue'YY]`, such as `[Cluster'26]`, `[BigData'24]`, and `[TC'23]`. `publication_format.py` formats these labels across all demos, using the `short` field without its `IEEE ` prefix and a two-digit year. Render brackets as HTML text, not CSS-generated content. Publication `id` values must be stable and unique. All publications appear on the homepage. Preserve the `selected` field for possible later highlighting.
- Distinguish accepted papers from preprints. Do not overwrite a conference title with a preprint title without checking which version is intended.
- Preserve the owner's name, email, links, and existing public lab name unless the owner explicitly updates them.
- Do not use a search result snippet alone to assert a new paper's full metadata. Read the primary paper or publisher record.
- Preserve old URLs, course resources, and PDFs during any migration of the existing GitHub Pages repository. Add redirects if routes change.

## Design rules

- The owner chose UNC Charlotte colors. Light mode uses official Charlotte Green (#005035) for links and navigation, white (#FFFFFF) surfaces, charcoal body text, and restrained Niner Gold (#A49665) for section markers and active-navigation underlines. Gold is decorative, not small text on white. Preserve this palette for future logo and slide work. Colors were verified against the university brand palette on October 9, 2026. Avoid gradients, decorative animation, icon collections, and dashboard-like panels.
- Retain semantic headings, keyboard access, visible focus, reduced-motion support, and narrow-screen layouts.
- News text is 16px. No text may be smaller, including labels, author lists, controls, captions, contact details, and mobile layouts. Preserve compact spacing without shrinking type.
- Sponsors are NSF, DOE, and UNC Charlotte, with official local logo assets, full alt text, and original transparent artwork in both themes; sponsor sections show only linked logos, without descriptions, captions, project/program lists, cards, or background panels. Keep logo source provenance in `assets/logos/README.md`. Charlotte has no supplied program metadata; do not invent awards or support amounts.
- Use relative links and local assets. Do not add external fonts, analytics, remote data fetching, npm frameworks, or a backend for routine content changes.
- The bundled fonts are an intentional owner-requested exception to the original system-font-only demo. Use their local assets and preserve the included licenses. Do not add a CDN request.
- Keep all demos consistent until the owner selects one. Once chosen, remove the alternate cleanly if requested.
- The owner's additional reference is `https://wdong5.github.io/`. Adapt its clear personal/lab distinction, anchored navigation, compact dated news, and small accent markers beside section headings. Preserve our green palette and original layout. Its inspected font stack starts with Palatino, with other serif fallbacks. The selected `palatino` preset uses locally hosted TeX Gyre Pagella for consistent typography across platforms, with Palatino as fallback. Preserve its regular, bold, italic, and bold italic WOFF faces and GUST license. The WOFF files preserve the original font data; they are converted from CTAN OpenType files without subsetting or design changes.
- The additional owner reference `https://picomp-lab.github.io/` informs only the `/compact/` demo: wide reading column, right-hand image, compact dated rows, and section bars. Preserve Charlotte colors, local Pagella fonts, personal-page news, and the separate lab page. Do not copy the reference lab's people, affiliations, sponsors, or research claims.
- Future logos and slide templates should reuse the selected design's color and typography hierarchy. A new logo is outside the current scope.

## Example owner requests

"Add this accepted paper, mark it selected, and announce it in news for October 2026."

"Add these student profiles exactly as supplied. Show current students before alumni."

"Update the project description and link its code repository. Preserve both layouts."

"Review my latest supplied CV for website updates. Show any uncertain facts for review."

There is no scheduled update job or automatic fact-discovery pipeline. Routine updates are made when the owner asks Codex or Claude to update the repository.

## Content editor

The owner authorized a form-based content editor at `/admin/`. `editor/schema.py` defines forms; `editor/content.py` and `assets/editor-model.js` validate complete content packages. `build.py` generates the editor seed and schema. Keep browser drafts, import/export, and preview functional. The hosted editor does not directly publish; preserve honest messaging about that limitation.

The optional `scripts/editor_server.py` is an owner-requested local editing service, an exception to the routine no-backend rule. It uses only the standard library, binds to loopback, requires same-origin requests and its session token, protects against stale drafts, validates/builds before saving, and backs up source changes. Local publishing requires a GitHub origin on synchronized `main` and the user's existing local Git authentication; do not collect or embed credentials. Failed pushes must be retryable without duplicate commits. `scripts/apply_content.py` applies exported drafts using the same checks. `.editor-state/` must remain ignored.

Run the editor Python and Node regression tests after changing this functionality. Public pages remain static and readable without JavaScript; the editor itself requires JavaScript. Do not edit generated `dist/admin/` directly.

## Design editor maintenance

The owner authorized Design controls, live desktop/mobile previews, presets, and reset. `content/design.json` is the authoritative active design for every layout. `editor/design.py` defines bounded control groups, original defaults, contrast checks, and token generation; `assets/design-model.js` mirrors its validation/tokens in the browser. Keep their outputs equivalent. `assets/design.css` consumes these variables after layout CSS. `build.py` generates `design-tokens.css`, active palettes, preview defaults, and portrait-position attributes. Fonts stay local, Chinese names retain 行楷, logos keep their original artwork, and news remains scrollable.

`assets/design-editor.js` shows actual current pages in sandboxed iframes after stripping scripts and resolving relative assets. Design previews support all four layouts, personal/lab pages, light/dark, and 1100px/390px viewports. Draft content has a separate preview. Keep sliders and numeric inputs synchronized, preserve draft changes, and never silently apply design drafts to the public site. Named presets are browser-local; exported content packages include the current design. Reset only design settings, without changing content.

Validation enforces 16px minimum text, bounded layout/spacing values, allowed bundled/system font stacks, six-digit colors, and 4.5:1 contrast for body/secondary/link text on both surfaces. Do not accept arbitrary executable CSS. Preserve stale-draft protection and include `design.json` in local saves/backups/publishing. Run the Python and Node editor tests, including preview/build token equivalence and all-layout save checks, after changes.

## GitHub checkout and migration

This is the GitHub Pages codebase. `dist/` is ignored and regenerated. Do not stage ignored output; the local editor publishes source content only when output is not tracked. Keep the Pages workflow on `main` and preserve a review branch until the owner chooses to launch. The root `index.html` is the legacy Google Sites redirect, not the new homepage template. Use the generators for new layout changes.

`content/legacy.json` specifies original underscore HTML routes, `assets/main.css`, `files/`, and `imgs/` to copy unchanged into output. Preserve these files and URLs. Checks verify exact resource bytes separately from new-page metadata and links. The local editor's temporary builds must copy these resources too. No new student information is public until supplied by the owner.

The ChatGPT demo is a separate Sites source/deployment. GitHub changes do not synchronize it automatically. Read README local instructions before editing; use Python 3.9+, rerun build/check after code edits, and push source to the requested branch.

## Latest profile and publication refinement

The owner now requests only the official CCI logo in the top header. Keep it left aligned, with navigation and theme controls on the right. Preserve the original artwork on its white background in both modes. The horizontal UNC Charlotte logo remains in Sponsors, not the header. Profile controls show exactly Google Scholar, CV, the email address, and the room together in one nonwrapping row in the main column. On narrow screens this row scrolls horizontally without reducing text size. Publication labels stay on one line; reserve at least eight body-size units for the desktop label column and use intrinsic sizing for longer labels. Publication search and year controls were removed; all papers stay visible. The author legend only explains underlined student names; PI authors remain bold without a legend sentence describing bold.

## Design XML interchange

The owner authorized XML import/export and an Optima trial. `editor/design_xml.py` and `assets/design-xml.js` implement version-1 design-only XML and must stay equivalent. `content/design.json` remains the only active design source. Build output `/assets/design.xml` exports the published settings; files under `assets/design-examples/` are reversible snapshots. UI imports update only the design draft; local Save files performs validation/backups/builds. `scripts/design_xml.py` provides equivalent CLI export/import. Reject extra/missing groups or attributes, unsafe declarations, arbitrary CSS, invalid bounds/contrast, and files over 64 KiB. Keep Chinese 行楷 styling independent of the English Optima trial. Run XML round-trip/rejection/content-preservation tests alongside existing editor tests.

## Header refinement

The owner requested left-aligned institutional logos with right-aligned navigation and theme controls across the demos and sun/moon theme controls. Keep the logo group on the left using its auto end margin, with the other header controls aligned right, with safe navigation overflow on narrow screens. The theme button contains monochrome SVG symbols, has accessible action labels/tooltips, and shows moon to offer dark mode or sun to offer light mode. Preserve these symbols in design preview rather than replacing them with text.

## Sponsor presentation

The owner requested logo-only sponsors: retain the section heading and three linked original logos, with transparent backgrounds in both modes. Program metadata remains in `content/lab.json` for maintenance but is not displayed. Keep accessible organization names in image alt text. Institutional header logo panels remain separate from this sponsor-specific change.

## Footer and name-style review

The footer displays `Last update: (date)` from `profile.updated`, including on mobile. Update that source date intentionally when making visible changes; avoid nondeterministic build timestamps. The personal homepage recruiting sentence no longer repeats an email link; the primary contact chip remains. `fonts.html#chinese-fonts` compares 楷体, 行楷, 草书 with actual three-character local font subsets. `?chinese-font=kai|xingkai|cursive` gives reversible review previews, carried across internal page navigation by `assets/name-fonts.js`. The saved/default name style remains 行楷 until the owner chooses another. Preserve each font's license and regenerate its subset if name characters change.

## Lab title and confirmed roster

The lab hero shows only `HPDi Lab` and the mission paragraph. Do not reintroduce the university/department eyebrow or the full lab name beneath the title. The full name stays in profile metadata. Confirmed team records have `approved: true`, concise `bio`/`topic` fields, and `source_url`; roles omit time-sensitive year-in-program labels. Preserve the original team page's Alumni grouping for Raivat and do not infer graduation or joining dates. Original team photos were inaccessible during import; the roster is text-only. Sponsor Charlotte uses the same original `logos/charlotte-horizontal.png` asset supplied by the owner; sponsors occupy three equal-width columns with centered, identical 240×96px image boxes and proportional artwork; on narrow screens they form equally centered rows.

## Latest lab directory refinement

The owner confirmed Aagat Pokhrel as a displayed Students entry; keep the generic Team member role until further information is supplied, and do not infer a joining date. Adelina Zheng belongs to Alumni as a summer REU student and Brown University undergraduate; no year is supplied. People use the same responsive three-column grid for Faculty, Students, and Alumni (two columns on medium screens and one on phones), without profile divider lines or a separate PI portrait layout. The lab joining section is removed. Lab mission text includes a linked PI introduction and focuses on scientific data management, compression, HPC systems, and machine learning. The homepage browser title is Jinzhen Wang | Assistant professor, University of North Carolina at Charlotte, derived from profile fields; lab page browser titles are HPDi Lab. The remaining CCI header logo has no added padding and aligns with the page content's left edge. Do not reintroduce a university header logo.

Sponsor alignment uses three equal-width columns, each with a centered 240×96px image box. Preserve this even distribution and equal image dimensions; do not restore a flex group aligned to one side. On phones, use evenly centered rows with the same image-box size.

## Primary editor preview
Content previews use the actual primary generated pages through the local build.
Do not introduce a second JavaScript page renderer. Copy current source modules
into isolated draft builds, preserve validation/revision protections, and exclude
Git metadata, generated output, credentials and local state. Hosted editing exports
drafts; exact previews require the loopback editor. `python3 edit.py` starts it.

## Current simplified workflow (supersedes prior editor/design UI instructions)
Use python3 edit.py for startup: fetch origin and fast-forward clean local-design
checkouts. Preserve dirty local-design files and allow reopening saved content.
Open local files if offline or diverged; never merge main automatically.
Do not switch away from dirty other branches or unfinished merges.
Publish commits summarized content changes and pushes only local-design.
Main remains the deployment branch and is changed through review/merge.
The browser editor supports content only; do not restore design forms/presets.
Design changes use scripts/design_xml.py with supported XML, or source edits.
Content preview must use the current primary build without a duplicate renderer.
