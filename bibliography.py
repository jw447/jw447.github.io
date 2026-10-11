"""Format citations from publisher-deposited Crossref DOI metadata."""
import json
import re
import difflib
from urllib.parse import quote, urlencode
from urllib.request import urlopen, Request


def text(value):
    return str(value).replace('\\', r'\textbackslash{}').replace('&', r'\&').replace('%', r'\%').replace('_', r'\_').replace('#', r'\#').replace('{', r'\{').replace('}', r'\}')


def citation(paper):
    if paper.get('bibtex', '').strip(): return paper['bibtex'].strip()
    meta = paper.get('citation', {})
    kind = meta.get('type') or ('article' if any(x in paper.get('venue', '') for x in ('Transactions', 'Letters', 'Journal')) else 'inproceedings')
    fields = {'title': meta.get('title', paper.get('title', '')), 'author': meta.get('author', ' and '.join(paper.get('authors', '').split(', '))),
              'journal' if kind == 'article' else 'booktitle': meta.get('venue', paper.get('venue', '')), 'year': meta.get('year', paper.get('year', ''))}
    for key in ('volume', 'number', 'pages', 'publisher', 'doi', 'url'):
        if meta.get(key): fields[key] = meta[key]
    if not meta and paper.get('doi'): fields.update(doi=paper['doi'], url='https://doi.org/' + paper['doi'])
    lines = [f'  {key} = {{{{{text(value)}}}}}' if key == 'title' else f'  {key} = {{{text(value)}}}' for key, value in fields.items()]
    return '@' + kind + '{' + paper['id'] + ',\n' + ',\n'.join(lines) + '\n}'


def from_metadata(meta):
    dates = meta.get('published-print') or meta.get('published') or meta.get('issued')
    authors = ' and '.join((a.get('family', '') + ', ' + a.get('given', '')).strip(', ') if a.get('family') else '{' + a.get('name', '') + '}' for a in meta.get('author', []))
    return dict(type='article' if meta.get('type') == 'journal-article' else 'inproceedings', title=meta['title'][0],
                author=authors, venue=meta.get('container-title', [''])[0], year=dates['date-parts'][0][0],
                volume=meta.get('volume', ''), number=meta.get('issue', ''), pages=re.sub(r'[-–]+', '--', meta.get('page', '')),
                publisher=meta.get('publisher', ''), doi=meta['DOI'], url='https://doi.org/' + meta['DOI'])


def lookup(paper):
    doi = paper.get('doi', '').strip().removeprefix('https://doi.org/')
    if doi:
        if not re.fullmatch(r'10\.\d{4,9}/[^\s]+', doi): raise ValueError('Enter a DOI such as 10.1145/3721145.3725763.')
        url = 'https://api.crossref.org/works/' + quote(doi, safe='')
    else:
        if not paper.get('title'): raise ValueError('Enter a paper title or DOI first.')
        url = 'https://api.crossref.org/works?' + urlencode({'query.title': paper['title'], 'rows': 1})
    request = Request(url, headers={'User-Agent': 'HPDi-WebsiteEditor/1.0', 'Accept': 'application/json'})
    with urlopen(request, timeout=15) as response: meta = json.load(response)['message']
    if not doi:
        meta = meta['items'][0]
        if difflib.SequenceMatcher(None, paper['title'].lower(), meta['title'][0].lower()).ratio() < .92:
            raise ValueError('No confident title match. Enter the publisher DOI or paste its BibTeX export.')
    data = from_metadata(meta)
    return dict(ok=True, doi=data['doi'], bibtex=citation({**paper, 'bibtex': '', 'citation': data}), source='https://api.crossref.org/works/' + data['doi'])
