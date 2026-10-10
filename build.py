#!/usr/bin/env python3
"""Build academic demos with Python's standard library."""
import json
import html
import shutil
from pathlib import Path
from datetime import datetime
from simple_layout import render as render_simple
from publication_format import publication_label
from editor.content import bundle as editor_bundle
from editor.schema import SECTIONS as editor_sections
from editor.design import default_design, token_css, validate_design
from editor.design_xml import to_xml

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'dist'
OUT.mkdir(parents=True, exist_ok=True)
shutil.copytree(ROOT / 'assets', OUT / 'assets', dirs_exist_ok=True)
def load(name): return json.loads((ROOT / 'content' / (name+'.json')).read_text())
def e(value): return html.escape(str(value), quote=True)
profile=load('profile'); news=sorted(load('news'),key=lambda x:x['date'],reverse=True)
settings=load('site')
brand=load('brand')
design_settings=load('design')
design_errors=validate_design(design_settings)
if design_errors: raise ValueError('\n'.join(design_errors))
(OUT/'assets'/'design-tokens.css').write_text('/* Generated from content/design.json. */\n'+token_css(design_settings))
# One palette feeds both layouts, browser chrome, and the temporary favicon.
palette=design_settings['light']
dark_palette=design_settings['dark']
tokens=lambda colors: ''.join(f'--{key}:{value};' for key,value in colors.items())
(OUT/'assets'/'colors.css').write_text('/* Generated from content/design.json; original palette provenance is in brand.json. */\n:root{color-scheme:light;'+tokens(palette)+'}\n@media(prefers-color-scheme:dark){:root:not([data-theme="light"]){color-scheme:dark;'+tokens(dark_palette)+'}}\nhtml[data-theme="dark"]{color-scheme:dark;'+tokens(dark_palette)+'}\n')
(OUT/'assets'/'favicon.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="8" fill="{palette["accent"]}"/><text x="32" y="43" text-anchor="middle" font-family="Georgia,serif" font-size="32" fill="{palette["paper"]}">W</text></svg>')
papers=sorted(load('publications'),key=lambda x:x['year'],reverse=True)
projects=load('projects'); teaching=load('teaching'); lab=load('lab')
people=[person for person in load('people') if person.get('approved') is True]
name_heading=e(profile['name'])+(f' <span class="chinese-name" lang="zh-Hans">{e(profile["name_chinese"])}</span>' if profile.get('name_chinese') else '')
FONTS=[('optima','Optima','Current trial. Uses installed Optima, with Candara and locally hosted Source Sans 3 as fallbacks.'),('source-sans','Source Sans 3','Warm, readable, understated sans-serif alternative.'),('inter','Inter','Crisp and modern, with a clean sans-serif hierarchy.'),('plex','IBM Plex Sans','A distinctive technical character, well suited to systems research.'),('serif','Source Serif 4 + Source Sans 3','Contemporary serif headings with readable sans-serif body text.'),('palatino','TeX Gyre Pagella / Palatino','Academic serif alternative. Locally hosted TeX Gyre Pagella for body and headings, with Palatino as fallback. Navigation uses Source Sans 3.')]

def link(label,url,cls=''):
    return f'<a class="{e(cls)}" href="{e(url)}">{e(label)}</a>'

def head(title,desc,design,asset):
    return f'''<!doctype html><html lang="en" data-portrait="{e(design_settings['layout']['portrait_position'])}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="{e(desc)}"><meta name="theme-color" content="{e(palette['accent'])}"><title>{e(title)} · Jinzhen Wang</title><link rel="icon" href="{asset}favicon.svg" type="image/svg+xml"><script src="{asset}theme.js"></script><script src="{asset}name-fonts.js" defer></script><link rel="stylesheet" href="{asset}colors.css"><link rel="stylesheet" href="{asset}style.css"><link rel="stylesheet" href="{asset}typography.css"><link rel="stylesheet" href="{asset}theme.css"><link rel="stylesheet" href="{asset}sponsors.css"><link rel="stylesheet" href="{asset}design-tokens.css"><link rel="stylesheet" href="{asset}design.css"><script src="{asset}site.js" defer></script></head><body data-design="{design}" data-font="{e(settings['font'])}"><a class="skip-link" href="#main">Skip to content</a>'''

def sidebar(asset):
    return f'''<aside class="profile" aria-label="Profile"><img class="portrait" src="{asset}jinzhen-wang.jpg" alt="Jinzhen Wang" width="520" height="440"><div class="profile-info"><h2>{e(profile['name'])}</h2><p class="role">{e(profile['role'])}</p><p class="affiliation">Computer Science<br>UNC Charlotte</p><a class="lab-label" href="lab.html">HPDi Lab <span>High-Performance<br>Data Intensive Lab</span></a></div></aside>'''

def page(filename,title,body,design='classic',description=None,lab_page=False):
    d=OUT if design=='classic' else OUT/'editorial'; d.mkdir(parents=True,exist_ok=True)
    asset='assets/' if design=='classic' else '../assets/'
    nav=''
    for item in lab['navigation'] if lab_page else settings['navigation']:
        if item['kind']=='section':
            href=('#' if filename=='index.html' else 'index.html#')+item['target']
            nav+=f'<a class="section-nav" data-section="{e(item["target"])}" href="{e(href)}">{e(item["label"])}</a>'
        elif item['kind']=='local':
            nav+=f'<a class="section-nav" data-section="{e(item["target"])}" href="#{e(item["target"])}">{e(item["label"])}</a>'
        else:
            nav+=f'<a href="{e(item["target"])}"'+(' aria-current="page"' if filename==item['target'] else '')+(' class="nav-lab"' if item['target']=='lab.html' else '')+f'>{e(item["label"])}</a>'
    font_controls='<aside class="font-preview" hidden aria-label="Typography preview"><div class="font-preview-title"><strong>Compare typefaces</strong><a href="fonts.html">View samples →</a></div><div class="font-buttons">'+''.join(f'<button type="button" data-font-choice="{key}" aria-pressed="false">{e(name)}</button>' for key,name,_ in FONTS)+'</div><p id="font-description" role="status" aria-live="polite"></p></aside>'
    s=head(title,description or 'Academic website of Jinzhen Wang at UNC Charlotte. Research, publications, news, and teaching.',design,asset)
    if filename=='fonts.html': s=s.replace(f'<link rel="stylesheet" href="{asset}design.css">','')
    shell='page-shell lab-shell' if lab_page else ('page-shell single-column' if design=='classic' else 'page-shell')
    side=sidebar(asset) if design=='editorial' and not lab_page else ''
    if lab_page:
        body=body.replace('src="__SPONSOR_ASSET__', 'src="'+asset)
    s+=f'''<header class="site-header"><div class="header-inner"><div class="institution-logos" aria-label="University and college"><a class="institution-logo university-logo" href="https://www.charlotte.edu/"><img src="{asset}logos/charlotte-horizontal.png" alt="UNC Charlotte" width="270" height="70"></a><a class="institution-logo college-logo" href="https://cci.charlotte.edu/"><img src="{asset}logos/cci.png" alt="College of Computing and Informatics" width="288" height="115"></a></div><button class="menu-toggle" type="button" aria-controls="site-nav" aria-expanded="false">Menu</button><nav id="site-nav" aria-label="Main navigation">{nav}</nav><button class="theme-toggle" type="button" aria-label="Switch to dark mode" aria-pressed="false" hidden><svg class="theme-icon theme-moon" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M21 12.8A9 9 0 1 1 11.2 3 7 7 0 0 0 21 12.8Z"/></svg><svg class="theme-icon theme-sun" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42m0-14.14-1.42 1.42M6.35 17.65l-1.42 1.42"/></svg></button></div></header><div class="{shell}">{side}<main id="main">{font_controls}{body}</main></div><footer class="site-footer"><span>Jinzhen Wang · HPDi Lab</span><span class="last-update">Last update: {e(profile["updated"])}</span><a href="#main">Back to top ↑</a></footer></body></html>'''
    (d/filename).write_text(s)

def section(title,content,url=None,label=None,cls='',anchor=None):
    attr=f' id="{e(anchor)}"' if anchor else ''
    return f'<section class="section {cls}"{attr}><div class="section-heading"><h2>{e(title)}</h2>{link(label or "View all →",url) if url else ""}</div>{content}</section>'

def newslist(items):
    rows=[]
    for n in items:
        date=datetime.strptime(n['date'],'%Y-%m').strftime('%b %Y')
        text=link(n['text'],n['url']) if n.get('url') else e(n['text'])
        rows.append(f'<li class="news-item"><time datetime="{n["date"]}">{date}</time><div><span class="news-kind">{e(n["kind"])}</span><p>{text}</p></div></li>')
    return '<ul class="news-list">'+''.join(rows)+'</ul>'

def bib(p):
    typ='article' if 'Transactions' in p['venue'] or 'Letters' in p['venue'] or 'Journal' in p['venue'] else 'inproceedings'
    field='journal' if typ=='article' else 'booktitle'
    return '@'+typ+'{'+p['id']+',\n  title = {'+p['title']+'},\n  author = {'+' and '.join(p['authors'].split(', '))+'},\n  '+field+' = {'+p['venue']+'},\n  year = {'+str(p['year'])+'}\n}'

def paperlist(items):
    rows=[]
    student_authors=set(settings.get('student_authors',[]))
    for p in items:
        author_parts=[]
        for name in p['authors'].split(', '):
            text=e(name)
            if name==profile['name']: text=f'<strong>{text}</strong>'
            if name in student_authors: text=f'<span class="student-author">{text}</span>'
            author_parts.append(text)
        authors=', '.join(author_parts)
        links=''.join(link(x['label'],x['url']) for x in p.get('links',[]))
        citation=f'<details class="citation"><summary>BibTeX</summary><pre>{e(bib(p))}</pre><button type="button" class="copy-citation">Copy citation</button></details>'
        rows.append(f'''<article class="paper" data-year="{p['year']}"><div class="paper-venue">{e(publication_label(p))}</div><div class="paper-body"><h3>{e(p['title'])}</h3><p class="authors">{authors}</p><p class="venue-full">{e(p['venue'])}, {p['year']}</p><div class="paper-links">{links}{citation}</div>{f'<p class="paper-note">{e(p["note"])}</p>' if p.get('note') else ''}</div></article>''')
    return '<div class="paper-list">'+''.join(rows)+'</div>'

def intro(title,desc): return f'<div class="page-intro"><p class="eyebrow">HPDi Lab · UNC Charlotte</p><h1>{e(title)}</h1><p class="intro-description">{e(desc)}</p></div>'

bio=''.join('<p>'+e(p)+'</p>' for p in profile['bio'])
bio=bio.replace('High-Performance Data Intensive (HPDi) Lab','<a class="bio-lab-link" href="lab.html">High-Performance Data Intensive (HPDi) Lab</a>')
research='<ul class="research-list">'+''.join('<li>'+e(x)+'</li>' for x in profile['interests'])+'</ul>'
join=f'''<aside class="join-note"><h3>Interested in joining our research?</h3><p>I welcome inquiries from students interested in high-performance computing and scientific data management.</p>{link('Get in touch →','mailto:'+profile['email'])}</aside>'''
profile_controls=f'''<div class="profile-controls" role="region" aria-label="Profile links and contact details" tabindex="0">{link('Google Scholar',profile['scholar'],'profile-button')}{link('CV',profile['cv'],'profile-button')}{link(profile['email'],'mailto:'+profile['email'],'contact-chip')}<span class="contact-chip">{e(profile['office'])}</span></div>'''
home_intro=f'''<section class="home-intro" id="about"><h1>{name_heading}</h1><p class="home-subtitle">Assistant Professor of Computer Science</p>{profile_controls}<div class="bio">{bio}</div>{research}<p class="recruiting-inline"><strong>Prospective students</strong> · Explore {link('HPDi Lab','lab.html')} for research opportunities.</p></section>'''
main_intro=f'''<section class="home-intro" id="about"><div class="home-profile"><img class="portrait" src="assets/jinzhen-wang.jpg" alt="Jinzhen Wang" width="520" height="440"><div class="home-profile-details"><h1>{name_heading}</h1><p class="home-subtitle">{e(profile['role'])}</p>{profile_controls}</div></div><div class="bio">{bio}</div>{research}<p class="recruiting-inline"><strong>Prospective students</strong> · Explore {link('HPDi Lab','lab.html')} for research opportunities.</p></section>'''

author_legend=f'<p class="author-legend"><span class="student-author">Underlined</span> names are HPDi Lab students.</p>'
pubbody=intro('Publications','Research in scientific data management, compression, and high-performance systems.')+author_legend+paperlist(papers)+f'<p class="end-note">{link("Google Scholar →",profile["scholar"])}</p>'
projbody=intro('Research & projects','Efficient methods for managing and understanding scientific data at scale.')
project_content=''
for p in projects:
    project_content+=f'''<article class="project" id="{e(p['id'])}"><p class="eyebrow">{e(p['context'])}</p><h3 class="project-name">{e(p['name'])}</h3><p class="project-subtitle">{e(p['subtitle'])}</p><p>{e(p['description'])}</p>{f'<p class="collaborators">{e(p["people"])}</p>' if p.get('people') else ''}<div class="resource-links">{''.join(link(x['label']+' →',x['url']) for x in p['links'])}</div></article>'''
projbody+=project_content
projbody+=section('Research interests',research)
course_content=''
for t in teaching:
    course_content+=f'''<article class="course"><p class="eyebrow">{e(t['institution'])}</p><h3>{e(t['title'])}</h3><p class="course-code">{e(t['code'])} · {e(t['terms'])}</p>{f'<p>{e(t["description"])}</p>' if t.get('description') else ''}</article>'''
teachbody=intro('Teaching','Courses in parallel computing, computer architecture, and digital systems.')+course_content
newsbody=intro('News','Updates from our research, publications, and academic community.')
for y in sorted({n['date'][:4] for n in news},reverse=True): newsbody+=section(y,newslist([n for n in news if n['date'].startswith(y)]))
peoplebody=intro('Lab directory','Student profiles now belong to the dedicated lab page.')+link('View HPDi Lab people →','lab.html#people')
home_sections=section('News','<div class="news-scroll" role="region" aria-label="News updates" tabindex="0">'+newslist(news)+'</div>',anchor='news')
home_sections+=section('Publications',author_legend+paperlist(papers),profile['scholar'],'Google Scholar →',anchor='papers')
home_sections+=section('Teaching',course_content,anchor='teaching')
fontbody=intro('Typography options','Compare the same academic content in six typeface options. Open a full-page preview to see each font in context.')
fontbody+='<section id="chinese-fonts"><h2>Chinese name styles</h2><p>Compare 王金震 in 楷体、行楷、草书. These previews do not change the saved design.</p><div class="name-font-grid">'
for key,label,description in [('kai','楷体','Regular script · LXGW WenKai'),('xingkai','行楷','Running script · Zhi Mang Xing'),('cursive','草书','Grass script · Liu Jian Mao Cao')]:
    fontbody+=f'<article class="name-font-sample"><h3>{e(label)}</h3><p class="chinese-name" data-name-font="{key}" lang="zh-Hans">{e(profile["name_chinese"])}</p><p>{e(description)}</p>'+link('Preview on homepage →','index.html?chinese-font='+key)+'</article>'
fontbody+='</div></section>'
for key,name,desc in FONTS:
    fontbody+=f'''<section class="font-sample" data-font="{key}"><div class="font-sample-label"><span>{e(name)}</span>{link('Preview full website →','index.html?font='+key+'&preview=fonts')}</div><h2>Jinzhen Wang</h2><h3>High-performance computing & scientific data</h3><p>I lead the High-Performance Data Intensive Lab at UNC Charlotte. My research focuses on data reduction, compression, and parallel and distributed systems.</p><p class="sample-paper">DeepCQ: A Two-Stage Deep-Surrogate Framework for Lossy Compression Quality Prediction</p><p class="font-sample-description">{e(desc)}</p></section>'''
labbody=f'''<section class="lab-hero" id="lab-overview"><p class="eyebrow">UNC Charlotte · Computer Science</p><h1>{e(profile['lab'])}</h1><p class="lab-full-name">{e(profile['lab_name'])}</p><p class="lab-mission">{e(lab['mission'])}</p></section>'''
themes='<div class="research-themes">'+''.join(f'<article><h3>{e(x["title"])}</h3><p>{e(x["description"])}</p></article>' for x in lab['research'])+'</div>'
labbody+=section('Research',themes,anchor='research')+section('Projects',project_content,anchor='projects')
directory=f'''<article class="person pi-person"><h3>{link(profile['name'],'index.html')}</h3><p class="person-role">Principal Investigator</p><p>{e(profile['role'])}, Computer Science · UNC Charlotte</p></article>'''
for group in ['Students','Alumni','Collaborators']:
    members=[p for p in people if p.get('group')==group]
    if not members and group!='Students':continue
    directory+=f'<div class="people-group"><h3>{group}</h3>'
    if not members:directory+='<p class="pending-roster">Student profiles will be added here.</p>'
    for person in members:
        name=link(person['name'],person['url']) if person.get('url') else e(person['name'])
        directory+=f'<article class="person"><h4>{name}</h4><p class="person-role">{e(person["role"])}</p>'
        if person.get('topic'):directory+=f'<p>{e(person["topic"])}</p>'
        if person.get('joined'):directory+=f'<p class="person-detail">Joined {e(person["joined"])}</p>'
        directory+='</article>'
    directory+='</div>'
labbody+=section('People',directory,anchor='people')
labbody+=section('Join the lab',f'<p>{e(lab["recruiting"])}</p>'+link('Contact '+profile['name']+' →','mailto:'+profile['email']),anchor='join')
def sponsor_logo(sponsor,asset=None):
    if not sponsor.get('logo'):return ''
    prefix=asset or '__SPONSOR_ASSET__'
    return f'<a class="sponsor-logo-panel" href="{e(sponsor["url"])}"><img src="{prefix}{e(sponsor["logo"])}" alt="{e(sponsor["name"])} logo" width="240" height="96" loading="lazy"></a>'
sponsor_cards=''.join(sponsor_logo(sponsor,asset=None) for sponsor in lab.get('sponsors',[]))
labbody+=section('Sponsors','<div class="sponsor-grid">'+sponsor_cards+'</div>',anchor='sponsors')
for design in ['classic','editorial']:
    page('index.html','Home',(main_intro if design=='classic' else home_intro)+home_sections,design)
    page('news.html','News',newsbody,design)
    page('publications.html','Publications',pubbody,design)
    page('projects.html','Projects',projbody,design)
    page('lab.html',profile['lab'],labbody,design,lab_page=True)
    page('people.html','People',peoplebody,design)
    page('teaching.html','Teaching',teachbody,design)
    page('fonts.html','Typography options',fontbody,design)
    for extra in settings.get('extra_pages',[]):
        content=intro(extra['title'],extra['description'])
        for item in extra.get('items',[]):
            content+=f'<article class="project"><h2>{e(item["title"])}</h2><p>{e(item["description"])}</p>'+(link('Details →',item['url']) if item.get('url') else '')+'</article>'
        page(extra['file'],extra['title'],content,design)
    page('404.html','Page not found',intro('Page not found','This page may have moved.')+link('Return home →','index.html'),design)
render_simple(OUT,profile,settings,lab,news,papers,teaching,projects,people,palette,design_settings=design_settings)
compact_copy=load('compact')
compact_profile={**profile,'bio':compact_copy['bio']}
compact_projects=[{**project,'description':compact_copy['projects'].get(project['id'],project['description'])} for project in projects]
render_simple(OUT,compact_profile,settings,lab,news,papers,teaching,compact_projects,people,palette,variant='compact',design_settings=design_settings)
(OUT/'admin').mkdir(exist_ok=True)
shutil.copy2(ROOT/'editor/index.html', OUT/'admin/index.html')
(OUT/'admin/editor-data.json').write_text(json.dumps(editor_bundle(ROOT),ensure_ascii=False))
(OUT/'admin/editor-schema.json').write_text(json.dumps(editor_sections,ensure_ascii=False))
(OUT/'assets/design.xml').write_text(to_xml(design_settings),encoding='utf-8')
(OUT/'admin/design-defaults.json').write_text(json.dumps(default_design(),ensure_ascii=False))
(OUT/'.nojekyll').touch()
legacy_path=ROOT/'content/legacy.json'
if legacy_path.exists():
    legacy=json.loads(legacy_path.read_text())
    for name in legacy['files']:
        target=OUT/name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(ROOT/name,target)
    for name in legacy['directories']:
        shutil.copytree(ROOT/name,OUT/name,dirs_exist_ok=True,ignore=shutil.ignore_patterns('.DS_Store'))
(OUT/'assets'/'publications.bib').write_text('\n\n'.join(bib(p) for p in papers)+'\n')
print(f'Built {len(list(OUT.rglob("*.html")))} pages, {len(papers)} papers and {len(news)} news items.')
