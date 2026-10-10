"""Generate local pages and the shared catalogue using the standard library."""
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
SHARED = (ROOT / 'components.html').read_text()


def e(value):
    return escape(str(value), quote=True)


HEADER = re.search(r'<header\b.*?</header>', HOME, re.S).group(0).replace('href="#accueil"', 'href="index.html#accueil"')
FOOTER = re.search(r'<footer\b.*?</footer>', HOME, re.S).group(0).replace('href="#accueil"', 'href="index.html#accueil"')
CONTACT_FORM = re.search(r'<section class="contact-section.*?</section>', HOME, re.S).group(0)
LIGHTBOX = re.search(r'<dialog class="lightbox.*?</dialog>', HOME, re.S).group(0)
ARROW = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14m-6-6 6 6-6 6"/></svg>'


def contact_url(page=None):
    if not page or page['kind'] in ('catalogue', 'hub'):
        return 'nous-contacter-faq.html?type=location#contact'
    return 'nous-contacter-faq.html?prestation=' + quote(page['title'], safe='') + '#contact'


def category_nav(active=None):
    links = [('materiel', 'Tout le matériel')] + [(slug, BY_SLUG[slug]['title']) for slug in CATEGORIES]
    return '<div class="category-navigation"><nav class="category-nav" aria-label="Catégories de matériel">' + ''.join(f'<a href="{slug}.html"' + (' aria-current="page"' if slug == active else '') + f'>{e(title)}</a>' for slug, title in links) + '</nav><p class="category-scroll-hint" aria-hidden="true">Faites défiler les catégories →</p></div>'


def hero(page):
    slug, title = page['slug'], page['title']
    equipment = page['kind'] in ('catalogue', 'hub')
    crumbs = '<a href="index.html">Accueil</a><span aria-hidden="true">/</span>'
    if equipment and slug != 'materiel':
        crumbs += '<a href="materiel.html">Matériel</a><span aria-hidden="true">/</span>'
    elif page['kind'] == 'service':
        crumbs += '<a href="prestations.html">Prestations</a><span aria-hidden="true">/</span>'
    crumbs += f'<span aria-current="page">{e(title)}</span>'
    cta = '#catalogue' if page['kind'] == 'catalogue' else '#categories' if page['kind'] == 'hub' else '#contact' if page['kind'] == 'contact' else '#prestations' if page['kind'] == 'services-hub' else contact_url(page)
    label = 'Voir le catalogue' if page['kind'] == 'catalogue' else 'Choisir mon matériel' if page['kind'] == 'hub' else 'Préparer ma demande' if page['kind'] == 'contact' else 'Découvrir les prestations' if page['kind'] == 'services-hub' else 'Demander un devis'
    return f'''<section class="subpage-hero" aria-labelledby="page-title"><div class="container">
      <nav class="breadcrumbs" aria-label="Fil d’Ariane">{crumbs}</nav>
      <div class="subpage-hero-grid"><div class="subpage-hero-copy">
      <p class="section-kicker">{e(page['group'])} · Saint-Malo &amp; Grand Ouest</p>
      <h1 id="page-title">{e(title)}</h1><p class="subpage-lead">{e(page['subtitle'])}</p>
      <div class="subpage-actions"><a class="button" href="{cta}">{label} {ARROW}</a><a class="text-link" href="tel:0664728321">Appeler</a></div>
      {'<p class="rental-meta">Tarifs TTC à la journée · Location sur demande, après confirmation</p>' if equipment else '<p class="rental-meta">Prestations et installation définies avec vous</p>' if page['kind'] == 'service' else ''}
      </div><div class="subpage-hero-picture"><img src="{e(page['hero_image'])}" alt="{e(title)} — Fix-Events" width="1200" height="900" fetchpriority="high"><span class="photo-badge">FIX-e <span>Son. Musique. Lumière.</span></span></div></div>
      </div></section>'''


def conditions(items):
    cards = ''.join(f'<article class="rental-condition"><h3>{e(item["title"])}</h3><p>{e(item["text"])}</p></article>' for item in items)
    return '<section class="rental-section container"><p class="section-kicker">Une location en toute sérénité</p><h2 class="section-title">Les repères avant de louer</h2><div class="rental-grid">' + cards + '</div></section>'


def workflow():
    cards = ''.join(f'<article class="workflow-step"><span class="condition-number">0{i + 1}</span><h3>{e(item["title"])}</h3><p>{e(item["text"])}</p></article>' for i, item in enumerate(DATA['workflow']))
    return '<section class="workflow-section container"><p class="section-kicker">À vos côtés, étape par étape</p><h2 class="section-title">Du premier échange au jour J</h2><div class="workflow-grid">' + cards + '</div></section>'


def catalog(page):
    products = page['products']
    types = sorted({item['type'] for item in products})
    options = ''.join(f'<option value="{e(kind)}">{e(kind.capitalize())}</option>' for kind in types)
    needs = sorted({item['need'] for item in products}, key=lambda key: DATA['needs'][key])
    need_options = ''.join(f'<option value="{key}">{e(DATA["needs"][key])}</option>' for key in needs)
    cards = []
    for item in products:
        search = ' '.join([item['type'], item['name'], item['use'], *item['specs'], item['description'], *item['badges']])
        specs = ''.join(f'<li>{e(line)}</li>' for line in item['specs'])
        badges = ''.join(f'<span>{e(badge)}</span>' for badge in item['badges'])
        inquiry = quote(f"{page['title']} — {item['name']} ({item['price']})", safe='')
        cards.append(f'''<article class="product-card" data-id="{item['id']}" data-type="{e(item['type'])}" data-need="{item['need']}" data-price="{item['amount']}" data-search="{e(search)}">
          <button class="product-image product-zoom" type="button" data-image="{e(item['image'])}" data-name="{e(item['name'])}" aria-label="Agrandir la photo : {e(item['name'])}"><img src="{e(item['image'])}" alt="{e(item['name'])}" loading="lazy" decoding="async" width="750" height="750"><span aria-hidden="true">+</span></button>
          <div class="product-body"><p class="product-type">{e(item['type'])}</p><h3>{e(item['name'])}</h3><p class="product-use">{e(item['use'])}</p><div class="product-badges">{badges}</div>
          <details class="product-details"><summary>Caractéristiques &amp; éléments inclus</summary><ul class="product-specs">{specs}</ul>{'<p class="product-description">' + e(item['description']) + '</p>' if item['description'] else ''}</details>
          <div class="product-bottom"><p class="product-price"><strong>{item['amount']:g} €</strong><span>TTC / jour</span></p><button class="button product-add" type="button" data-add="{item['id']}">Ajouter à ma demande {ARROW}</button><a class="quote-link product-fallback" href="nous-contacter-faq.html?materiel={inquiry}#contact">Demander ce matériel {ARROW}</a></div></div></article>''')
    return category_nav(page['slug']) + f'''<section class="catalog-section container" id="catalogue" data-catalog aria-labelledby="catalog-title">
      <div class="catalog-heading"><div><p class="section-kicker">Le matériel adapté à votre projet</p><h2 class="section-title" id="catalog-title">Notre sélection</h2></div><p class="catalog-count" role="status" aria-live="polite">{len(products)} références</p></div>
      <p class="catalog-intro">Ajoutez les équipements à votre demande, puis précisez vos quantités, votre date et votre lieu. Vous ne réservez rien à cette étape.</p>
      <form class="catalog-toolbar" role="search">
        <label class="catalog-search"><span>Rechercher</span><input type="search" name="recherche" placeholder="Une référence, une marque, un usage…" maxlength="150" autocomplete="off"></label>
        <details class="catalog-filter-panel" open><summary>Filtrer et trier</summary><div class="catalog-filter-fields">
        <label><span>Votre besoin</span><select name="besoin"><option value="">Tous les usages</option>{need_options}</select></label>
        <label><span>Type de matériel</span><select name="categorie"><option value="">Tous les types</option>{options}</select></label>
        <label><span>Trier</span><select name="tri"><option value="selection">Notre sélection</option><option value="prix-asc">Prix croissant</option><option value="prix-desc">Prix décroissant</option></select></label></div></details>
        <div class="catalog-filter-status"><p class="active-filters" role="status"></p><button type="button" class="text-link catalog-reset">Effacer les filtres</button></div>
      </form><div class="product-grid">{''.join(cards)}</div>
      <div class="catalog-empty" hidden><h3>Aucune référence trouvée</h3><p>Essayez un autre usage ou effacez les filtres ci-dessus. Nous pouvons aussi vous conseiller.</p><a class="button button-secondary" href="{contact_url(page)}">Être conseillé</a></div>
      <p class="catalog-footnote">Prix indicatifs TTC à la journée. Disponibilité, accessoires, installation, transport et tarif final sont confirmés dans le devis. Les éléments fournis sont précisés dans chaque fiche.</p>
    </section>''' + conditions(page['conditions'])


def photo_gallery(page):
    photos = page.get('photos', [])
    if not photos:
        return '', ''
    slides = ''.join(f'<button class="gallery-slide" data-image="{e(image)}" aria-label="Agrandir la photo {i + 1} — {e(page["title"])}"><img src="{e(image)}" alt="{e(page["title"])} — photographie Fix-Events {i + 1}" loading="lazy" decoding="async" width="750" height="750"></button>' for i, image in enumerate(photos))
    return '<section class="realization-section container"><p class="section-kicker">Les prestations en images</p><h2 class="section-title">Sur le terrain</h2><p class="section-description">Quelques images de nos installations et de nos événements.</p></section><section class="gallery-section secondary-gallery" aria-label="Les prestations en images"><div class="gallery-track">' + slides + '</div><div class="gallery-controls"><button class="gallery-prev" aria-label="Photo précédente">‹</button><button class="gallery-next" aria-label="Photo suivante">›</button></div></section>', LIGHTBOX


def faq(items, title='Vos questions, avant de vous lancer'):
    return '<section class="faq-section container"><p class="section-kicker">Quelques réponses utiles</p><h2 class="section-title">' + e(title) + '</h2><div class="faq-list">' + ''.join(f'<details class="faq-item"><summary>{e(q["title"])}</summary><p>{e(q["text"])}</p></details>' for q in items) + '</div></section>'


def service(page):
    markup = ''
    intro = [text for text in page.get('intro', []) if text != page['subtitle']]
    if intro:
        markup += '<section class="service-intro container"><p class="section-kicker">Votre événement, notre engagement</p>' + ''.join('<p>' + e(text) + '</p>' for text in intro) + '</section>'
    for block in page.get('sections', []):
        cards = []
        notes = list(block['paragraphs'])
        seen_text = set()
        for card in block['cards']:
            if not card['text']:
                notes.append(card['title'])
                continue
            if card['text'] in seen_text:
                continue
            seen_text.add(card['text'])
            icon = f'<img class="service-icon" src="{e(card["icon"])}" alt="" width="42" height="42" loading="lazy">' if card['icon'] else '<span class="service-mark" aria-hidden="true">✦</span>'
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
    questions = [
        {'title':'Comment définir la prestation ?', 'text':'Indiquez votre date, le lieu, le nombre de participants et les moments à accompagner. Ces informations permettent de préparer une proposition adaptée.'},
        {'title':'Que comprend le devis ?', 'text':'Les prestations, équipements et conditions retenus sont précisés dans la proposition. Signalez vos besoins de livraison, d’installation et de présence technique.'},
        {'title':'Puis-je louer du matériel sans prestation ?', 'text':'Le catalogue de location présente les références et les tarifs indicatifs. La disponibilité doit être confirmée avant toute réservation.'},
    ]
    if page['slug'] == 'mariages':
        questions.insert(1, {'title':'Quels moments de la journée pouvez-vous accompagner ?', 'text':'La cérémonie, le cocktail, les discours du dîner et la soirée dansante peuvent être accompagnés selon la prestation convenue. Fix-Events n’organise pas de jeux ; une collaboration avec vos autres prestataires est possible.'})
    if page['slug'] in ('sonorisation-exterieure', 'le-concept-fix-e-self-powered-events'):
        questions.insert(1, {'title':'Et si le lieu n’a pas de prise électrique ?', 'text':'Des solutions sur batterie font partie du matériel Fix-Events. Leur autonomie et leur adéquation au projet doivent être étudiées selon la consommation, la durée et les conditions du lieu.'})
    if page['slug'] == 'bornes-photobooth':
        questions.insert(1, {'title':'À quoi sert la borne photo ?', 'text':'Elle permet à vos invités de réaliser des photos et de garder un souvenir grâce à l’impression instantanée. Les modalités de la prestation sont définies avec vous.'})
    return markup + gallery + workflow() + faq(questions), dialog


def project_cta(page=None):
    return f'<section class="project-cta container"><div><p class="section-kicker">Concevons la suite ensemble</p><h2>Un projet en tête ?<br><span>Faisons-le vivre.</span></h2><p>Votre date, votre lieu et vos envies : commençons par en parler.</p></div><div class="cta-actions"><a class="button" href="{contact_url(page)}">Demander un devis {ARROW}</a><a class="text-link" href="tel:0664728321">Ou appelez-nous</a></div></section>'


def related(page):
    complements = {
        'mariages':['bornes-photobooth','eclairage-evenementiel','bar-a-vinyles'],
        'anniversaires':['effets-sceniques','bornes-photobooth','eclairage-evenementiel'],
        'seminaire':['sonorisation-evenementielle','projection-video','regie-son-lumiere'],
        'clients-collaborateurs':['bar-a-vinyles','bornes-photobooth','projection-video'],
        'lancement-de-produit':['effets-sceniques','projection-video','eclairage-evenementiel'],
        'galas-etudiants':['regie-son-lumiere','effets-sceniques','structures-podium'],
    }
    slugs = complements.get(page['slug'], [slug for slug in (CATEGORIES if page['kind'] == 'catalogue' else ['sonorisation-evenementielle','eclairage-evenementiel','bornes-photobooth']) if slug != page['slug']][:3])
    return '<section class="related-section container"><p class="section-kicker">Pour compléter votre projet</p><div class="related-links">' + ''.join(f'<a href="{slug}.html">{e(BY_SLUG[slug]["title"])} {ARROW}</a>' for slug in slugs) + '</div></section>'


def document(page, content, dialogs=''):
    slug, title = page['slug'], page['title']
    header = HEADER.replace(f'href="{slug}.html"', f'href="{slug}.html" aria-current="page"')
    if page['kind'] in ('service', 'catalogue', 'hub'):
        header = header.replace('href="nous-contacter-faq.html#contact"', f'href="{contact_url(page)}"')
    if page['kind'] in ('catalogue', 'hub'):
        header = header.replace('<summary>Location', '<summary class="nav-active">Location')
    elif page.get('group') in ('Particuliers','Professionnels'):
        header = header.replace('<summary>Vos événements', '<summary class="nav-active">Vos événements')
    elif page['kind'] in ('service', 'services-hub') and slug != 'le-concept-fix-e-self-powered-events':
        header = header.replace('<summary>Prestations', '<summary class="nav-active">Prestations')
    html = f'''<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{e(page['subtitle'][:180])}"><meta name="theme-color" content="#101310"><title>{e(title)} — Fix-Events</title>
<link rel="icon" href="assets/logo-icon.png"><link rel="stylesheet" href="styles.css"><script src="catalog-data.js" defer></script><script src="script.js" defer></script></head>
<body class="secondary-page {page['kind']}-page" data-page="{slug}" data-kind="{page['kind']}"><div class="scroll-progress" aria-hidden="true"></div><a class="skip-link" href="#main">Aller au contenu</a>{header}
<main id="main">{hero(page)}{content}</main>{FOOTER}<a class="back-to-top" href="#page-title" aria-label="Retour en haut de la page" tabindex="-1"><span aria-hidden="true">↑</span></a>{dialogs}{SHARED}</body></html>'''
    return '\n'.join(line.rstrip() for line in html.splitlines()) + '\n'


for page in PAGES:
    dialogs = ''
    if page['kind'] == 'catalogue':
        content = catalog(page) + project_cta(page) + related(page)
    elif page['kind'] == 'contact':
        intro = '<div class="contact-options container"><a href="tel:0664728321"><span>Par téléphone</span><strong>06.64.72.83.21</strong></a><div><span>Notre secteur</span><strong>Saint-Malo &amp; Grand Ouest</strong></div></div>'
        content = intro + CONTACT_FORM + faq(BY_SLUG['eclairages']['conditions'], 'Vos questions sur la location')
    else:
        content, dialogs = service(page)
        content += project_cta(page) + related(page)
    (SOURCES / (page['slug'] + '.html')).write_text(document(page, content, dialogs))


hub = {'slug':'materiel','title':'Location de matériel','group':'Louer sans prestation','kind':'hub','subtitle':'Choisissez vos équipements, composez votre demande et précisez vos besoins. Nous confirmons ensemble la disponibilité et le devis.','hero_image':'assets/quality.jpeg'}
cards = []
for slug in CATEGORIES:
    page = BY_SLUG[slug]
    cards.append(f'<a class="category-card" href="{slug}.html"><img src="{page["hero_image"]}" alt="{e(page["title"])}" width="750" height="750" loading="lazy"><div><p class="section-kicker">{len(page["products"])} références</p><h3>{e(page["title"])}</h3><span>Voir le catalogue {ARROW}</span></div></a>')
content = category_nav('materiel') + '<section class="category-section container" id="categories"><p class="section-kicker">Tout pour votre événement</p><h2 class="section-title">Choisissez votre univers</h2><div class="category-grid">' + ''.join(cards) + '</div></section><aside class="help-panel container"><div><h2>Vous préférez être accompagné ?</h2><p>Découvrez nos prestations avec une installation et un accompagnement définis pour votre projet.</p></div><a class="button button-secondary" href="prestations.html">Voir les prestations</a></aside>' + conditions(BY_SLUG['eclairages']['conditions']) + project_cta(hub)
(SOURCES / 'materiel.html').write_text(document(hub, content))

services_hub = {'slug':'prestations','title':'Votre événement, notre savoir-faire','group':'Être accompagné','kind':'services-hub','subtitle':'Son, musique, lumière et vidéo : découvrez les prestations à combiner pour votre événement.','hero_image':'assets/video-poster.jpeg'}
slugs = ['sonorisation-evenementielle','eclairage-evenementiel','bar-a-vinyles','bornes-photobooth','effets-sceniques','projection-video','regie-son-lumiere','sonorisation-exterieure','structures-podium']
cards = '<a class="category-card" href="index.html#equipe"><img src="assets/cyril.jpg" alt="Cyril derrière ses platines" loading="lazy" width="800" height="800"><div><h3>DJ &amp; musiciens</h3><span>Rencontrer notre équipe ' + ARROW + '</span></div></a>'
cards += ''.join(f'<a class="category-card" href="{slug}.html"><img src="{BY_SLUG[slug]["hero_image"]}" alt="{e(BY_SLUG[slug]["title"])}" loading="lazy" width="750" height="750"><div><h3>{e(BY_SLUG[slug]["title"])}</h3><span>Découvrir la prestation {ARROW}</span></div></a>' for slug in slugs)
content = '<section class="category-section container" id="prestations"><p class="section-kicker">Une prestation à votre mesure</p><h2 class="section-title">Composez votre événement</h2><div class="category-grid">' + cards + '</div></section>' + workflow() + project_cta(services_hub) + '<aside class="help-panel container"><div><h2>Vous cherchez uniquement du matériel ?</h2><p>Consultez les équipements et préparez une demande de location.</p></div><a class="button button-secondary" href="materiel.html">Voir le catalogue</a></aside>'
(SOURCES / 'prestations.html').write_text(document(services_hub, content))

manifest = {}
for page in PAGES:
    for item in page.get('products', []):
        manifest[item['id']] = {key:item[key] for key in ('name','amount','image','use')}
        manifest[item['id']].update(category=page['title'], slug=page['slug'])
(ROOT / 'catalog-data.js').write_text('"use strict";\nwindow.FIX_CATALOG = ' + json.dumps(manifest,ensure_ascii=False,separators=(',',':')).replace('</','<\\/') + ';\n')

# Refresh only the marked shared UI and workflow sections in the home source.
HOME = re.sub(r'<!-- shared-ui:start -->.*?<!-- shared-ui:end -->', '<!-- shared-ui:start -->\n' + SHARED + '\n<!-- shared-ui:end -->', HOME, flags=re.S)
HOME = re.sub(r'<!-- workflow:start -->.*?<!-- workflow:end -->', '<!-- workflow:start -->' + workflow() + '<!-- workflow:end -->', HOME, flags=re.S)
(ROOT / 'page.html').write_text(HOME)
print(f'Generated {len(PAGES) + 2} secondary pages and {len(manifest)} catalogue references.')
