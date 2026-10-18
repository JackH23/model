import '@fontsource/dm-sans/latin-400.css';
import '@fontsource/dm-sans/latin-600.css';
import '@fontsource/space-grotesk/latin-500.css';
import '@fontsource/space-grotesk/latin-700.css';
import './style.css';
import './gallery.css';
import { models, assetUrl } from './catalog.js';
const grid = document.querySelector('#model-grid');
const prefetched = new Set();
function prefetchModel(model) {
  if (prefetched.has(model.id) || navigator.connection?.saveData || /(^|-)2g$/.test(navigator.connection?.effectiveType || '')) return;
  prefetched.add(model.id);
  const link = document.createElement('link');
  link.rel = 'prefetch'; link.as = 'fetch'; link.crossOrigin = 'anonymous'; link.href = assetUrl(model.file);
  document.head.append(link);
}
function render(query = '') {
  grid.replaceChildren();
  const filtered = models.filter(model => `${model.name} ${model.category} ${model.description}`.toLowerCase().includes(query.toLowerCase().trim()));
  for (const model of filtered) {
    const card = document.createElement('a');
    card.className = 'model-card';
    card.addEventListener('pointerenter', () => prefetchModel(model), { once: true });
    card.addEventListener('focus', () => prefetchModel(model), { once: true });
    card.href = `${import.meta.env.BASE_URL}viewer.html?model=${encodeURIComponent(model.id)}`;
    card.setAttribute('aria-label', `Open ${model.name} interactive model`);
    const imageWrap = document.createElement('div'); imageWrap.className = 'card-image';
    const image = document.createElement('img'); image.src = assetUrl(model.preview); image.alt = `${model.name} 3D model preview`; image.width = 900; image.height = 900;
    const chip = document.createElement('span'); chip.className = 'card-chip'; chip.textContent = 'INTERACTIVE 3D';
    imageWrap.append(image, chip);
    const body = document.createElement('div'); body.className = 'card-body';
    const category = document.createElement('span'); category.className = 'eyebrow'; category.textContent = model.category;
    const title = document.createElement('h3'); title.textContent = model.name;
    const description = document.createElement('p'); description.textContent = model.description;
    const footer = document.createElement('div'); footer.className = 'card-footer';
    const count = document.createElement('span'); count.textContent = model.partCount ? `${model.partCount} individual parts` : 'Explore the assembly';
    const open = document.createElement('span'); open.textContent = 'Open model ↗';
    footer.append(count, open); body.append(category, title, description, footer); card.append(imageWrap, body); grid.append(card);
  }
  document.querySelector('#catalog-empty').hidden = filtered.length !== 0;
  document.querySelector('#model-count').textContent = String(models.length).padStart(2, '0');
}
document.querySelector('#model-search').addEventListener('input', event => render(event.target.value));
render();
