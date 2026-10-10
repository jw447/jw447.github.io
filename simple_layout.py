"""Single-column demo adapted from the owner's Claude example.

Shares the existing JSON content and standard-library build; no Jekyll runtime.
"""
import html
from datetime import datetime
from publication_format import publication_label


def render(out, profile, settings, lab, news, papers, teaching, projects, people, palette, *, variant='simple', design_settings=None):
    """Shared renderer with an optional compact, PiComp-inspired presentation."""
    compact = variant == 'compact'
    folder = out / variant
    folder.mkdir(exist_ok=True)
    esc = lambda value: html.escape(str(value), quote=True)
    def link(label, url):
        return f'<a href="{esc(url)}">{esc(label)}</a>'

    student_authors = set(settings.get('student_authors', []))
    def authors(paper):
        parts = []
        for name in paper['authors'].split(', '):
            text = esc(name)
            if name == profile['name']:
                text = f'<span class="me">{text}</span>'
            if name in student_authors:
                text = f'<span class="lab">{text}</span>'
            parts.append(text)
        return ', '.join(parts)

    def publications(items):
        result = ''
        for year in sorted({p['year'] for p in items}, reverse=True):
            result += f'<h3 class="year">{year}</h3><ul class="pubs">'
            for paper in [p for p in items if p['year'] == year]:
                venue = publication_label(paper)
                resources = ''.join(link(x['label'], x['url']) for x in paper.get('links', []))
                note = f' <span class="pub-note">{esc(paper["note"])}</span>' if paper.get('note') else ''
                result += f'''<li class="pub" id="{esc(paper['id'])}"><span class="venue">{esc(venue)}</span><div class="pub-body"><p class="pub-title">{esc(paper['title'])}</p><p class="pub-authors">{authors(paper)}</p><p class="pub-where"><em>{esc(paper['venue'])}</em>, {year}{note}</p><p class="pub-links">{resources}</p></div></li>'''
            result += '</ul>'
        return result

    legend = f'<p class="author-legend"><span class="lab">Underlined</span> names are HPDi Lab students. {link("Google Scholar", profile["scholar"])}.</p>'
    def newslist(items):
        rows = []
        for item in items:
            date = datetime.strptime(item['date'], '%Y-%m').strftime('%b %Y')
            text = link(item['text'], item['url']) if item.get('url') else esc(item['text'])
            rows.append(f'<li><time datetime="{item["date"]}">{date}</time><div>{text}</div></li>')
        return '<ul class="news">' + ''.join(rows) + '</ul>'

    def page(filename, title, body, lab_page=False):
        nav = []
        for item in lab['navigation'] if lab_page else settings['navigation']:
            if item['kind'] == 'local':
                url = '#' + item['target']
            elif item['kind'] == 'section':
                url = ('#' if filename == 'index.html' else 'index.html#') + item['target']
            else:
                url = item['target']
            switch = item['kind'] == 'page'
            if switch:
                nav.append('<span class="nav-divider" aria-hidden="true"></span>')
            nav.append(f'<a href="{esc(url)}"'+(' class="nav-switch"' if switch else '')+(' aria-current="page"' if url == filename else '')+f'>{esc(item["label"])}</a>')
        identity = profile['lab'] if lab_page else profile['name']
        compact_styles = '<link rel="stylesheet" href="../assets/compact.css">' if compact else ''
        demo_links = '<p class="demo-links">Other demos: <a href="../index.html">Classic</a> · <a href="../simple/index.html">Simple</a> · <a href="../editorial/index.html">Editorial</a></p>' if compact else ''
        result = f'''<!doctype html><html lang="en" data-portrait="{esc(design_settings['layout']['portrait_position'])}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)} · {esc(profile['name'])}</title><meta name="description" content="Academic website of Jinzhen Wang and HPDi Lab at UNC Charlotte."><meta name="theme-color" content="{esc(palette['accent'])}"><link rel="icon" href="../assets/simple-mark.svg" type="image/svg+xml"><link rel="preload" href="../assets/fonts/texgyrepagella-regular.woff" as="font" type="font/woff" crossorigin><script src="../assets/theme.js"></script><script src="../assets/name-fonts.js" defer></script><link rel="stylesheet" href="../assets/colors.css"><link rel="stylesheet" href="../assets/simple.css"><link rel="stylesheet" href="../assets/theme.css"><link rel="stylesheet" href="../assets/sponsors.css">{compact_styles}<link rel="stylesheet" href="../assets/design-tokens.css"><link rel="stylesheet" href="../assets/design.css"></head><body data-layout="{variant}"><a class="skip" href="#main">Skip to content</a><header class="site-header"><div class="wrap header-row"><div class="institution-logos" aria-label="University and college"><a class="institution-logo university-logo" href="https://www.charlotte.edu/"><img src="../assets/logos/charlotte-horizontal.png" alt="UNC Charlotte" width="270" height="70"></a><a class="institution-logo college-logo" href="https://cci.charlotte.edu/"><img src="../assets/logos/cci.png" alt="College of Computing and Informatics" width="288" height="115"></a></div><nav class="nav" aria-label="{'Lab' if lab_page else 'Main'}">{''.join(nav)}</nav><button class="theme-toggle" type="button" aria-label="Switch to dark mode" aria-pressed="false" hidden><svg class="theme-icon theme-moon" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M21 12.8A9 9 0 1 1 11.2 3 7 7 0 0 0 21 12.8Z"/></svg><svg class="theme-icon theme-sun" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42m0-14.14-1.42 1.42M6.35 17.65l-1.42 1.42"/></svg></button></div></header><main id="main" class="wrap">{body}</main><footer class="site-footer"><div class="wrap footer-row"><address><strong>{esc(identity)}</strong><br>{esc(profile['department'])}<br>{esc(profile['university'])}</address><p class="footer-meta">{esc(profile['lab_name'])}<br>Last update: {esc(profile['updated'])}</p>{demo_links}</div></footer></body></html>'''
        (folder / filename).write_text(result)

    bio = ''.join(f'<p>{esc(p)}</p>' for p in profile['bio'])
    bio = bio.replace('High-Performance Data Intensive (HPDi) Lab', '<a href="lab.html">High-Performance Data Intensive (HPDi) Lab</a>')
    motif = '<figure class="motif">' + (out / 'assets/simple-refinement.svg').read_text() + '<figcaption>Illustration: one field, approximated with error bounds that tighten from left to right.</figcaption></figure>'
    if compact:
        motif = ''
    name_heading = esc(profile['name']) + (f' <span class="chinese-name" lang="zh-Hans">{esc(profile["name_chinese"])}</span>' if profile.get('name_chinese') else '')
    controls = f'''<div class="profile-controls" role="region" aria-label="Profile links and contact details" tabindex="0"><a class="profile-button" href="{esc(profile['scholar'])}">Google Scholar</a><a class="profile-button" href="{esc(profile['cv'])}">CV</a><a class="contact-chip" href="mailto:{esc(profile['email'])}">{esc(profile['email'])}</a><span class="contact-chip">{esc(profile['office'])}</span></div>'''
    intro = f'''<section class="intro" id="about"><img class="portrait" src="../assets/jinzhen-wang.jpg" alt="Portrait of {esc(profile['name'])}" width="168" height="168"><div class="intro-text"><h1>{name_heading}</h1><p class="role">{esc(profile['role'])} of Computer Science<br>{esc(profile['university'])}<br>Director, {link(profile['lab'], 'lab.html')}</p>{controls}</div></section><section class="bio prose">{bio}<p class="recruit"><strong>Prospective students:</strong> {esc(lab['recruiting'])} {link('Explore HPDi Lab', 'lab.html')}.</p></section>'''
    if compact:
        intro = f'''<section class="compact-intro" id="about"><h1>{name_heading}</h1><p class="compact-role">{esc(profile['role'])}</p><div class="intro-columns"><div><div class="compact-bio">{bio}</div>{controls}<p class="recruit">{esc(lab['recruiting'])} {link('Explore the lab →', 'lab.html')}</p></div><img class="portrait" src="../assets/jinzhen-wang.jpg" alt="Portrait of {esc(profile['name'])}" width="174" height="174"></div></section>'''
    courses = '<ul class="courses">'
    for course in teaching:
        courses += f'<li><span class="course-code">{esc(course["code"])}</span><div><p class="course-name">{esc(course["title"])}</p><p class="course-meta">{esc(course["institution"])}, {esc(course["terms"])}</p></div></li>'
    courses += '</ul>'
    body = intro + motif + '<section id="news"><h2>News</h2><div class="news-scroll" role="region" aria-label="News updates" tabindex="0">' + newslist(news) + '</div>'
    body += '</section><section id="papers"><h2>Publications</h2>' + legend + publications(papers) + '</section>'
    body += '<section id="teaching"><h2>Teaching</h2>' + courses + '</section>'
    page('index.html', 'Home', body)
    page('publications.html', 'Publications', '<h1 class="page-title">Publications</h1>' + legend + publications(papers))
    page('teaching.html', 'Teaching', '<h1 class="page-title">Teaching</h1>' + courses)
    page('about.html', 'About', '<h1 class="page-title">About</h1><div class="prose">' + bio + '</div><h2>Research interests</h2><p>' + esc(', '.join(profile['interests'])) + '</p>')

    body = f'<section class="lab-hero" id="lab-overview"><h1 class="page-title">{esc(profile["lab_name"])}</h1><p class="lede">{esc(lab["mission"])}</p></section>' + motif
    if compact:
        body = f'<section class="lab-hero" id="lab-overview"><h1 class="page-title">{esc(profile["lab"])}</h1><p class="lab-full-name">{esc(profile["lab_name"])}</p><p class="lede">{esc(lab["mission"])}</p></section>'
    body += '<section id="research"><h2>Research</h2><div class="research-list">'
    for theme in lab['research']:
        body += f'<div class="thrust"><div><h3>{esc(theme["title"])}</h3><p>{esc(theme["description"])}</p></div></div>'
    body += '</div></section><section id="projects"><h2>Projects</h2>'
    for project in projects:
        context = f'<p class="project-context">{esc(project["context"])}</p>' if compact and project.get('context') else ''
        body += f'<div class="thrust"><div><h3>{esc(project["name"])}</h3>{context}<p>{esc(project["description"])}</p><p class="links">'+''.join(link(x['label'], x['url']) for x in project.get('links', []))+'</p></div></div>'
    body += f'</section><section id="people"><h2>People</h2><div class="people"><div class="person person-lead"><img class="avatar" src="../assets/jinzhen-wang.jpg" alt="Jinzhen Wang" width="112" height="112"><div><p class="person-name">{link(profile["name"], "index.html")}</p><p class="person-role">Director; {esc(profile["role"])}</p></div></div></div>'
    for group in ['Students', 'Alumni', 'Collaborators']:
        members = [p for p in people if p.get('group', 'Students') == group]
        if group != 'Students' and not members:
            continue
        body += f'<h3>{group}</h3>'
        if not members:
            body += '<p class="placeholder">Student profiles will be added here.</p>'
        for person in members:
            name = link(person['name'], person['url']) if person.get('url') else esc(person['name'])
            body += f'<div class="person-text"><p class="person-name">{name}</p><p class="person-role">{esc(person["role"])}</p>'
            if person.get('topic'):
                body += f'<p>{esc(person["topic"])}</p>'
            body += '</div>'
    body += '</section>'
    body += '<section id="join"><h2>Join us</h2><p>' + esc(lab['recruiting']) + '</p><p>' + link(profile['email'], 'mailto:' + profile['email']) + '</p></section>'
    body += '<section id="sponsors"><h2>Sponsors</h2><div class="sponsor-grid">'
    for sponsor in lab.get('sponsors', []):
        logo = f'<a class="sponsor-logo-panel" href="{esc(sponsor["url"])}"><img src="../assets/{esc(sponsor["logo"])}" alt="{esc(sponsor["name"])} logo" width="240" height="96" loading="lazy"></a>' if sponsor.get('logo') else ''
        body += logo
    body += '</div></section>'
    page('lab.html', profile['lab'], body, lab_page=True)
    for extra in settings.get('extra_pages', []):
        body = f'<h1 class="page-title">{esc(extra["title"])}</h1><p class="lede">{esc(extra["description"])}</p>'
        for item in extra.get('items', []):
            body += f'<h2>{esc(item["title"])}</h2><p>{esc(item["description"])}</p>'
            if item.get('url'):
                body += '<p>' + link('Details', item['url']) + '</p>'
        page(extra['file'], extra['title'], body)
    page('404.html', 'Page not found', '<h1 class="page-title">Page not found</h1><p>' + link('Return home', 'index.html') + '</p>')
