"""Shared, static lab portrait cards with accessible profile details."""
import html
import re
from pathlib import Path


def render_people(profile, people, asset):
    esc = lambda value: html.escape(str(value), quote=True)
    pi = dict(name=profile['name'], role='Principal Investigator', bio=' '.join(profile['bio']),
              topic=', '.join(profile['interests']), photo='jinzhen-wang.jpg', url='',
              keywords=[], group='Current')
    current = [pi] + [person for person in people if person.get('group') != 'Alumni']
    alumni = [person for person in people if person.get('group') == 'Alumni']

    def card(person, number):
        name = person['name']
        photo = person.get('photo', '')
        if photo and re.fullmatch(r'(?:people/)?[a-zA-Z0-9_-]+\.(?:jpg|jpeg|png|webp)', photo) and (Path(__file__).parent / 'assets' / photo).is_file():
            portrait = f'<img class="person-photo" src="{esc(asset + photo)}" alt="{esc(name)}" width="180" height="180" loading="lazy">'
        else:
            initials = ''.join(word[0] for word in name.split()[:2])
            portrait = f'<div class="person-photo-placeholder" role="img" aria-label="Photo not yet available for {esc(name)}"><span aria-hidden="true">{esc(initials)}</span><span class="photo-pending">Photo forthcoming</span></div>'
        details = f'<p><strong>{esc(name)}</strong></p><p>{esc(person["role"])}</p>'
        for key in ('bio', 'topic'):
            if person.get(key):
                details += f'<p>{esc(person[key])}</p>'
        if person.get('joined'):
            details += f'<p>Joined {esc(person["joined"])}</p>'
        name_html = f'<a href="{esc(person["url"])}">{esc(name)}</a>' if person.get('url') else esc(name)
        keywords = person.get('keywords', [])
        tags = ''.join(f'<li>{esc(word)}</li>' for word in keywords)
        keyword_html = f'<ul class="person-keywords" aria-label="Research keywords">{tags}</ul>' if tags else ''
        return f'<article class="person person-card"><button class="person-portrait person-open" type="button" aria-label="View biography of {esc(name)}" aria-haspopup="dialog" data-person-dialog="person-dialog-{number}">{portrait}<span class="person-view">View profile</span></button><h4>{name_html}</h4><p class="person-role">{esc(person["role"])}</p>{keyword_html}<details class="person-touch-details"><summary>Biography</summary>{details}</details><dialog class="person-dialog" id="person-dialog-{number}" aria-labelledby="person-title-{number}"><button class="person-close" type="button" aria-label="Close biography">×</button><div class="person-dialog-photo">{portrait}</div><div class="person-dialog-copy"><h3 id="person-title-{number}">{esc(name)}</h3>{details}</div></dialog></article>'


    result = '<div class="people-grid">' + ''.join(card(person, index) for index, person in enumerate(current)) + '</div>'
    if alumni:
        result += '<div class="people-group"><h3>Alumni</h3><div class="people-grid">' + ''.join(card(person, index + len(current)) for index, person in enumerate(alumni)) + '</div></div>'
    return result
