# Fix-Events

Site en HTML, CSS et JavaScript : accueil et 26 pages locales, dans le style sombre et vert de Fix-Events. Les photos, produits, logos et spécifications d’origine sont conservés sous `assets/` et dans `site-data.json`.

## Démarrer

À la racine du dépôt :

```sh
python3 -m http.server 8000 --bind 0.0.0.0
```

Aucune installation de dépendances n’est nécessaire. Les pages à la racine utilisent des images optimisées et des ressources partagées (`site.css`, `script.js`, `catalog-data.js`) que le navigateur peut réutiliser entre les pages. Les noms des ressources CSS et JavaScript incluent une empreinte dans leur URL pour actualiser le cache après une reconstruction.

## Modifier et reconstruire

- `page.html` : source de l’accueil, navigation, pied de page et formulaire commun.
- `styles.css` : styles et adaptation mobile.
- `script.js` : navigation, galerie, sélection et filtres.
- `components.html` : sélection de matériel, agrandissement des produits et barre mobile.
- `site-data.json` : contenus, photos, 54 références, tarifs indicatifs, descriptions d’usage et caractéristiques.
- `build-pages.py` : génère les modèles sous `pages/` et le catalogue partagé.
- `build-preview.py` : génère les pages finales et la feuille optimisée `site.css`.

```sh
python3 build-preview.py
```

Le build utilise uniquement la bibliothèque standard Python et les images déjà présentes. Il ne télécharge rien. Modifier les sources plutôt que les HTML générés, `site.css` ou `catalog-data.js`.

Pour des HTML indépendants avec les styles, scripts, polices et images intégrés :

```sh
python3 build-preview.py --standalone
```

Ils sont écrits sous `previews/`, ignoré par Git. La navigation entre ces aperçus utilise les autres pages du même dossier. La vidéo utilise le fichier local du dépôt quand le dossier est servi ; une copie HTML isolée utilise la vidéo du site d’origine. Le site principal utilise la vidéo locale, chargée seulement à la lecture.

## Parcours et interactions

- Deux parcours : prestations accompagnées (`prestations.html`) et location seule (`materiel.html`). Les liens de l’accueil vers la sonorisation et l’éclairage conduisent aux prestations correspondantes.
- Navigation avec rubrique active, fil d’Ariane, liens complémentaires selon l’événement, accès au devis et appel téléphonique.
- Cinq catalogues avec recherche, filtre par besoin, type technique, tri par prix et réinitialisation. Les filtres sont mémorisés pour la session et inscrits dans l’URL.
- Les 54 références présentent un usage compréhensible, des caractéristiques dépliables, les éléments inclus quand ils sont indiqués dans la source, un tarif TTC journalier et une photo agrandissable.
- Sélection multi-produits avec quantités de 1 à 99, retrait, montant journalier indicatif et récapitulatif dans le formulaire. Elle est conservée dans le stockage local du navigateur. Seuls les identifiants du matériel et les quantités sont mémorisés, sans coordonnées personnelles. Le lien vers la demande transporte aussi la sélection pour les navigateurs qui bloquent le stockage.
- Le montant indicatif ne réserve aucun matériel. Disponibilité, durée, accessoires, transport, installation et tarif final restent à confirmer par Fix-Events.
- Formulaire visuel avec intitulés permanents, type de demande, événement, date, lieu, participants et durée. Les liens des prestations préremplissent le contexte.
- **À la demande du propriétaire, le bouton « Envoyer ma demande » reste désactivé. Aucun formulaire ne transmet de données et aucun service de messagerie n’est configuré.** Il sera raccordé ultérieurement. L’appel téléphonique reste disponible.
- Barre mobile donnant accès à l’appel et à la sélection ou au devis ; filtres accessibles pendant la consultation ; zones tactiles d’au moins 44 px pour les principales commandes.
- Animations courtes et apparitions jouées une seule fois. Les cartes informatives ne se déplacent plus au survol. La préférence de réduction des animations est respectée.
- Photos contextualisées, déroulement de l’accompagnement et FAQ. Liens vers les avis Google et Mariages.net ; aucune note ni citation client n’est inventée.

Les aperçus indépendants sont plus volumineux que les pages du site, car ils embarquent leurs ressources. Préférer les pages finales et leurs fichiers partagés pour un hébergement public. Le dépôt peut être servi par tout hébergement statique en conservant `assets/`, `site.css`, `script.js` et `catalog-data.js` à côté des HTML.

## Sources

Photos, produits et identité visuelle : Fix-Events. Les URLs originales sont conservées dans `site-data.json`. Les descriptions d’usage et l’organisation des parcours ont été ajoutées pour guider les visiteurs, sans garantir de capacité ou de disponibilité supplémentaire. Les polices Rubik et Lato sont fournies localement et utilisent la licence SIL Open Font License (`assets/OFL-*.txt`).
