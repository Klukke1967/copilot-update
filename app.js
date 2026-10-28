
async function loadNews() {
  try {
    const res = await fetch('updates.json?t=' + Date.now());
    const data = await res.json();
    
    // Vi ved fra tidligere at data er et array af items. 
    // Men hvis den fejler med "forEach is not a function", er det fordi 'data' er noget andet.
    // Jeg tilføjer en log her for at se hvad der kommer ind.
    console.log("Data fra updates.json:", data);

    if (!Array.isArray(data)) {
        console.error("Data er ikke et array!");
        return;
    }

    data.forEach(item => {
        const targetId = item.category || 'Copilot'; // Fallback til Copilot
        const target = document.getElementById(targetId);
        if (target) {
          target.innerHTML += `<div class="card"><h3>${item.title}</h3><a href="${item.link}" target="_blank">Læs mere</a></div>`;
        }
    });
  } catch (error) {
    console.error('Error loading news:', error);
  }
}
document.addEventListener('DOMContentLoaded', loadNews);
