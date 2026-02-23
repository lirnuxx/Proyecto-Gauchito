const runBtn = document.getElementById('runBtn');
const fileInput = document.getElementById('fileInput');
const resultsContainer = document.getElementById('results');

// 1. Preview de la foto
fileInput.onchange = () => {
    const file = fileInput.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const preview = document.getElementById('preview');
            document.getElementById('label').style.display = 'none';
            preview.src = e.target.result;
            preview.style.display = 'block';
            if(label) label.style.opacity = '0.2';
        };
       
        reader.readAsDataURL(fileInput.files[0]);
        mostrarAviso();
    }
};

// 2. Ejecutar Análisis
runBtn.onclick = async () => {
    if (!fileInput.files[0]) return alert("Falta la imagen");

    runBtn.disabled = true;
    runBtn.innerHTML = `<span class="spinner-mini"></span> Procesando...`;
    resultsContainer.innerHTML = "<p style='text-align:center;' class='titilar'>Evaluando color de muestras...</p>";

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    try {
        const response = await fetch('/analizar_color', { method: 'POST', body: formData });
        const data = await response.text();
        
        // Llamamos a la función que agrupa el texto
        mostrarResumen(data);

    } catch (error) {
        resultsContainer.innerHTML = `<p style="color:red;">Error de conexión.</p>`;
    } finally {
        runBtn.disabled = false;
        runBtn.innerHTML = "Analizar Ahora";
    }
};

function mostrarResumen(data) {
    resultsContainer.innerHTML = "";

    const lineas = data.split('\n').filter(l => l.trim() !== "");

    let aptas = [];
    let noAptas = [];

    lineas.forEach(linea => {
        const texto = linea.trim();
        const textoMayus = texto.toUpperCase();

        if (textoMayus.includes("APTO BLANCO")) {
            const numeros = texto.match(/\d+/g);
            if (numeros) {
                aptas = numeros;
            }
        }

        else if (textoMayus.includes("NO APTO AMARILLO")) {
            const numeros = texto.match(/\d+/g);
            if (numeros) {
                noAptas = numeros;
            }
        }
    });

    if (aptas.length > 0) {
        const divAptas = document.createElement('div');
        divAptas.className = 'resultado-card-resumen apto';

        const listaIds = aptas.map(id => `N° ${id}`).join(', ');
        divAptas.innerHTML = `
            <p><strong>APTO BLANCO ("LA EMPANADERIA"):</strong> ${listaIds}</p>
        `;

        resultsContainer.appendChild(divAptas);
    }

    if (noAptas.length > 0) {
        const divNoAptas = document.createElement('div');
        divNoAptas.className = 'resultado-card-resumen no-apto';

        const listaIds = noAptas.map(id => `N° ${id}`).join(', ');
        divNoAptas.innerHTML = `
            <p><strong>NO APTO AMARILLO ("LA EMPANADERIA"):</strong> ${listaIds}</p>
        `;

        resultsContainer.appendChild(divNoAptas);
    }
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
toggleSwitch.addEventListener('change', switchTheme, false)