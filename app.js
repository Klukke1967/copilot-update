const UPDATE_KEY = 'copilot-dashboard-build-time';
const BUILD_VERSION_URL = 'version.json';
const DATA_URL = 'updates.json';

const els = {
  updates: document.getElementById('updates'),
  sources: document.getElementById('sources'),
  toast: document.getElementById('toast'),
  buildInfo: document.getElementById('buildInfo'),
  lastChecked: document.getElementById('lastChecked'),
  reloadBtn: document.getElementById('reloadBtn'),
  refreshBtn: document.getElementById('refreshBtn'),
  updateNowBtn: document.getElementById('updateNowBtn'),
};

function fmtDate(value) {
  if (!value) return 'Ukendt dato';
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return value;
  return d.toLocaleString('da-DK', { dateStyle: 'medium', timeStyle: 'short' });
}

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

async function fetchJson(url) {
  const response = await fetch(`${url}?v=${Date.now()}`, { cache: 'no-store' });
  if (!response.ok) throw new Error(`${url} ${response.status}`);
  return response.json();
}

function renderUpdates(data) {
  const items = Array.isArray(data.items) ? data.items : [];
  if (!items.length) {
    els.updates.innerHTML = '<div class="empty">Ingen Copilot-opdateringer endnu. Når feedet opdateres, vises de her.</div>';
    return;
  }
  els.updates.innerHTML = items.map(item => `
    <article class="update">
      <div class="meta">
        <span>${escapeHtml(item.source || 'Copilot')}</span>
        <span>•</span>
        <span>${escapeHtml(fmtDate(item.published || item.updated || item.fetchedAt))}</span>
      </div>
      <h3><a href="${escapeHtml(item.link || '#')}" target="_blank" rel="noreferrer noopener">${escapeHtml(item.title || 'Uden titel')}</a></h3>
      <p>${escapeHtml(item.summary || item.description || 'Ingen beskrivelse')}</p>
    </article>
  `).join('');
}

function renderSources(data) {
  const sources = Array.isArray(data.sources) ? data.sources : [];
  if (!sources.length) {
    els.sources.innerHTML = '<div class="empty">Ingen kilder er konfigureret endnu.</div>';
    return;
  }
  els.sources.innerHTML = sources.map(source => `
    <div class="source-item">
      <strong>${escapeHtml(source.name)}</strong>
      <div class="meta">
        <span>${escapeHtml(source.feedUrl)}</span>
      </div>
      <div><a href="${escapeHtml(source.homepage || source.feedUrl)}" target="_blank" rel="noreferrer noopener">Åbn kilde</a></div>
    </div>
  `).join('');
}

async function checkForUpdate() {
  try {
    const data = await fetchJson(BUILD_VERSION_URL);
    const current = String(data.buildTime || '');
    const last = localStorage.getItem(UPDATE_KEY);
    els.buildInfo.textContent = `Bygget: ${fmtDate(data.generatedAt || data.buildTime)}`;
    els.lastChecked.textContent = `Sidst tjekket: ${fmtDate(new Date().toISOString())}`;
    if (last && current && current !== last) {
      els.toast.style.display = 'block';
    }
    if (current) localStorage.setItem(UPDATE_KEY, current);
  } catch (error) {
    els.lastChecked.textContent = 'Kan ikke læse version.json';
  }
}

async function refreshData() {
  els.refreshBtn.disabled = true;
  els.refreshBtn.textContent = 'Henter…';
  try {
    const data = await fetchJson(DATA_URL);
    renderUpdates(data);
    renderSources(data);
    els.buildInfo.textContent = `Bygget: ${fmtDate(data.generatedAt)}`;
  } catch (error) {
    els.updates.innerHTML = `<div class="empty">Kunne ikke hente opdateringer: ${escapeHtml(error.message)}</div>`;
  } finally {
    els.refreshBtn.disabled = false;
    els.refreshBtn.textContent = 'Opdater data';
  }
}

function reloadPage() {
  const url = new URL(window.location.href);
  url.searchParams.set('v', Date.now().toString());
  window.location.href = url.toString();
}

async function init() {
  await Promise.all([checkForUpdate(), refreshData()]);
  if ('serviceWorker' in navigator) {
    try {
      await navigator.serviceWorker.register('sw.js');
    } catch (error) {
      console.warn('SW registration failed', error);
    }
  }
}

els.reloadBtn.addEventListener('click', reloadPage);
els.updateNowBtn.addEventListener('click', reloadPage);
els.refreshBtn.addEventListener('click', refreshData);
window.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'visible') checkForUpdate();
});
window.addEventListener('focus', checkForUpdate);
window.addEventListener('load', init);
