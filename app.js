async function loadNews() {
  try {
    const res = await fetch('/updates.json?t=' + Date.now());
    const data = await res.json();
    const container = document.getElementById('updates');
    
    const items = Array.isArray(data) ? data : (data.items || []);
    
    if (items.length === 0) {
      container.innerHTML = '<p>Ingen nyheder tilgængelige.</p>';
      return;
    }

    container.innerHTML = items.map(item => `
      <div class="card">
        <h2>${item.title || 'Uden titel'}</h2>
        <p>${item.summary || 'Ingen opsummering'}</p>
        <a href="${item.link}" target="_blank">Læs mere</a>
      </div>
    `).join('');
  } catch (error) {
    document.getElementById('updates').innerHTML = '<p>Kunne ikke hente nyheder. Prøv igen senere.</p>';
    console.error('Error loading news:', error);
  }
}
document.addEventListener('DOMContentLoaded', loadNews);
