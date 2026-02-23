const runBtn = document.getElementById('runBtn');
const fileInput = document.getElementById('fileInput');
const results = document.getElementById('results');

fileInput.onchange = () => {
    const reader = new FileReader();
    reader.onload = (e) => {
        document.getElementById('preview').src = e.target.result;
        document.getElementById('preview').style.display = 'block';
        document.getElementById('label').style.display = 'none';
    };
    reader.readAsDataURL(fileInput.files[0]);
    mostrarAviso();
};

runBtn.onclick = async () => {

    if (!fileInput.files[0]) return alert("Sube una foto del gratinado");
    results.innerHTML = "<p style='text-align:center;' class='titilar'>Analizando muestras de gratinado...</p>";
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    const resp = await fetch('/analizar_gratinado', { method: 'POST', body: formData });
    const text = await resp.text();
    
    renderizarLista(text);
};

function renderizarLista(text) {
    results.innerHTML = "<div class='lista-resultados'></div>";
    const container = results.querySelector('.lista-resultados');
    const lineas = text.split('\n').filter(l => l.includes(':'));

    lineas.forEach(linea => {
        const esApto = linea.toUpperCase().includes("APTO") && !linea.toUpperCase().includes("NO APTO");
        const [titulo, resto] = linea.split(':');
        const card = document.createElement('div');
        card.className = 'resultado-card';
        card.innerHTML = `
            <div class="status-bar ${esApto ? 'bg-apto' : 'bg-no-apto'}"></div>
            <div class="resultado-info">
                <div class="resultado-header">
                    <span class="resultado-titulo">${titulo.trim()}</span>
                    <span class="badge-status ${esApto ? 'badge-apto' : 'badge-no-apto'}">${esApto ? 'Aprobado' : 'Rechazado'}</span>
                </div>
                <div class="resultado-descripcion">${resto ? resto.trim() : ''}</div>
            </div>`;
        container.appendChild(card);
    });
}

function mostrarAviso() {
    const aviso = document.createElement('div');
    aviso.className = 'notificacion-aviso';
    aviso.innerHTML = '⚠️ <b>Recordatorio:</b> Las muestras deben estar numeradas en la foto.';
    document.body.appendChild(aviso);
    setTimeout(() => { aviso.remove(); }, 7000);
}

const logoutBtn = document.querySelector('.btn-logout');
const modal = document.getElementById('logoutModal');

// Al hacer clic en el botón de la navbar, mostramos el modal
if (logoutBtn) {
    logoutBtn.onclick = (e) => {
        e.preventDefault(); // Evita que el enlace se dispare de inmediato
        modal.style.display = 'flex';
    };
}

// Función para cerrar el modal si se arrepiente
function cerrarModal() {
    modal.style.display = 'none';
}

// Cerrar si hace clic fuera de la cajita blanca
window.onclick = (event) => {
    if (event.target == modal) {
        cerrarModal();
    }
};
const toggleSwitch = document.querySelector('.theme-switch input[type="checkbox"]');
const currentTheme = localStorage.getItem('theme');

// 1. Al cargar, chequear si ya existía una preferencia
if (currentTheme) {
    document.documentElement.setAttribute('data-theme', currentTheme);

    if (currentTheme === 'dark') {
        toggleSwitch.checked = true;
    }
}

// 2. Función para cambiar el tema
function switchTheme(e) {
    if (e.target.checked) {
        document.documentElement.setAttribute('data-theme', 'dark');
        localStorage.setItem('theme', 'dark');
    } else {
        document.documentElement.setAttribute('data-theme', 'light');
        localStorage.setItem('theme', 'light');
    }    
}

// 3. Escuchar el evento de cambio
toggleSwitch.addEventListener('change', switchTheme, false);