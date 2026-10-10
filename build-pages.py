"""Generate secondary page templates from retained reference content (stdlib only)."""
from html import escape
import json
from pathlib import Path
import re
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
HOME = (ROOT / 'page.html').read_text()
DATA = json.loads((ROOT / 'site-data.json').read_text())
PAGES = DATA['pages']
BY_SLUG = {page['slug']: page for page in PAGES}
CATEGORIES = ['sonorisation', 'eclairages', 'pack-son-lights', 'effets-video', 'structures']
SOURCES = ROOT / 'pages'
SOURCES.mkdir(exist_ok=True)


def e(value):
    return escape(str(value), quote=True)


def local_links(markup):
    for page in PAGES:
        markup = markup.replace(page['source'], page['slug'] + '.html')
    return markup


# Navigation and footer come from the homepage so future edits stay consistent.
HEADER = re.search(r'<header\b.*?</header>', HOME, re.S).group(0)
HEADER = local_links(HEADER).replace('href="#accueil"', 'href="index.html#accueil"')
HEADER = HEADER.replace('href="#contact"', 'href="nous-contacter-faq.html#contact"')
HEADER = HEADER.replace('<div class="dropdown-panel">\n        <a href="sonorisation.html">', '<div class="dropdown-panel">\n        <a href="materiel.html">Tout le matériel</a>\n        <a href="sonorisation.html">')
FOOTER = re.search(r'<footer\b.*?</footer>', HOME, re.S).group(0).replace('href="#accueil"', 'href="index.html#accueil"')
CONTACT_FORM = re.search(r'<section class="contact-section.*?</section>', HOME, re.S).group(0)
CONTACT_DIALOG = re.search(r'<dialog class="contact-dialog.*?</dialog>', HOME, re.S).group(0)
LIGHTBOX = re.search(r'<dialog class="lightbox.*?</dialog>', HOME, re.S).group(0)
ARROW = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 19 19 5M5 5h14v14"/></svg>'


def category_nav(active=None):
    links = [('materiel', 'Tout le matériel')] + [(slug, BY_SLUG[slug]['title']) for slug in CATEGORIES]
    return '<nav class="category-nav" aria-label="Catégories de matériel">' + ''.join(f'<a href="{slug}.html"' + (' aria-current="page"' if slug == active else '') + f'>{e(title)}</a>' for slug, title in links) + '</nav>'


def hero(page):
    slug, title = page['slug'], page['title']
    equipment = page['kind'] in ('catalogue', 'hub')
    crumbs = '<a href="index.html">Accueil</a><span aria-hidden="true">/</span>'
    if equipment and slug != 'materiel':
        crumbs += '<a href="materiel.html">Matériel</a><span aria-hidden="true">/</span>'
    crumbs += f'<span aria-current="page">{e(title)}</span>'
    cta = '#catalogue' if page['kind'] == 'catalogue' else '#categories' if page['kind'] == 'hub' else '#contact' if page['kind'] == 'contact' else 'nous-contacter-faq.html#contact'
    label = 'Explorer le catalogue' if page['kind'] == 'catalogue' else 'Choisir mon matériel' if page['kind'] == 'hub' else 'Nous écrire' if page['kind'] == 'contact' else 'Parlons de votre projet'
    return f'''<section class="subpage-hero" aria-labelledby="page-title">
      <div class="container">
        <nav class="breadcrumbs" aria-label="Fil d’Ariane">{crumbs}</nav>
        <div class="subpage-hero-grid"><div class="subpage-hero-copy">
          <p class="section-kicker">{e(page['group'])} · Saint-Malo &amp; Grand Ouest</p>
          <h1 id="page-title">{e(title)}</h1><p class="subpage-lead">{e(page['subtitle'])}</p>
          <a class="button" href="{cta}">{ARROW} {label}</a>
          {'<p class="rental-meta">Tarifs TTC à la journée · Disponibilité sur demande</p>' if equipment else ''}
        </div><div class="subpage-hero-picture"><img src="{e(page['hero_image'])}" alt="{e(title)} — prestation Fix-Events" width="1200" height="900"><span class="photo-badge">FIX-e <span>Son. Musique. Lumière.</span></span></div></div>
      </div>
    </section>'''


def conditions(items):
    cards = ''.join(f'<article class="rental-condition"><span class="condition-number">0{i + 1}</span><h3>{e(item["title"])}</h3><p>{e(item["text"])}</p></article>' for i, item in enumerate(items))
    return f'<section class="rental-section container"><p class="section-kicker">Une location en toute sérénité</p><h2 class="section-title">Comment ça se passe ?</h2><div class="rental-grid">{cards}</div></section>'


def catalog(page):
    products = page['products']
    types = sorted({item['type'] for item in products})
    options = ''.join(f'<option value="{e(kind)}">{e(kind.capitalize())}</option>' for kind in types)
    cards = []
    for item in products:
        search = ' '.join([item['type'], item['name'], *item['specs'], item['description']])
        detail = ''.join(f'<li>{e(line)}</li>' for line in item['specs'])
        inquiry = quote(f"{page['title']} — {item['name']} ({item['price']})", safe='')
        cards.append(f'''<article class="product-card" data-type="{e(item['type'])}" data-price="{item['amount']}" data-search="{e(search)}">
          <div class="product-image"><img src="{e(item['image'])}" alt="{e(item['name'])}" loading="lazy" width="750" height="750"></div>
          <div class="product-body"><p class="product-type">{e(item['type'])}</p><h3>{e(item['name'])}</h3>
          <ul class="product-specs">{detail}</ul>{'<p class="product-description">' + e(item['description']) + '</p>' if item['description'] else ''}
          <div class="product-bottom"><p class="product-price">{e(item['price'])}</p><a class="quote-link" href="nous-contacter-faq.html?materiel={inquiry}#contact">Demander un devis {ARROW}</a></div></div>
        </article>''')
    return category_nav(page['slug']) + f'''<section class="catalog-section container" id="catalogue" data-catalog aria-labelledby="catalog-title">
      <div class="catalog-heading"><div><p class="section-kicker">Le matériel adapté à votre projet</p><h2 class="section-title" id="catalog-title">Notre sélection</h2></div><p class="catalog-count" role="status" aria-live="polite">{len(products)} références</p></div>
      <form class="catalog-toolbar" role="search" onsubmit="return false">
        <label class="catalog-search"><span class="visually-hidden">Rechercher un matériel</span><input type="search" name="recherche" placeholder="Rechercher une référence, une marque…" maxlength="150" autocomplete="off"></label>
        <label><span class="visually-hidden">Type de matériel</span><select name="categorie"><option value="">Tous les types</option>{options}</select></label>
        <label><span class="visually-hidden">Trier les références</span><select name="tri"><option value="selection">Notre sélection</option><option value="prix-asc">Prix croissant</option><option value="prix-desc">Prix décroissant</option></select></label>
      </form><div class="product-grid">{''.join(cards)}</div>
      <div class="catalog-empty" hidden><h3>Aucune référence trouvée</h3><p>Essayez un autre nom ou réinitialisez les filtres.</p><button type="button" class="button catalog-reset">Réinitialiser les filtres</button></div>
      <p class="catalog-footnote">Les tarifs et la disponibilité sont confirmés lors de votre demande de devis.</p>
    </section>''' + conditions(page['conditions'])


def photo_gallery(page):
    if not page['photos']:
        return '', ''
    slides = ''.join(f'<button class="gallery-slide" data-image="{e(image)}" aria-label="Agrandir la photo {i + 1} — {e(page["title"])}"><img src="{e(image)}" alt="{e(page["title"])} — réalisation Fix-Events {i + 1}" loading="lazy" width="750" height="750"></button>' for i, image in enumerate(page['photos']))
    return '<section class="gallery-section secondary-gallery" aria-label="Nos réalisations en images"><div class="gallery-track">' + slides + '</div><div class="gallery-controls"><button class="gallery-prev" aria-label="Photo précédente">‹</button><button class="gallery-next" aria-label="Photo suivante">›</button></div></section>', LIGHTBOX


def service(page):
    markup = ''
    if page['intro']:
        markup += '<section class="service-intro container"><p class="section-kicker">Votre événement, notre engagement</p>' + ''.join('<p>' + e(text) + '</p>' for text in page['intro']) + '</section>'
    for block in page['sections']:
        cards = []
        notes = list(block['paragraphs'])
        for card in block['cards']:
            if not card['text']:
                notes.append(card['title'])
                continue
            icon = f'<img class="service-icon" src="{e(card["icon"])}" alt="" width="42" height="42" loading="lazy">' if card['icon'] else '<span class="service-mark" aria-hidden="true">↗</span>'
            cards.append(f'<article class="service-feature">{icon}<h3>{e(card["title"])}</h3><p>{e(card["text"])}</p></article>')
        if cards or notes:
            markup += '<section class="service-section container">'
            if block['title']:
                markup += '<h2 class="section-title service-section-title">' + e(block['title']) + '</h2>'
            if cards:
                markup += f'<div class="service-grid{ " two-column" if len(cards) == 2 else ""}">' + ''.join(cards) + '</div>'
            for note in dict.fromkeys(notes):
                markup += '<div class="service-note"><p>' + e(note) + '</p></div>'
            markup += '</section>'
    gallery, dialog = photo_gallery(page)
    return markup + gallery, dialog


def project_cta():
    return f'<section class="project-cta container"><div><p class="section-kicker">Concevons la suite ensemble</p><h2>Un projet en tête ?<br><span>Faisons-le vivre.</span></h2><p>Parlez-nous de votre lieu, de votre date et de vos envies.</p></div><a class="button" href="nous-contacter-faq.html#contact">{ARROW} Demander un devis</a></section>'


def related(page):
    selection = [p for p in PAGES if p['group'] == page['group'] and p['slug'] != page['slug'] and p['kind'] != 'contact'][:3]
    if not selection:
        return ''
    return '<section class="related-section container"><p class="section-kicker">À découvrir aussi</p><div class="related-links">' + ''.join(f'<a href="{e(p["slug"])}.html">{e(p["title"])} {ARROW}</a>' for p in selection) + '</div></section>'


def document(page, content, dialogs=''):
    slug, title = page['slug'], page['title']
    header = HEADER.replace(f'href="{slug}.html"', f'href="{slug}.html" aria-current="page"')
    return f'''<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{e(page['subtitle'][:180])}"><meta name="theme-color" content="#101310"><title>{e(title)} — Fix-Events</title>
<link rel="icon" href="assets/logo-icon.png"><link rel="stylesheet" href="styles.css"><script src="script.js" defer></script></head>
<body class="secondary-page"><div class="scroll-progress" aria-hidden="true"></div><a class="skip-link" href="#main">Aller au contenu</a>{header}
<main id="main">{hero(page)}{content}</main>{FOOTER}
<a class="back-to-top" href="#page-title" aria-label="Retour en haut de la page" tabindex="-1"><span aria-hidden="true">↑</span></a>{dialogs}</body></html>
'''


for page in PAGES:
    dialogs = ''
    if page['kind'] == 'catalogue':
        content = catalog(page) + project_cta() + related(page)
    elif page['kind'] == 'contact':
        intro = '<div class="contact-options container"><a href="tel:0664728321"><span>Par téléphone</span><strong>06.64.72.83.21</strong></a><div><span>Notre secteur</span><strong>Saint-Malo &amp; Grand Ouest</strong></div></div>'
        questions = BY_SLUG['eclairages']['conditions']
        faq = '<section class="faq-section container"><p class="section-kicker">Location de matériel</p><h2 class="section-title">Quelques repères avant de réserver</h2><div class="faq-list">' + ''.join(f'<details class="faq-item"><summary>{e(q["title"])}</summary><p>{e(q["text"])}</p></details>' for q in questions) + '</div></section>'
        content = intro + CONTACT_FORM + faq
        dialogs = CONTACT_DIALOG
    else:
        content, dialogs = service(page)
        content += project_cta() + related(page)
    (SOURCES / (page['slug'] + '.html')).write_text(document(page, content, dialogs))


hub = {'slug': 'materiel', 'title': 'Location de matériel', 'group': 'Le catalogue Fix-Events', 'kind': 'hub', 'subtitle': 'Du premier discours à la dernière danse : trouvez le son, la lumière et les équipements qui donnent vie à votre événement.', 'hero_image': BY_SLUG['eclairages']['hero_image']}
photos = ['assets/quality.jpeg', 'assets/flexibility.jpeg', 'assets/video-poster.jpeg', 'assets/event-3.jpeg', 'assets/expertise.jpeg']
cards = []
for slug, photo in zip(CATEGORIES, photos):
    page = BY_SLUG[slug]
    cards.append(f'<a class="category-card" href="{slug}.html"><img src="{photo}" alt="{e(page["title"])}" width="750" height="750" loading="lazy"><div><p class="section-kicker">{len(page["products"])} références</p><h3>{e(page["title"])}</h3><span>Explorer la sélection {ARROW}</span></div></a>')
content = category_nav('materiel') + '<section class="category-section container" id="categories"><p class="section-kicker">Tout pour votre événement</p><h2 class="section-title">Choisissez votre univers</h2><div class="category-grid">' + ''.join(cards) + '</div></section>' + conditions(BY_SLUG['eclairages']['conditions']) + project_cta()
(SOURCES / 'materiel.html').write_text(document(hub, content))

# Homepage links now use the generated local pages. Keep the external contact
# submission URL in its review dialog: the static site has no mail backend.
start, end = HOME.index('<main'), HOME.index('</main>') + len('</main>')
new_home = HOME[:start] + local_links(HOME[start:end]) + HOME[end:]
new_home = new_home[:new_home.index('<header')] + HEADER.replace('href="index.html#accueil"', 'href="#accueil"') + new_home[new_home.index('</header>') + len('</header>'):]
new_home = new_home.replace('<a class="button" href="pack-son-lights.html"><span aria-hidden="true">»</span> Louer notre matériel</a>', '<a class="button" href="materiel.html"><span aria-hidden="true">»</span> Louer notre matériel</a>')
(ROOT / 'page.html').write_text(new_home)
print(f'Generated {len(PAGES) + 1} secondary page templates; updated homepage links.')
