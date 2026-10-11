"""Shared project cards and dedicated introductions."""
from html import escape as e

def project_cards(projects):
    cards = []
    for p in projects:
        cards.append(f'<a class="portfolio-card" href="project-{e(p["id"])}.html"><h3>{e(p["name"])}</h3><p>{e(p.get("summary") or p["description"])}</p><span class="portfolio-more">Explore project →</span></a>')
    return '<div class="portfolio-grid">'+''.join(cards)+'</div>'

def project_detail(p, papers=()):
    body = f'<a href="lab.html#projects">← All projects</a><header class="project-introduction"><h1>{e(p["name"])}</h1></header><section class="project-detail-section"><h2>Overview</h2><p>{e(p["description"])}</p></section>'
    related = [paper for paper in papers if paper['id'] in p.get('publication_ids', [])]
    if related:
        body += '<section class="project-detail-section"><h2>Publications</h2>'
        for paper in related:
            body += f'<article class="project-paper"><h3>{e(paper["title"])}</h3><p class="project-paper-meta">{e(paper["authors"])} <span class="project-paper-venue"> · {e(paper["short"])} {paper["year"]}</span></p>'
            links = paper.get('links', [])
            preferred = next((x for x in links if x.get('label', '').lower() == 'paper'), links[0] if links else None)
            if preferred: body += f'<a href="{e(preferred["url"],quote=True)}">Paper →</a>'
            body += '</article>'
        body += '</section>'
    return body
