'use strict';
const header = document.querySelector('.site-header');
const navigation = document.querySelector('#navigation');
const menuToggle = document.querySelector('.menu-toggle');
const dropdowns = [...document.querySelectorAll('.dropdown')];
const backToTop = document.querySelector('.back-to-top');
function closeMenu() {
  navigation.classList.remove('is-open');
  menuToggle.setAttribute('aria-expanded', 'false');
  menuToggle.setAttribute('aria-label', 'Ouvrir le menu');
  dropdowns.forEach(menu => { menu.open = false; });
}
function updateHeader() {
  header.classList.toggle('scrolled', window.scrollY > 35);
  const height = document.documentElement.scrollHeight - window.innerHeight;
  const progress = height > 0 ? Math.min(1, Math.max(0, window.scrollY / height)) : 0;
  document.documentElement.style.setProperty('--scroll-progress', progress);
  const showBackToTop = window.scrollY > 600;
  backToTop.classList.toggle('is-visible', showBackToTop);
  backToTop.tabIndex = showBackToTop ? 0 : -1;
}
let scrollFrame = null;
window.addEventListener('scroll', () => {
  if (scrollFrame !== null) return;
  scrollFrame = requestAnimationFrame(() => {
    updateHeader();
    scrollFrame = null;
  });
}, { passive: true });
window.addEventListener('resize', updateHeader, { passive: true });
updateHeader();
menuToggle.addEventListener('click', () => {
  const open = menuToggle.getAttribute('aria-expanded') !== 'true';
  menuToggle.setAttribute('aria-expanded', String(open));
  menuToggle.setAttribute('aria-label', open ? 'Fermer le menu' : 'Ouvrir le menu');
  navigation.classList.toggle('is-open', open);
});
dropdowns.forEach(menu => {
  menu.addEventListener('toggle', () => {
    if (menu.open) dropdowns.forEach(other => { if (other !== menu) other.open = false; });
  });
});
document.addEventListener('click', event => {
  if (!header.contains(event.target)) closeMenu();
});
navigation.querySelectorAll('a').forEach(link => link.addEventListener('click', closeMenu));
document.addEventListener('keydown', event => {
  if (event.key === 'Escape') closeMenu();
});
window.matchMedia('(min-width: 981px)').addEventListener('change', closeMenu);

const videoFeature = document.querySelector('.video-feature');
const video = videoFeature.querySelector('video');
videoFeature.querySelector('.video-cover').addEventListener('click', async () => {
  videoFeature.classList.add('playing');
  video.focus();
  // Prefer the retained video when the full site is served; an isolated HTML
  // preview falls back to the reference site's video.
  if (/^https?:$/.test(location.protocol)) {
    const localSource = new URL('assets/presentation.mp4', location.href);
    try {
      const response = await fetch(localSource, { method: 'HEAD', signal: AbortSignal.timeout(2500) });
      if (response.ok && response.headers.get('content-type')?.includes('video/mp4')) {
        video.src = localSource.href;
      }
    } catch { /* The standalone preview can still use the remote source. */ }
  }
  video.play().catch(() => { /* Native controls remain available if autoplay is refused. */ });
});
video.querySelector('source').addEventListener('error', () => {
  videoFeature.querySelector('.video-error').hidden = false;
});

const track = document.querySelector('.gallery-track');
const slides = [...track.querySelectorAll('.gallery-slide')];
function moveGallery(direction) {
  const distance = slides[0].getBoundingClientRect().width + parseFloat(getComputedStyle(track).gap);
  const end = track.scrollWidth - track.clientWidth;
  let target = track.scrollLeft + direction * distance;
  if (target > end + 5) target = 0;
  if (target < -5) target = end;
  track.scrollTo({ left: Math.max(0, target), behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth' });
}
document.querySelector('.gallery-prev').addEventListener('click', () => moveGallery(-1));
document.querySelector('.gallery-next').addEventListener('click', () => moveGallery(1));

const lightbox = document.querySelector('.lightbox');
let photoIndex = 0;
function updatePhoto() {
  const source = slides[photoIndex];
  lightbox.querySelector('img').src = source.dataset.image;
  lightbox.querySelector('img').alt = source.querySelector('img').alt;
}
function openDialog(dialog) { dialog.showModal(); document.body.classList.add('modal-open'); }
slides.forEach((slide, index) => slide.addEventListener('click', () => {
  photoIndex = index;
  updatePhoto();
  openDialog(lightbox);
}));
function movePhoto(direction) {
  photoIndex = (photoIndex + direction + slides.length) % slides.length;
  updatePhoto();
}
lightbox.querySelector('.lightbox-prev').addEventListener('click', () => movePhoto(-1));
lightbox.querySelector('.lightbox-next').addEventListener('click', () => movePhoto(1));
lightbox.addEventListener('keydown', event => {
  if (event.key === 'ArrowLeft') movePhoto(-1);
  if (event.key === 'ArrowRight') movePhoto(1);
});
document.querySelectorAll('dialog').forEach(dialog => {
  dialog.querySelector('.dialog-close').addEventListener('click', () => dialog.close());
  dialog.addEventListener('close', () => document.body.classList.remove('modal-open'));
  dialog.addEventListener('click', event => {
    if (event.target === dialog) {
      const box = dialog.getBoundingClientRect();
      if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) dialog.close();
    }
  });
});

const contactDialog = document.querySelector('.contact-dialog');
const summary = contactDialog.querySelector('.request-summary');
const copyStatus = contactDialog.querySelector('.copy-status');
document.querySelector('#contact-form').addEventListener('submit', event => {
  event.preventDefault();
  const data = new FormData(event.currentTarget);
  summary.textContent = `${data.get('prenom').trim()} ${data.get('nom').trim()}\nTéléphone : ${data.get('tel').trim()}\nE-mail : ${data.get('email').trim()}\n\n${data.get('message').trim()}`;
  copyStatus.textContent = '';
  openDialog(contactDialog);
});
contactDialog.querySelector('.copy-request').addEventListener('click', async () => {
  try {
    await navigator.clipboard.writeText(summary.textContent);
    copyStatus.textContent = 'Votre demande a été copiée.';
  } catch {
    const selection = window.getSelection();
    const range = document.createRange();
    range.selectNodeContents(summary);
    selection.removeAllRanges();
    selection.addRange(range);
    copyStatus.textContent = 'Sélectionnez puis copiez votre demande pour la transmettre.';
  }
});

// Content stays visible when scripts are blocked in an HTML preview. Animate
// each section once as it enters the viewport, without retaining transforms
// that would interfere with card hover or keyboard focus.
const motionPreference = window.matchMedia('(prefers-reduced-motion: reduce)');
const activeReveals = new Set();
let revealObserver;
function setupReveals() {
  revealObserver?.disconnect();
  activeReveals.forEach(animation => animation.cancel());
  activeReveals.clear();
  if (motionPreference.matches || !('IntersectionObserver' in window) || !Element.prototype.animate) return;
  const selector = '.experience-strip > div, .section-kicker, .section-title, .large-title, .section-description, .expertise-card, .why-intro > p, .benefit-grid article, .team-member, .social-card, .contact-section form';
  revealObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      const element = entry.target;
      revealObserver.unobserve(element);
      element.dataset.revealed = 'true';
      const isCard = element.matches('.expertise-card, .team-member, .social-card, .benefit-grid article');
      const siblings = [...element.parentElement.children];
      const delay = isCard ? (siblings.indexOf(element) % 3) * 85 : 0;
      const animation = element.animate([
        { opacity: 0, transform: 'translateY(22px)' },
        { opacity: 1, transform: 'translateY(0)' },
      ], { duration: 650, delay, easing: 'cubic-bezier(.22, 1, .36, 1)', fill: 'backwards' });
      activeReveals.add(animation);
      animation.onfinish = animation.oncancel = () => activeReveals.delete(animation);
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -35px 0px' });
  document.querySelectorAll(selector).forEach(element => {
    if (!element.dataset.revealed) revealObserver.observe(element);
  });
}
motionPreference.addEventListener('change', setupReveals);
setupReveals();
