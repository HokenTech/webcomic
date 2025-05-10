import os
import re
import random
import streamlit as st
import streamlit.components.v1 as components
import requests
from newspaper import Article
from typing import Optional

# --- COSTANTI ---
# URL e modello per le chiamate all'API Groq
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL_NAME = "llama-3.3-70b-versatile"
REQUEST_TIMEOUT = 90  # Durata massima in secondi per completare una richiesta API

# Icone disponibili per assegnare casualmente ai pannelli del fumetto
AVAILABLE_ICONS = [
    "icon-globe", "icon-ai", "icon-code", "icon-trophy", "icon-star",
    "icon-fire", "icon-lightbulb", "icon-music", "icon-book", "icon-rocket",
    "icon-map", "icon-blockchain", "icon-gameboy", "icon-machine", "icon-leaf", "icon-team", "icon-cloud"
]

# Definizione del CSS per lo stile fumettistico dell'applicazione
COMIC_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Bangers&family=Comic+Neue:wght@400;700&display=swap');
body:has(.comic-container) {
    font-family: 'Comic Neue', cursive;
    background: linear-gradient(135deg, #f6f8fa, #e9ecef);
    margin: 0;
    padding: 20px;
    color: #24292e;
    overflow-x: hidden;
}
.comic-container {
    display: flex;
    flex-wrap: wrap;
    gap: 25px;
    justify-content: center;
    max-width: 1400px;
    margin: 20px auto;
    padding: 25px;
    background-color: #ffffff;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    border-radius: 12px;
    box-sizing: border-box;
}
.panel {
    background-color: #ffffff;
    border: 4px solid #333;
    box-shadow: 3px 3px 10px rgba(0, 0, 0, 0.2);
    padding: 20px;
    border-radius: 8px;
    position: relative;
    overflow: hidden;
    width: calc(50% - 25px);
    min-width: 320px;
    box-sizing: border-box;
    opacity: 0;
    transform: translateY(30px);
    transition: opacity 0.6s ease-out, transform 0.6s ease-out;
}
.panel.visible {
    opacity: 1;
    transform: translateY(0);
}
.panel h2 {
    font-family: 'Bangers', cursive;
    color: #e53935;
    text-align: center;
    margin-top: 0;
    text-shadow: 1px 1px #555;
    font-size: 2.2em;
    line-height: 1.2;
    margin-bottom: 15px;
}
.panel p {
    margin-top: 10px;
    line-height: 1.6;
    text-align: justify;
    white-space: pre-wrap;
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
    font-size: 3.5em;
    margin: 10px auto 15px auto;
    text-align: center;
    color: #ff8f00;
}
.icon-trophy::before { content: '🏆'; }
.icon-globe::before { content: '🌍'; }
.icon-map::before { content: '🗺️'; }
.icon-blockchain::before { content: '🔗'; }
.icon-gameboy::before { content: '👾'; }
.icon-machine::before { content: '⚙️'; }
.icon-leaf::before { content: '🌿'; }
.icon-star::before { content: '⭐'; }
.icon-team::before { content: '👥'; }
.icon-ai::before { content: '🤖'; }
.icon-code::before { content: '💻'; }
.icon-cloud::before { content: '☁️'; }
.icon-fire::before { content: '🔥'; }
.icon-lightbulb::before { content: '💡'; }
.icon-music::before { content: '🎵'; }
.icon-book::before { content: '📚'; }
.icon-rocket::before { content: '🚀'; }
@media (max-width: 992px) {
    .panel {
        width: calc(100% - 25px);
    }
}
@media (max-width: 768px) {
    .panel {
        width: 100%;
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

# --- FUNZIONI DI SUPPORTO ---
def get_article_content(url: str) -> Optional[str]:
    """
    Scarica e analizza il contenuto di un articolo dall'URL specificato.
    Il testo principale viene restituito qualora presente, altrimenti viene restituito None.
    """
    try:
        article = Article(url)
        article.download()
        article.parse()
        if not article.text:
            st.warning(f"L'articolo all'URL {url} è stato scaricato ma il testo non contiene informazioni significative.")
            return None
        return article.text
    except Exception as e:
        st.error(f"Errore durante l'estrazione dell'articolo da {url}.")
        st.error(f"Dettagli tecnici: {e}")
        return None

def transform_text_narrative(api_key: str, text: str) -> Optional[str]:
    """
    Esegue la trasformazione del testo dell'articolo in uno stile fumettistico narrativo tramite l'API Groq.
    Il prompt viene formulato specificando esplicitamente l'elaborazione di titoli per ogni paragrafo,
    evitando l'inserimento esplicito della sequenza '\\n\\n' nell'output finale.
    La risposta dell'API viene sanificata per rimuovere formattazioni indesiderate e sequenze inutili.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    prompt = (
        "Si prega di riscrivere il seguente articolo in uno stile fumettistico narrativo, "
        "utilizzando un linguaggio semplice, accattivante e informativo. "
        "Per ogni paragrafo, elaborare un titolo esplicito e indicarlo chiaramente. "
        "Il testo prodotto non DEVE contenere la sequenza '\\n\\n' esplicitamente, "
        "ma deve essere suddiviso in pannelli distinti in base a concetti e idee. "
        "Di seguito, il testo dell'articolo:\n\n" + text
    )
    payload = {
        "model": GROQ_MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 3500,
    }
    try:
        response = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        st.write("Risposta API Groq (debug):", data)
        choices = data.get("choices")
        if choices and isinstance(choices, list) and len(choices) > 0:
            message = choices[0].get("message")
            if message and isinstance(message, dict):
                transformed_text = message.get("content", "")
                # Rimozione di formattazioni indesiderate e sequenze '\\n\\n'
                transformed_text = transformed_text.replace("**", "")
                transformed_text = re.sub(r"$[^$]*$", "", transformed_text)
                transformed_text = re.sub(r"\*([^*]+)\*", r"\1", transformed_text)
                transformed_text = transformed_text.replace("\\n\\n", " ")
                return transformed_text.strip()
        st.warning("La risposta dell'API Groq non è conforme alle aspettative o risulta vuota.")
        st.json(data)
        return None
    except requests.exceptions.HTTPError as http_err:
        st.error("Errore HTTP durante la chiamata all'API Groq.")
        st.error(f"Codice di stato: {http_err.response.status_code}")
        try:
            error_details = http_err.response.json()
            st.error(f"Dettagli errore API: {error_details.get('error', {}).get('message', str(error_details))}")
        except ValueError:
            st.error(f"Dettagli errore API (testo): {http_err.response.text}")
        return None
    except requests.exceptions.Timeout:
        st.error(f"Timeout ({REQUEST_TIMEOUT}s) durante la chiamata all'API Groq. L'articolo potrebbe essere troppo lungo o l'API troppo lenta.")
        return None
    except requests.exceptions.RequestException as req_err:
        st.error(f"Errore di connessione durante la chiamata all'API Groq: {req_err}")
        return None
    except Exception as e:
        st.error("Errore imprevisto durante la trasformazione del testo.")
        st.error(f"Dettagli tecnici: {e}")
        return None

def generate_panel_html(title: str, content: str, icon_class: str) -> str:
    """
    Genera il codice HTML per un pannello del fumetto, comprensivo di titolo, contenuto e un'icona.
    """
    return f"""
    <div class="panel visible">
        <div class="panel-content">
            <div class="icon {icon_class}"></div>
            <h2>{title}</h2>
            <p>{content}</p>
        </div>
    </div>
    """

def display_comic_output(comic_text: str):
    """
    Divide il testo trasformato nei singoli pannelli, eliminando eventuali pannelli vuoti o composti unicamente da spazi e interruzioni.
    Viene quindi generato il codice HTML completo per visualizzare il fumetto nell'interfaccia utente.
    """
    # Suddivide il testo basandosi sulla presenza di doppie interruzioni di riga, eliminando pannelli inutili
    raw_panels = re.split(r'\n\s*\n', comic_text)
    panels_data = []
    for panel in raw_panels:
        if re.sub(r'[\n\s]', '', panel):
            panels_data.append(panel.strip())
    if not panels_data:
        st.warning("Il testo trasformato non contiene pannelli validi. Verrà mostrato il testo grezzo.")
        panels_data = [comic_text.strip()]
    panels_html_list = []
    for idx, panel_text in enumerate(panels_data):
        lines = panel_text.split("\n", 1)
        # Verifica se il testo contiene un titolo separato in base a criteri di lunghezza e punteggiatura
        if len(lines) > 1:
            potential_title = lines[0].strip()
            content_candidate = lines[1].strip()
            if potential_title and content_candidate and len(potential_title) < 70 and not potential_title.endswith(('.', '!', '?', ':', ';')):
                title = potential_title
                content = content_candidate
            else:
                title = "Titolo Non Specificato"
                content = panel_text
        else:
            title = "Titolo Non Specificato"
            content = panel_text
        if not content.strip():
            continue
        icon_class = random.choice(AVAILABLE_ICONS)
        panels_html_list.append(generate_panel_html(title, content, icon_class))
    if not panels_html_list:
        st.error("Non è stato possibile generare alcun pannello per il fumetto.")
        return
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
      <script>
        document.addEventListener('DOMContentLoaded', function() {{
            const panels = document.querySelectorAll('.panel');
            panels.forEach((panel, index) => {{
                setTimeout(() => {{
                    panel.classList.add('visible');
                }}, index * 100);
            }});
        }});
      </script>
    </body>
    </html>
    """
    components.html(full_html, height=1500, scrolling=True)

# --- INTERFACCIA UTENTE STREAMLIT ---
st.set_page_config(page_title="Articolo a Fumetti", layout="wide", initial_sidebar_state="collapsed")
st.title("🎨 Articolo a Fumetti ⚡")
st.markdown("""
Trasforma un articolo di notizie in un fumetto narrativo, semplice e divertente!
Incollare il link dell'articolo per avviare la trasformazione e ottenere titoli elaborati per ciascun pannello.
""")

if 'GROQ_API_KEY' not in st.session_state:
    st.session_state.GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")
if not st.session_state.GROQ_API_KEY:
    st.session_state.GROQ_API_KEY = st.text_input(
        "🔑 Inserisci la chiave API Groq:",
        type="password",
        help="La chiave API può essere ottenuta gratuitamente da console.groq.com"
    )

article_url = st.text_input(
    "🔗 Inserisci il link dell'articolo da trasformare:",
    placeholder="Es. https://www.ansa.it/sito/notizie/..."
)

if st.button("Trasforma in Fumetto!", type="primary", use_container_width=True, key="transform_button"):
    valid_input = True
    if not article_url:
        st.error("Il link non è stato inserito.")
        valid_input = False
    if not st.session_state.GROQ_API_KEY:
        st.error("La chiave API Groq è obbligatoria per procedere.")
        valid_input = False
    if article_url and not (article_url.startswith("http://") or article_url.startswith("https://")):
        st.error("Il link inserito non sembra valido. Verificare che inizi con http:// o https://")
        valid_input = False
    if valid_input:
        with st.spinner("Recupero l'articolo dal web... 📰"):
            article_text = get_article_content(article_url)
        if article_text:
            st.info(f"Articolo estratto ({len(article_text)} caratteri). Inizio trasformazione in formato fumettistico.")
            with st.spinner("Esecuzione della trasformazione con l'AI di Groq... 🗯️ (potrebbero volerci alcuni istanti)"):
                comic_text_output = transform_text_narrative(st.session_state.GROQ_API_KEY, article_text)
            if comic_text_output:
                st.success("Trasformazione completata. Ecco il fumetto generato!")
                display_comic_output(comic_text_output)
            else:
                st.error("Si è verificato un errore durante la trasformazione. Consultare i messaggi di debug per ulteriori informazioni.")
st.markdown("---")
st.markdown("Realizzato con AI, Streamlit, Newspaper3k e Groq. Font utilizzati: Comic Neue, Bangers. Icone: Emoji e simboli.")
