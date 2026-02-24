import io
import os
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from google import genai
from PIL import Image              

app = Flask(__name__)
app.secret_key = 'A231Juhsda334gtyfaus-1204os-NADHsf' # Cambia esto por algo aleatorio



API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)
MODEL_ID = "gemini-3-flash-preview"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

USERS = {
    "CanagroSA": "laboratorio2026",
}

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    if user_id not in USERS:
        return None
    return User(user_id)

# --- RUTAS DE AUTENTICACIÓN ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in USERS and USERS[username] == password:
            user = User(username)
            login_user(user)
            return redirect(url_for('gratinado_page'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- FUNCIÓN AUXILIAR: CARGA DE REFERENCIAS ---
def cargar_referencias(subcarpeta):
    ruta_base = os.path.join('static', 'img', subcarpeta)
    rutas = []

    if os.path.exists(ruta_base):
        archivos = sorted([
            f for f in os.listdir(ruta_base)
            if f.lower().endswith(('.png', '.jpg', '.jpeg'))
        ])
        for archivo in archivos:
            rutas.append(os.path.join(ruta_base, archivo))

    return rutas

REFS_GRATINADO = cargar_referencias('refs_gratinado')
REFS_ROLLITOS = cargar_referencias('refs_rollitos')
REFS_PLANCHA = cargar_referencias('refs_plancha')

@app.route('/')
@login_required
def gratinado_page():
    # Página inicial: IA Gratinado
    return render_template('gratinado.html')

@app.route('/color')
@login_required
def rollitos_page():
    # Página: IA Rollitos
    return render_template('rollito.html')

@app.route('/fundido')
@login_required
def fundido_page():
    # Página: IA fundido
    return render_template('fundido.html')

# --- ENDPOINTS DE ANÁLISIS (IA) ---

@app.route('/analizar_gratinado', methods=['POST'])
def analizar_gratinado():
    file = request.files['file']
    img_lote = Image.open(io.BytesIO(file.read()))
    
    # Carga referencias específicas de la carpeta 'refs_gratinado'
    imagenes_refs = []
    for ruta in REFS_GRATINADO:
        img = Image.open(ruta)
        img.thumbnail((800, 800))  # reduce tamaño
        imagenes_refs.append(img)
    
    prompt = """
    ACTÚA COMO UN AUDITOR DE CONTROL DE CALIDAD VISUAL (ESPECIALISTA EN ALIMENTOS). Tu misión es determinar la aptitud de una muestra de queso gratinado comparándola con un estándar de referencia.

1. CRITERIOS DE CLASIFICACIÓN
RANGO DORADO (APTO): Color y textura comprendidos entre las Imágenes 1, 2, 3 y 4.

PATRONES DE RECHAZO (NO APTO):

QUEMADA (Imagen 5): Tonos más oscuros o negros que el Rango Dorado.

CRUDA (Imagen 6): Color blanco mate, ausencia de burbujas, textura gomosa.

POROSA (Imagen 7): Presencia de cavidades de aire, poros o estructura de panal (Independientemente del color).

2. PROTOCOLO DE ANÁLISIS (ORDEN DE PRIORIDAD)
DETECCIÓN DE POROSIDAD (FILTRO CRÍTICO): Escanea la superficie buscando patrones de "panal de abeja" o burbujas secas. Si detectas poros, clasifica como NO APTO - POROSA inmediatamente, sin importar el color.


3. REGLA DE ORO DE SALIDA
Si la muestra es porosa, el veredicto SIEMPRE es NO APTO - POROSA, aunque el color sea dorado.

4. FORMATO DE RESPUESTA (ESTRICTO)
Responde ÚNICAMENTE con este formato, sin introducciones ni explicaciones: Muestra [N]: [APTO/NO APTO] - [MOTIVO] (Motivos posibles: RANGO DORADO / QUEMADA / POROSA / CRUDA)
    """
    
    
    
    response = client.models.generate_content(
    model=MODEL_ID,
    contents=[
        prompt,
        *imagenes_refs,
        img_lote
    ]
)
    return response.text.strip()

@app.route('/analizar_color', methods=['POST'])
def analizar_color():
    file = request.files['file']
    img_lote = Image.open(io.BytesIO(file.read()))
    
    # Carga referencias específicas de la carpeta 'refs_rollitos'
    imagenes_refs = []
    for ruta in REFS_ROLLITOS:
        img = Image.open(ruta)
        img.thumbnail((800, 800))  # reduce tamaño
        imagenes_refs.append(img)
    
    prompt = """
    IA AUDITORA DE TEXTURA DE ROLLITOS DE MOZZARELLA.
 1. CALIBRACIÓN DE "BLANCO REAL" (MARGEN DE TOLERANCIA)
EL BLANCO NO ES PERFECTO: Entiende que las Imágenes 1, 2 y 3 no son blanco puro (#FFFFFF), sino que tienen matices neutros (hueso, gris claro, crema muy pálido).

FILTRO DE FLASH: Ignora el brillo blanco intenso del flash. Busca el color en las zonas de luz difusa.

FILTRO DE SOMBRA: No castigues las sombras naturales. El color de una sombra no es el color del producto.

2. PROTOCOLO DE EVALUACIÓN (TEST DE COMPARACIÓN DIRECTA)
Para cada muestra, hazte esta pregunta antes de decidir:

¿Es el tono de esta muestra significativamente más cálido/amarillo que la Imagen 3?

SI ES IGUAL O MÁS BLANCO QUE LA IMAGEN 3: Clasifica como APTO.

SI ES VISIBLEMENTE MÁS AMARILLO/MARRÓN/CREMA QUE LA IMAGEN 3: Clasifica como NO APTO.

3. CRITERIOS DE DECISIÓN
APTO (Rango Blanco/Neutro): Incluye tonos blanco, marfil pálido o hueso frío (Similares a las Referencias 1, 2 y 3).

NO APTO (Rango Cálido): Tonos claramente amarillos, pajizos o ámbar (Similares al resto de las referencias).
    Formato de respuesta: 
    BLOQUE APTAS: Si hay muestras blancas, escribe una única línea: [APTO BLANCO ("LA EMPANADERIA"): N° [N], N° [N]...]

    BLOQUE NO APTA: Si hay muestras amarillas, escribe una unica línea: [NO APTO AMARILLO ("LA EMPANADERIA"): N° [N], N° [N]... ]
    """
    
    
    
    response = client.models.generate_content(
    model=MODEL_ID,
    contents=[
        prompt,
        *imagenes_refs,
        img_lote
    ]
)
    return response.text.strip()

@app.route('/analizar_fundido', methods=['POST'])
def analizar_fundido():
    file = request.files['file']
    img_lote = Image.open(io.BytesIO(file.read()))
    
    # Carga referencias específicas de la carpeta 'refs_plancha'
    imagenes_refs = []
    for ruta in REFS_PLANCHA:
        img = Image.open(ruta)
        img.thumbnail((800, 800))  # reduce tamaño
        imagenes_refs.append(img)
    
    prompt = """
    IA AUDITORA DE fundido DE MOZZARELLA.
    Usa las fotos de referencia: las primeras 3 son aptas,  el restoo, estos 3 Errores: Falta de Fundido(aparencia de relieve, puntas o zonas quemadas/oscuras, se mantiene la estructura original del corte), Separación de Fases(canales con liquidos amarillentos), Brownie (blister o burbujas quemadas/oscuras en gran cantidad que supere mas del 20% de la superficie o en su defecto que esten agrupadas en una zona puntual)).
    Aquellas planchas aptas son aquellas que no presentan ninguno de los errores mencionados, y además de apariencia lisa, sin grumos ni surcos, un brillo y color uniforme.
    INSTRUCCIONES:
    - Evalúa cada muestra teniendo en cuenta la liberación de aceite (separación de fases), el exceso de brownie (quemado) y la falta de fundido (cruda).
    - Clasifica cada muestra como APTA o NO APTA.

    
INSTRUCCIONES DE FORMATO ESTRICTO: Analiza las fundido de mozzarella en la imagen basándote en: Separación de Fases (Aceite), Exceso de Brownie (Quemada) y Falta de Fundido (Cruda).

REGLAS DE SALIDA:

BLOQUE APTAS: Si hay muestras correctas, escribe una única línea: APTAS: N° [N], N° [N]...

BLOQUES NO APTAS: Por cada muestra con falla, escribe una línea independiente: Muestra [N]:  [MOTIVO ESPECÍFICO]

NOTAS IMPORTANTES:

Usa exclusivamente estos motivos: "Separacion de Fases", "Exceso de Brownie" o "Falta de Fundido".

Si no hay aptas, omite ese bloque. Si todas son aptas, omite el listado de fallas.

No añadas introducciones ni conclusiones. Solo los bloques de datos.
    """
    
    response = client.models.generate_content(
    model=MODEL_ID,
    contents=[
        prompt,
        *imagenes_refs,
        img_lote
    ]
)
    return response.text.strip()

if __name__ == '__main__':
    # Ejecución del servidor
    app.run(debug=True, port=5000)