"""Shared project cards and dedicated introductions."""
from html import escape as e

def project_cards(projects):
    cards = []
    for p in projects:
        cards.append(f'<a class="portfolio-card" href="project-{e(p["id"])}.html"><span class="portfolio-context">{e(p["context"])}</span><h3>{e(p["name"])}</h3><p>{e(p["subtitle"])}</p><span class="portfolio-more">Explore project →</span></a>')
    return '<div class="portfolio-grid">'+''.join(cards)+'</div>'

def project_detail(p, papers=()):
    body = f'<a href="lab.html#projects">← All projects</a><header class="project-introduction"><p>{e(p["context"])}</p><h1>{e(p["name"])}</h1></header><section class="project-detail-section"><h2>Overview</h2><p>{e(p["description"])}</p></section>'
    related = [paper for paper in papers if paper['id'] in p.get('publication_ids', [])]
    if related:
        body += '<section class="project-detail-section"><h2>Publications</h2>'
        for paper in related:
            body += f'<article class="project-paper"><h3>{e(paper["title"])}</h3><p class="project-paper-meta">{e(paper["authors"])} <span class="project-paper-venue"> · {e(paper["short"])} {paper["year"]}</span></p>'
            body += ''.join(f'<a href="{e(x["url"],quote=True)}">Paper →</a>' for x in paper.get('links', [])) + '</article>'
        body += '</section>'
    return body
