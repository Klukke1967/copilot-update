async function checkUpdate() {
    try {
        const response = await fetch('version.json?cache-bust=' + Date.now());
        const data = await response.json();
        const lastBuild = localStorage.getItem('buildTime');
        if (lastBuild && data.buildTime > lastBuild) {
            document.getElementById('update-toast').style.display = 'block';
        }
        localStorage.setItem('buildTime', data.buildTime);
    } catch (e) {}
}
setInterval(checkUpdate, 60000);
checkUpdate();
