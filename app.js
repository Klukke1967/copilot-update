
async function loadNews() {
  try {
    const res = await fetch('updates.json?t=' + Date.now());
    const rawData = await res.json();
    console.log("Data type:", typeof rawData);
    console.log("Data:", rawData);
    
    // Hvis vi stadig ser fejl, lad os tvinge den til array
    const data = Array.isArray(rawData) ? rawData : (rawData.items || []);
    
    data.forEach(item => {
        // Mapping logik: AI -> Google AI, Tech -> Generel AI, Resten -> Copilot
        let targetId = 'Copilot';
        const cat = (item.category || "").toLowerCase();
        if (cat.includes('ai')) {
            targetId = 'Google AI';
        } else if (cat.includes('tech')) {
            targetId = 'Generel AI';
        }
        
        const target = document.getElementById(targetId);
        if (target) {
          target.innerHTML += `<div class="card"><h3>${item.title}</h3><a href="${item.link}" target="_blank">Læs mere</a></div>`;
        } else {
          console.warn("Element med id " + targetId + " ikke fundet.");
        }
    });
  } catch (error) {
    console.error('Error loading news:', error);
  }
}
document.addEventListener('DOMContentLoaded', loadNews);
