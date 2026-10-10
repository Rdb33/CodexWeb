# Fix-Events homepage recreation

A responsive, static recreation of https://www.fix-events.fr/ using plain HTML, CSS and JavaScript. Original photography and logos are stored in `assets/`, alongside locally hosted Rubik and Lato fonts.

## Run locally

From `/workspace/CodexWeb`:

```sh
python3 -m http.server 8000 --bind 0.0.0.0
```

No package installation is needed. `index.html` is bundled for ChatGPT's HTML preview: styles, scripts, fonts and optimized images are embedded so it displays without sibling files.

Edit `page.html`, `styles.css` and `script.js`, then refresh the preview file using the standard Python library:

```sh
python3 build-preview.py
```

`assets/preview/` contains optimized copies of the original photos for bundling. Keep these retained files with the source assets.

## Behavior and scope

- Responsive navigation with the original service links, telephone link and section anchors.
- Scrollable event gallery with previous/next controls and an accessible photo dialog.
- Original promotional video, compressed to 720p and served locally on demand. In a standalone HTML preview, playback streams the original site's video instead.
- Original team and social links.
- Contact form with browser validation and a review/copy dialog. Actual submission is completed on the original contact page; no email or form backend is configured here.

This recreates the homepage. Links to other service pages open their corresponding pages on the original website. Images and branding originate from Fix-Events. Fonts originate from the Google Fonts repository and are licensed under the SIL Open Font License (see `assets/OFL-*.txt`).
