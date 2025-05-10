import os
import re
import random
import streamlit as st
import streamlit.components.v1 as components
import requests
from newspaper import Article
from typing import Optional, List, Dict, Any

# --- Costanti ---
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL_NAME = "llama-3.1-70b-versatile" # Aggiornato al modello più recente se disponibile
# GROQ_MODEL_NAME = "llama3-70b-8192" # Alternativa comune
# GROQ_MODEL_NAME = "mixtral-8x7b-32768" # Altra alternativa
REQUEST_TIMEOUT = 60  # Secondi

DEFAULT_PANEL_TITLES = [
    "Ehi, guarda un po'!", "Colpo di scena!", "Cosa succede qui?",
    "Notizia Flash!", "Un momento importante!", "E poi...", "Dritto al punto!"
]

AVAILABLE_ICONS = [
    "icon-globe", "icon-ai", "icon-code", "icon-trophy", "icon-star",
    "icon-fire", "icon-lightbulb", "icon-music", "icon-book", "icon-rocket",
    "icon-map", "icon-blockchain", "icon-gameboy", "icon-machine", "icon-leaf", "icon-team", "icon-cloud"
]

# --- CSS per lo stile fumettistico ---
COMIC_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Bangers&family=Comic+Neue:wght@400;700&display=swap');

body:has(.comic-container) {
    font-family: 'Comic Neue', cursive;
    background: linear-gradient(135deg, #f6f8fa, #e9ecef); /* Sfondo più leggero */
    margin: 0;
    padding: 20px;
    color: #24292e; /* Testo più scuro per contrasto */
    overflow-x: hidden;
}

.comic-container {
    display: flex;
    flex-wrap: wrap;
    gap: 25px; /* Leggermente ridotto */
    justify-content: center;
    max-width: 1400px; /* Aumentato per layout wide */
    margin: 20px auto;
    padding: 25px;
    background-color: #ffffff;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    border-radius: 12px;
    box-sizing: border-box;
}

.panel {
    background-color: #ffffff;
    border: 4px solid #333; /* Bordo leggermente più sottile */
    box-shadow: 3px 3px 10px rgba(0, 0, 0, 0.2);
    padding: 20px;
    border-radius: 8px;
    position: relative;
    overflow: hidden;
    width: calc(50% - 25px); /* Adattato al nuovo gap */
    min-width: 320px;
    box-sizing: border-box;
    opacity: 0;
    transform: translateY(30px);
    transition: opacity 0.6s ease-out, transform 0.6s ease-out;
}

.panel.visible { /* Questa classe dovrà essere aggiunta dinamicamente con JS se si vuole un'animazione all'entrata 'on scroll' */
    opacity: 1; /* Per ora, tutti visibili subito dopo il caricamento */
    transform: translateY(0);
}

.panel h2 {
    font-family: 'Bangers', cursive;
    color: #e53935; /* Rosso vibrante */
    text-align: center;
    margin-top: 0;
    text-shadow: 1px 1px #555; /* Ombra più soft */
    font-size: 2.2em;
    line-height: 1.2;
    margin-bottom: 15px;
}

.panel p {
    margin-top: 10px;
    line-height: 1.6;
    text-align: justify;
    white-space: pre-wrap; /* Mantiene le interruzioni di riga del testo generato */
    font-size: 1.1em;
    color: #333;
}

.panel-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 0 10px;
}

.icon {
    font-size: 3.5em; /* Icone più grandi */
    margin: 10px auto 15px auto;
    text-align: center;
    color: #ff8f00; /* Colore arancione per le icone */
}

/* Definizioni icone Emoji (semplici e cross-platform) */
.icon-trophy::before { content: '🏆'; }
.icon-globe::before { content: '🌍'; }
.icon-map::before { content: '🗺️'; } /* Mappa più generica */
.icon-blockchain::before { content: '🔗'; }
.icon-gameboy::before { content: '👾'; }
.icon-machine::before { content: '⚙️'; } /* Ingranaggio */
.icon-leaf::before { content: '🌿'; }
.icon-star::before { content: '⭐'; }
.icon-team::before { content: '👥'; } /* Gruppo persone */
.icon-ai::before { content: '🤖'; }
.icon-code::before { content: '💻'; }
.icon-cloud::before { content: '☁️'; }
.icon-fire::before { content: '🔥'; }
.icon-lightbulb::before { content: '💡'; }
.icon-music::before { content: '🎵'; }
.icon-book::before { content: '📚'; }
.icon-rocket::before { content: '🚀'; }

@media (max-width: 992px) { /* Nuovo breakpoint per tablet */
    .panel {
        width: calc(100% - 25px); /* Un pannello per riga su tablet */
    }
}

@media (max-width: 768px) {
    .panel {
        width: 100%; /* Già un pannello per riga, ma per coerenza */
    }
    .icon { font-size: 2.5em; }
    body:has(.comic-container) { padding: 15px; }
    .comic-container { padding: 15px; gap: 20px; }
}

@media (max-width: 480px) {
    .panel h2 { font-size: 1.8em; }
    .panel p { font-size: 1em; }
    .icon { font-size: 2.2em; }
    body:has(.comic-container) { padding: 10px; }
    .comic-container { padding: 10px; gap: 15px; }
}
"""

# --- Funzioni Helper ---

def get_article_content(url: str) -> Optional[str]:
    """Estrae il testo principale da un articolo all'URL specificato."""
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        st.error(f"Errore nell'estrazione dell'articolo da {url}.")
        st.error(f"Dettagli: {e}")
        return None

def transform_text_narrative(api_key: str, text: str) -> Optional[str]:
    """
    Trasforma il testo fornito in uno stile fumettistico narrativo
    utilizzando l'API Groq.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    prompt = (
        "Sei un simpatico e abile narratore di fumetti. Riscrivi il seguente articolo in uno stile fumettistico, "
        "estremamente semplice, accattivante e informativo, come se stessi raccontando una storia a dei bambini o ragazzi. "
        "Usa un linguaggio vivace e diretto. Dividi il testo in brevi pannelli (paragrafi) separati da una doppia interruzione di riga (\\n\\n). "
        "Ogni pannello dovrebbe concentrarsi su un'idea o un evento chiave. "
        "NON includere placeholder, descrizioni di immagini (es. '[Immagine di...]') o metacommenti sul tuo ruolo. "
        "Inizia direttamente con la narrazione. Ecco il testo dell'articolo:\n\n"
        f"{text}"
    )
    payload = {
        "model": GROQ_MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7, # Un po' di creatività
        "max_tokens": 3000, # Aumentato per articoli più lunghi
    }

    try:
        response = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()  # Solleva un'eccezione per errori HTTP 4xx/5xx
        data = response.json()

        # st.write("Risposta API Groq (debug):", data) # Decommenta per debug

        choices = data.get("choices")
        if choices and isinstance(choices, list) and len(choices) > 0:
            message = choices[0].get("message")
            if message and isinstance(message, dict):
                transformed_text = message.get("content", "")
                # Rimuove eventuali asterischi usati per il bold (il CSS non li gestisce)
                transformed_text = transformed_text.replace("**", "")
                # Rimuove placeholder come "[Immagine di un eroe]"
                transformed_text = re.sub(r"\[[^\]]*\]", "", transformed_text)
                return transformed_text.strip()
        
        st.warning("L'API Groq ha restituito una risposta inattesa o vuota.")
        st.json(data) # Mostra la risposta per debug
        return None

    except requests.exceptions.HTTPError as http_err:
        st.error("Errore HTTP durante la chiamata all'API Groq.")
        st.error(f"Status Code: {http_err.response.status_code}")
        try:
            st.error(f"Dettagli errore API: {http_err.response.json()}")
        except ValueError:
            st.error(f"Dettagli errore API (testo): {http_err.response.text}")
        return None
    except requests.exceptions.RequestException as req_err:
        st.error(f"Errore di connessione o timeout durante la chiamata all'API Groq: {req_err}")
        return None
    except Exception as e:
        st.error("Errore imprevisto durante la trasformazione del testo.")
        st.error(f"Dettagli: {e}")
        return None

def generate_panel_html(title: str, content: str, icon_class: str) -> str:
    """Genera l'HTML per un singolo pannello del fumetto."""
    return f"""
    <div class="panel visible"> {/* Aggiunta 'visible' per l'animazione */}
        <div class="panel-content">
            <div class="icon {icon_class}"></div>
            <h2>{title}</h2>
            <p>{content}</p>
        </div>
    </div>
    """

def display_comic_output(comic_text: str):
    """Suddivide il testo del fumetto e genera l'HTML completo per la visualizzazione."""
    panels_data = [panel.strip() for panel in comic_text.split("\n\n") if panel.strip()]
    if not panels_data:
        st.warning("Il testo trasformato non contiene pannelli validi. Mostro il testo grezzo.")
        panels_data = [comic_text] # Fallback a un singolo pannello

    panels_html_list = []
    for idx, panel_text in enumerate(panels_data):
        lines = panel_text.split("\n", 1) # Dividi solo sulla prima interruzione di riga
        
        # Tentativo di estrarre un titolo se la prima riga è breve e distintiva
        potential_title = lines[0].strip()
        if len(lines) > 1 and len(potential_title) < 70 and not potential_title.endswith(('.', '!', '?')):
            title = potential_title
            content = lines[1].strip() if len(lines) > 1 else "..." # Contenuto del pannello
        else:
            title = random.choice(DEFAULT_PANEL_TITLES) # Titolo di default
            content = panel_text # L'intero testo del pannello è il contenuto

        icon_class = random.choice(AVAILABLE_ICONS)
        panels_html_list.append(generate_panel_html(title, content, icon_class))

    panels_html_content = "\n".join(panels_html_list)
    
    full_html = f"""
    <!DOCTYPE html>
    <html lang="it">
    <head>
      <meta charset="utf-8">
      <title>Articolo a Fumetti Narrativo</title>
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <style>
      {COMIC_CSS}
      </style>
    </head>
    <body>
      <div class="comic-container">
          {panels_html_content}
      </div>
    </body>
    </html>
    """
    components.html(full_html, height=1200, scrolling=True)

# --- Interfaccia Streamlit ---
st.set_page_config(page_title="Articolo a Fumetti", layout="wide", initial_sidebar_state="collapsed")

st.title("🎨 Articolo a Fumetti ⚡")
st.markdown("Trasforma un noioso articolo di notizie in un vivace fumetto narrativo!")

# Gestione API Key
if 'GROQ_API_KEY' not in st.session_state:
    st.session_state.GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")

if not st.session_state.GROQ_API_KEY:
    st.session_state.GROQ_API_KEY = st.text_input(
        "🔑 Inserisci la tua chiave API Groq:", 
        type="password",
        help="Puoi ottenere una chiave API gratuita da console.groq.com"
    )

article_url = st.text_input("🔗 Inserisci il link dell'articolo:", placeholder="Es. https://www.example.com/news/article-name")

if st.button("Trasforma in Fumetto!", type="primary", use_container_width=True):
    if not article_url:
        st.error("🤔 Ops! Sembra che tu abbia dimenticato di inserire un link.")
    elif not st.session_state.GROQ_API_KEY:
        st.error("🔑 Per favore, inserisci la tua chiave API Groq per continuare.")
    else:
        with st.spinner("Sto recuperando l'articolo dal web... 📰"):
            article_text = get_article_content(article_url)

        if article_text:
            st.info(f"Ho trovato un articolo di circa {len(article_text)} caratteri. Ora lo trasformo!")
            with st.spinner("Sto scatenando la mia creatività fumettistica con Groq... 🗯️"):
                comic_text_output = transform_text_narrative(st.session_state.GROQ_API_KEY, article_text)

            if comic_text_output:
                st.success("🚀 Ecco il tuo articolo a fumetti!")
                display_comic_output(comic_text_output)
            else:
                st.error("😭 Non sono riuscito a trasformare l'articolo in un fumetto. Controlla i messaggi di errore sopra.")
        else:
            st.error("❌ Non sono riuscito a estrarre il contenuto dall'articolo fornito.")

st.markdown("---")
st.markdown("Realizzato con ❤️ da un AI Assistant e Streamlit. Icone e font da fonti open.")
