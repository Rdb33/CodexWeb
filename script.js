'use strict';
document.documentElement.classList.add('interactive');
const header = document.querySelector('.site-header');
const navigation = document.querySelector('#navigation');
const menuToggle = document.querySelector('.menu-toggle');
const dropdowns = [...document.querySelectorAll('.dropdown')];
const backToTop = document.querySelector('.back-to-top');
const dock = document.querySelector('.mobile-dock');
const motionPreference = window.matchMedia('(prefers-reduced-motion: reduce)');
const mobilePreference = window.matchMedia('(max-width: 700px)');
const equipmentPage = ['catalogue', 'hub'].includes(document.body.dataset.kind);
if (dock && document.body.dataset.kind === 'service') {
  const params = new URLSearchParams({ prestation: document.querySelector('h1').textContent });
  dock.querySelector('.dock-quote').href = `nous-contacter-faq.html?${params}#contact`;
}
const announcement = document.querySelector('.interaction-status');
const catalogData = window.FIX_CATALOG || {};
const selectionKey = 'fix-events.selection.v1';
let selection = {};
let storageAvailable = true;
let announceTimer;
const money = value => new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR', maximumFractionDigits: 2 }).format(value);
function announce(message) {
  if (!announcement) return;
  announcement.textContent = '';
  clearTimeout(announceTimer);
  announceTimer = setTimeout(() => { announcement.textContent = message; }, 30);
}
function readStore(store, key) {
  try { return JSON.parse(store.getItem(key)); } catch { return null; }
}
function sanitizeSelection(value) {
  const result = {};
  if (!value || typeof value !== 'object' || Array.isArray(value)) return result;
  Object.entries(value).slice(0, 60).forEach(([id, qty]) => {
    if (Object.hasOwn(catalogData, id) && Number.isInteger(qty) && qty >= 1 && qty <= 99) result[id] = qty;
  });
  return result;
}
try {
  selection = sanitizeSelection(readStore(localStorage, selectionKey));
  localStorage.setItem(selectionKey, JSON.stringify(selection));
} catch { storageAvailable = false; }
function selectionEntries() { return Object.entries(selection).filter(([id]) => Object.hasOwn(catalogData, id)); }
function selectionTotal() { return selectionEntries().reduce((total, [id, qty]) => total + catalogData[id].amount * qty, 0); }
function requestUrl() {
  const query = new URLSearchParams({ type: 'location' });
  if (selectionEntries().length) query.set('selection', selectionEntries().map(([id, qty]) => `${id}:${qty}`).join(','));
  return `nous-contacter-faq.html?${query}#contact`;
}
function saveSelection() {
  try { localStorage.setItem(selectionKey, JSON.stringify(selection)); }
  catch { storageAvailable = false; }
  updateSelection();
}

function closeMenu(returnFocus = false) {
  const wasOpen = menuToggle.getAttribute('aria-expanded') === 'true';
  navigation.classList.remove('is-open');
  document.body.classList.remove('menu-open');
  menuToggle.setAttribute('aria-expanded', 'false');
  menuToggle.setAttribute('aria-label', 'Ouvrir le menu');
  const opened = dropdowns.find(menu => menu.open);
  dropdowns.forEach(menu => { menu.open = false; });
  if (returnFocus && wasOpen) menuToggle.focus();
  else if (returnFocus && opened) opened.querySelector('summary').focus();
}
function updateHeader() {
  header.classList.toggle('scrolled', window.scrollY > 35);
  const height = document.documentElement.scrollHeight - window.innerHeight;
  document.documentElement.style.setProperty('--scroll-progress', height > 0 ? Math.min(1, Math.max(0, window.scrollY / height)) : 0);
  const showBackToTop = window.scrollY > 600;
  backToTop.classList.toggle('is-visible', showBackToTop);
  backToTop.tabIndex = showBackToTop ? 0 : -1;
  if (dock) {
    const showDock = equipmentPage || selectionEntries().length > 0 || window.scrollY > 400;
    dock.hidden = !showDock;
    document.body.classList.toggle('has-dock', showDock);
  }
}
let scrollFrame = null;
window.addEventListener('scroll', () => {
  if (scrollFrame !== null) return;
  scrollFrame = requestAnimationFrame(() => { updateHeader(); scrollFrame = null; });
}, { passive: true });
window.addEventListener('resize', updateHeader, { passive: true });
menuToggle.addEventListener('click', () => {
  const open = menuToggle.getAttribute('aria-expanded') !== 'true';
  menuToggle.setAttribute('aria-expanded', String(open));
  menuToggle.setAttribute('aria-label', open ? 'Fermer le menu' : 'Ouvrir le menu');
  navigation.classList.toggle('is-open', open);
  document.body.classList.toggle('menu-open', open);
});
dropdowns.forEach(menu => menu.addEventListener('toggle', () => {
  if (menu.open) dropdowns.forEach(other => { if (other !== menu) other.open = false; });
}));
document.addEventListener('click', event => { if (!header.contains(event.target)) closeMenu(); });
header.addEventListener('focusout', () => setTimeout(() => {
  if (!header.contains(document.activeElement)) closeMenu();
}, 0));
navigation.querySelectorAll('a').forEach(link => link.addEventListener('click', () => closeMenu()));
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && !document.querySelector('dialog[open]')) closeMenu(true);
});
window.matchMedia('(min-width: 1101px)').addEventListener('change', () => closeMenu());

const videoFeature = document.querySelector('.video-feature');
if (videoFeature) {
  const video = videoFeature.querySelector('video');
  const videoError = videoFeature.querySelector('.video-error');
  videoFeature.querySelector('.video-cover').addEventListener('click', async () => {
    videoFeature.classList.add('playing');
    video.focus();
    if (/^https?:$/.test(location.protocol) && location.pathname.includes('/previews/')) {
      try {
        const local = new URL('../assets/presentation.mp4', location.href);
        const response = await fetch(local, { method: 'HEAD', signal: AbortSignal.timeout(2000) });
        if (response.ok && response.headers.get('content-type')?.includes('video/mp4')) video.src = local.href;
      } catch { /* An isolated preview retains its remote video source. */ }
    }
    video.play().catch(() => { /* Native controls remain available. */ });
  });
  video.addEventListener('error', () => { videoError.hidden = false; });
  video.querySelector('source')?.addEventListener('error', () => { videoError.hidden = false; });
}

function openDialog(dialog) {
  closeMenu();
  if (!dialog || dialog.open) return;
  dialog.showModal();
  document.body.classList.add('modal-open');
}
function dismissDialog(dialog) {
  if (dialog.animateClose) dialog.animateClose();
  else dialog.close();
}
document.querySelectorAll('dialog').forEach(dialog => {
  dialog.querySelector('.dialog-close')?.addEventListener('click', () => dismissDialog(dialog));
  dialog.addEventListener('close', () => {
    if (!document.querySelector('dialog[open]')) document.body.classList.remove('modal-open');
  });
  dialog.addEventListener('click', event => {
    if (event.target !== dialog) return;
    const box = dialog.getBoundingClientRect();
    if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) dismissDialog(dialog);
  });
});
const track = document.querySelector('.gallery-track');
const lightbox = document.querySelector('.lightbox');
if (track && lightbox) {
  const slides = [...track.querySelectorAll('.gallery-slide')];
  const scrollBehavior = () => motionPreference.matches ? 'instant' : 'smooth';
  function moveGallery(direction) {
    const distance = slides[0].getBoundingClientRect().width + parseFloat(getComputedStyle(track).gap);
    const end = track.scrollWidth - track.clientWidth;
    let target = track.scrollLeft + direction * distance;
    if (target > end + 5) target = 0;
    if (target < -5) target = end;
    track.scrollTo({ left: Math.max(0, target), behavior: scrollBehavior() });
  }
  document.querySelector('.gallery-prev')?.addEventListener('click', () => moveGallery(-1));
  document.querySelector('.gallery-next')?.addEventListener('click', () => moveGallery(1));
  const gallery = track.closest('[data-auto-gallery]');
  let galleryPosition = track.scrollLeft;
  let cycleWidth = 0;
  let lastFrame;
  let previewSource;
  let previewAnimation;
  let closing = false;
  const previewImage = lightbox.querySelector('img');
  const galleryCopies = [];
  if (gallery) {
    // Copies keep the loop seamless. They share the originals' preview handlers.
    for (let copy = 0; copy < 2; copy++) {
      slides.forEach((slide, index) => {
        const clone = slide.cloneNode(true);
        clone.tabIndex = -1;
        clone.setAttribute('aria-hidden', 'true');
        clone.dataset.galleryCopy = String(index);
        track.append(clone);
        galleryCopies.push(clone);
        clone.addEventListener('click', () => showPhoto(index, clone));
      });
    }
    function measureGallery() {
      cycleWidth = galleryCopies[0].getBoundingClientRect().left - slides[0].getBoundingClientRect().left;
      if (cycleWidth > 0) galleryPosition %= cycleWidth;
    }
    new ResizeObserver(measureGallery).observe(track);
    measureGallery();
    function glide(timestamp) {
      const elapsed = lastFrame === undefined ? 0 : Math.min(timestamp - lastFrame, 64);
      lastFrame = timestamp;
      if (!motionPreference.matches && !document.hidden && !document.querySelector('dialog[open]') && cycleWidth > 0) {
        // Keep a fractional position: integer scroll rounding must not stall slow motion.
        galleryPosition = (galleryPosition + elapsed * 0.024) % cycleWidth;
        track.scrollLeft = galleryPosition;
      }
      requestAnimationFrame(glide);
    }
    requestAnimationFrame(glide);
  }
  let photoIndex = 0;
  function updatePhoto() {
    const source = slides[photoIndex];
    lightbox.querySelector('img').src = source.dataset.image;
    lightbox.querySelector('img').alt = source.querySelector('img').alt;
  }
  function thumbnailTransform(source) {
    const thumb = source?.getBoundingClientRect();
    const full = lightbox.getBoundingClientRect();
    if (!thumb || !full.width || !full.height || thumb.right <= 0 || thumb.left >= window.innerWidth || thumb.bottom <= 0 || thumb.top >= window.innerHeight) return 'scale(0.96)';
    const x = thumb.left + thumb.width / 2 - full.left - full.width / 2;
    const y = thumb.top + thumb.height / 2 - full.top - full.height / 2;
    return `translate(${x}px, ${y}px) scale(${thumb.width / full.width}, ${thumb.height / full.height})`;
  }
  function animatePreview(frames, duration) {
    previewAnimation?.cancel();
    previewAnimation = lightbox.animate(frames, { duration, easing: 'cubic-bezier(.2,.7,.2,1)' });
    return previewAnimation.finished.catch(() => {});
  }
  function showPhoto(index, source) {
    photoIndex = index;
    previewSource = source;
    updatePhoto();
    openDialog(lightbox);
    if (!motionPreference.matches) {
      animatePreview([{ transform: thumbnailTransform(source), opacity: 0.35 }, { transform: 'none', opacity: 1 }], 300);
    }
  }
  lightbox.animateClose = async () => {
    if (closing || !lightbox.open) return;
    closing = true;
    if (!motionPreference.matches) {
      await animatePreview([{ transform: 'none', opacity: 1 }, { transform: thumbnailTransform(previewSource), opacity: 0.15 }], 240);
    }
    lightbox.close();
    if (gallery) track.scrollLeft = galleryPosition;
    closing = false;
  };
  lightbox.addEventListener('cancel', event => { event.preventDefault(); dismissDialog(lightbox); });
  slides.forEach((slide, index) => slide.addEventListener('click', () => showPhoto(index, slide)));
  function movePhoto(direction) {
    if (closing) return;
    previewAnimation?.cancel();
    photoIndex = (photoIndex + direction + slides.length) % slides.length;
    updatePhoto();
    const candidates = [slides[photoIndex], ...galleryCopies.filter(copy => Number(copy.dataset.galleryCopy) === photoIndex)];
    previewSource = candidates.find(slide => {
      const box = slide.getBoundingClientRect();
      return box.right > 0 && box.left < window.innerWidth;
    }) || slides[photoIndex];
    if (!motionPreference.matches) previewImage.animate([{ opacity: 0.4 }, { opacity: 1 }], { duration: 180 });
  }
  lightbox.querySelector('.lightbox-prev').addEventListener('click', () => movePhoto(-1));
  lightbox.querySelector('.lightbox-next').addEventListener('click', () => movePhoto(1));
  lightbox.addEventListener('keydown', event => {
    if (event.key === 'ArrowLeft') movePhoto(-1);
    if (event.key === 'ArrowRight') movePhoto(1);
  });
}
const photoDialog = document.querySelector('.product-photo-dialog');
document.querySelectorAll('.product-zoom').forEach(button => button.addEventListener('click', () => {
  photoDialog.querySelector('img').src = button.dataset.image;
  photoDialog.querySelector('img').alt = button.dataset.name;
  photoDialog.querySelector('p').textContent = button.dataset.name;
  openDialog(photoDialog);
}));

const selectionDialog = document.querySelector('.selection-dialog');
function node(tag, className, content) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (content !== undefined) element.textContent = content;
  return element;
}
function updateSelection() {
  const entries = selectionEntries();
  const units = entries.reduce((total, [, qty]) => total + qty, 0);
  document.querySelectorAll('.selection-count').forEach(element => { element.textContent = String(units); });
  document.querySelectorAll('.selection-float').forEach(element => { element.hidden = entries.length === 0; });
  if (dock) {
    dock.querySelector('.dock-selection').hidden = !equipmentPage && entries.length === 0;
    dock.querySelector('.dock-quote').hidden = equipmentPage || entries.length > 0;
  }
  document.querySelectorAll('[data-add]').forEach(button => {
    const qty = selection[button.dataset.add] || 0;
    button.classList.toggle('is-selected', qty > 0);
    button.textContent = qty ? `Ajouter encore · ${qty} dans ma demande` : 'Ajouter à ma demande →';
  });
  if (selectionDialog) {
    selectionDialog.querySelector('.selection-empty').hidden = entries.length > 0;
    selectionDialog.querySelector('.selection-summary').hidden = entries.length === 0;
    selectionDialog.querySelector('.selection-storage-note').hidden = storageAvailable;
    selectionDialog.querySelector('.selection-amount').textContent = money(selectionTotal());
    selectionDialog.querySelector('.selection-actions a').href = requestUrl();
    const list = selectionDialog.querySelector('.selection-items');
    const activeId = document.activeElement?.dataset.quantity;
    list.replaceChildren();
    entries.forEach(([id, qty]) => {
      const item = catalogData[id];
      const row = node('li', 'selection-item');
      const image = node('img'); image.src = item.image; image.alt = ''; image.width = 76; image.height = 76;
      const info = node('div', 'selection-item-info');
      info.append(node('p', 'product-type', item.category), node('h3', '', item.name), node('p', '', `${money(item.amount)} TTC / jour / unité`));
      const controls = node('div', 'selection-item-controls');
      const label = node('label', 'quantity-label');
      label.append(node('span', '', 'Quantité'));
      const input = node('input'); input.type = 'number'; input.min = '1'; input.max = '99'; input.step = '1'; input.value = qty; input.inputMode = 'numeric'; input.dataset.quantity = id;
      input.setAttribute('aria-label', `Quantité : ${item.name}`); label.append(input);
      const remove = node('button', 'selection-remove', 'Retirer'); remove.type = 'button'; remove.dataset.remove = id; remove.setAttribute('aria-label', `Retirer ${item.name}`);
      controls.append(label, remove);
      row.append(image, info, controls); list.append(row);
    });
    if (activeId) list.querySelector(`[data-quantity="${activeId}"]`)?.focus({ preventScroll: true });
  }
  renderContactSelection();
  updateHeader();
}
document.querySelectorAll('[data-open-selection]').forEach(button => button.addEventListener('click', () => {
  updateSelection(); openDialog(selectionDialog);
}));
document.querySelectorAll('[data-add]').forEach(button => button.addEventListener('click', () => {
  const id = button.dataset.add;
  if (!Object.hasOwn(catalogData, id)) return;
  if ((selection[id] || 0) >= 99) { announce('La quantité maximale est de 99 unités par référence.'); return; }
  selection[id] = (selection[id] || 0) + 1;
  saveSelection();
  announce(`${catalogData[id].name} ajouté. ${selection[id]} unité${selection[id] > 1 ? 's' : ''} dans votre demande.`);
}));
selectionDialog?.querySelector('.selection-continue').addEventListener('click', () => selectionDialog.close());
selectionDialog?.addEventListener('change', event => {
  const id = event.target.dataset.quantity;
  if (!id) return;
  const qty = Number(event.target.value);
  if (!Number.isInteger(qty) || qty < 1 || qty > 99) {
    event.target.value = selection[id]; announce('Choisissez une quantité comprise entre 1 et 99.'); return;
  }
  selection[id] = qty; saveSelection(); announce('La quantité et le montant indicatif ont été actualisés.');
});
selectionDialog?.addEventListener('click', event => {
  const button = event.target.closest('[data-remove]');
  if (!button) return;
  const id = button.dataset.remove;
  const name = catalogData[id]?.name;
  delete selection[id]; saveSelection();
  selectionDialog.querySelector('[data-remove]')?.focus({ preventScroll: true });
  if (!selectionEntries().length) selectionDialog.querySelector('.selection-empty a').focus();
  announce(`${name} retiré de votre demande.`);
});
window.addEventListener('storage', event => {
  if (event.key === selectionKey) { selection = sanitizeSelection(readStore(localStorage, selectionKey)); updateSelection(); }
});

const contactForm = document.querySelector('#contact-form');
function renderContactSelection() {
  if (!contactForm) return;
  const box = contactForm.querySelector('.contact-selection');
  const list = box.querySelector('.contact-selection-items');
  const entries = selectionEntries();
  box.hidden = entries.length === 0;
  list.replaceChildren();
  entries.forEach(([id, qty]) => list.append(node('li', '', `${qty} × ${catalogData[id].name} — ${money(catalogData[id].amount * qty)} TTC / jour`)));
  box.querySelector('.contact-selection-total').textContent = `Base indicative : ${money(selectionTotal())} TTC pour une journée, hors transport et installation. Le devis reste à confirmer.`;
}
if (contactForm) {
  const query = new URLSearchParams(location.search);
  const supplied = query.get('selection');
  if (supplied && supplied !== '1') {
    const parsed = {};
    supplied.slice(0, 4000).split(',').slice(0, 60).forEach(pair => { const [id, qty] = pair.split(':'); parsed[id] = Number(qty); });
    selection = sanitizeSelection(parsed);
  }
  if (query.get('type') === 'location' || supplied || query.has('materiel') || (selectionEntries().length && !query.has('prestation'))) contactForm.elements.type.value = 'location';
  const equipment = query.get('materiel');
  const service = query.get('prestation');
  if (equipment || service) contactForm.querySelector('.request-preparation').open = true;
  if (equipment) contactForm.elements.message.value = `Je souhaite des informations pour : ${equipment.slice(0, 500)}.`;
  if (service) {
    contactForm.elements.message.value = `Mon projet concerne : ${service.slice(0, 500)}.`;
    if (/mariage/i.test(service)) contactForm.elements.evenement.value = 'Mariage';
    else if (/anniversaire/i.test(service)) contactForm.elements.evenement.value = 'Anniversaire';
    else if (/séminaire|collaborateur|produit/i.test(service)) contactForm.elements.evenement.value = 'Événement professionnel';
  }
  // The owner requested a visual form only for now. No request is transmitted.
  contactForm.addEventListener('submit', event => { event.preventDefault(); });
}
updateSelection();

const catalog = document.querySelector('[data-catalog]');
if (catalog) {
  const cards = [...catalog.querySelectorAll('.product-card')];
  const grid = catalog.querySelector('.product-grid');
  const fields = ['recherche', 'besoin', 'categorie', 'tri'];
  const controls = Object.fromEntries(fields.map(name => [name, catalog.querySelector(`[name="${name}"]`)]));
  const count = catalog.querySelector('.catalog-count');
  const empty = catalog.querySelector('.catalog-empty');
  const status = catalog.querySelector('.active-filters');
  const reset = catalog.querySelector('.catalog-reset');
  const panel = catalog.querySelector('.catalog-filter-panel');
  const stateKey = `fix-events.filters.${document.body.dataset.page}`;
  const normalize = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  const originalOrder = new Map(cards.map((card, index) => [card, index]));
  panel.open = !mobilePreference.matches;
  let remembered;
  try { remembered = readStore(sessionStorage, stateKey); } catch { /* Filters can work without storage. */ }
  const query = new URLSearchParams(location.search);
  fields.forEach(name => {
    const value = query.has(name) ? query.get(name) : remembered?.[name];
    if (typeof value !== 'string') return;
    if (name === 'recherche') controls[name].value = value.slice(0, 150);
    else if ([...controls[name].options].some(option => option.value === value)) controls[name].value = value;
  });
  function refreshCatalog(persist = true) {
    const search = normalize(controls.recherche.value.trim());
    let visible = 0;
    cards.forEach(card => {
      const matches = normalize(card.dataset.search).includes(search) && (!controls.categorie.value || card.dataset.type === controls.categorie.value) && (!controls.besoin.value || card.dataset.need === controls.besoin.value);
      card.hidden = !matches;
      if (matches) visible++;
    });
    const order = [...cards].sort((a, b) => controls.tri.value === 'prix-asc' ? Number(a.dataset.price) - Number(b.dataset.price) : controls.tri.value === 'prix-desc' ? Number(b.dataset.price) - Number(a.dataset.price) : originalOrder.get(a) - originalOrder.get(b));
    order.forEach(card => grid.append(card));
    count.textContent = `${visible} référence${visible === 1 ? '' : 's'} sur ${cards.length}`;
    empty.hidden = visible > 0;
    const active = fields.filter(name => name !== 'tri' && controls[name].value);
    status.textContent = active.length ? `${active.length} filtre${active.length > 1 ? 's' : ''} actif${active.length > 1 ? 's' : ''}` : 'Toutes les références';
    reset.disabled = active.length === 0 && controls.tri.value === 'selection';
    if (!persist) return;
    const state = Object.fromEntries(fields.map(name => [name, controls[name].value]));
    try { sessionStorage.setItem(stateKey, JSON.stringify(state)); } catch { /* Optional persistence. */ }
    const params = new URLSearchParams(location.search);
    fields.forEach(name => {
      if (state[name] && !(name === 'tri' && state[name] === 'selection')) params.set(name, state[name]);
      else params.delete(name);
    });
    try { history.replaceState(null, '', `${location.pathname}${params.size ? '?' + params : ''}${location.hash}`); } catch { /* file:// preview */ }
  }
  let searchTimer;
  controls.recherche.addEventListener('input', () => { clearTimeout(searchTimer); searchTimer = setTimeout(refreshCatalog, 120); });
  fields.filter(name => name !== 'recherche').forEach(name => controls[name].addEventListener('change', () => refreshCatalog()));
  catalog.querySelector('form').addEventListener('submit', event => { event.preventDefault(); refreshCatalog(); });
  reset.addEventListener('click', () => {
    clearTimeout(searchTimer);
    fields.forEach(name => { controls[name].value = name === 'tri' ? 'selection' : ''; });
    refreshCatalog(); controls.recherche.focus();
  });
  refreshCatalog(false);
}

// Reveal content once; keep all content visible if JavaScript is unavailable.
const activeReveals = new Set();
let revealObserver;
function setupReveals() {
  revealObserver?.disconnect();
  activeReveals.forEach(animation => animation.cancel()); activeReveals.clear();
  if (motionPreference.matches || !('IntersectionObserver' in window) || !Element.prototype.animate) return;
  const selector = '.experience-strip > div, .section-title, .large-title, .expertise-card, .path-card, .benefit-grid article, .team-member, .social-card, .category-card, .service-feature, .workflow-step';
  revealObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      const element = entry.target;
      revealObserver.unobserve(element);
      element.dataset.revealed = 'true';
      const index = [...element.parentElement.children].indexOf(element);
      const animation = element.animate([{ opacity: 0, transform: 'translateY(12px)' }, { opacity: 1, transform: 'translateY(0)' }], { duration: 380, delay: Math.max(0, index % 3) * 45, easing: 'cubic-bezier(.22, 1, .36, 1)', fill: 'backwards' });
      activeReveals.add(animation);
      animation.onfinish = animation.oncancel = () => activeReveals.delete(animation);
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -15px 0px' });
  document.querySelectorAll(selector).forEach(element => { if (!element.dataset.revealed) revealObserver.observe(element); });
}
motionPreference.addEventListener('change', setupReveals);
setupReveals();
