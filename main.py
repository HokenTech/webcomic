import os
import random
import streamlit as st
import streamlit.components.v1 as components
import requests
from newspaper import Article

# Funzione per estrarre il contenuto dell'articolo da un URL
def get_article_content(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        st.error("Errore durante l'estrazione dell'articolo.")
        st.error(e)
        return None

# Funzione per trasformare il testo in un fumetto narrativo in stile articolo informativo
def transform_text_narrative(api_key, text):
    api_url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    prompt = (
        "Riscrivi il seguente articolo in formato fumettistico, come se un narratore stesse raccontando la storia in maniera "
        "informativa e coinvolgente, destinata a un pubblico giovane. Suddividi il testo in numerosi pannelli. Per ciascun pannello "
        "non includere un titolo all'inizio del paragrafo, perché il titolo verrà assegnato in seguito in modo unico. "
        "Rendi il testo del pannello completo e coerente. Non inserire numerazioni, simboli o markdown extra. "
        "Testo articolo:\n\n" + text
    )
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=40)
        response.raise_for_status()
        data = response.json()
        st.write("Risposta API Groq (debug):", data)
        choices = data.get("choices", [])
        if choices and "message" in choices[0]:
            transformed_text = choices[0]["message"].get("content", "")
            transformed_text = transformed_text.replace("**", "")
            return transformed_text
        else:
            return None
    except Exception as e:
        st.error("Errore durante la trasformazione del testo dall'API Groq.")
        if hasattr(e, 'response') and e.response is not None:
            st.error("Dettagli errore API: " + e.response.text)
        st.error(e)
        return None

# Definiamo una lista di titoli evocativi da assegnare in modo univoco ad ogni pannello
default_titles = [
    "Avventura Inizia", "Scoperta Inedita", "Cuore della Narrazione", 
    "Intreccio Emozionante", "Finale Inatteso", "Svolta Cruciale", 
    "Momento Rivelatore", "Epilogo Indimenticabile"
]

# Lista di icone disponibili, per una maggiore varietà ad ogni pannello
available_icons = [
    "icon-globe", "icon-ai", "icon-code", "icon-trophy", "icon-star",
    "icon-fire", "icon-lightbulb", "icon-music", "icon-book", "icon-rocket"
]

# CSS per lo stile fumettistico, senza animazioni aggiuntive
comic_css = """
/* comic-style.css */
body:has(.comic-container) {
    font-family: 'Comic Neue', cursive;
    background: linear-gradient(135deg, #f0f0f0, #e0f0f0);
    margin: 0;
    padding: 20px;
    color: #333;
    overflow-x: hidden;
}

.comic-container {
    display: flex;
    flex-wrap: wrap;
    gap: 30px;
    justify-content: center;
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    background-color: #fff;
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
    border-radius: 15px;
    box-sizing: border-box;
}

.panel {
    background-color: #fff;
    border: 5px solid #333;
    box-shadow: 5px 5px 15px rgba(0, 0, 0, 0.3);
    padding: 20px;
    border-radius: 10px;
    position: relative;
    overflow: hidden;
    width: calc(50% - 30px);
    min-width: 300px;
    box-sizing: border-box;
    opacity: 0;
    transform: translateY(20px);
    transition: opacity 0.8s ease-out, transform 0.8s ease-out;
    z-index: 0;
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
    text-shadow: 2px 2px #333;
    font-size: 2em;
    line-height: 1.1;
    position: relative;
    z-index: 1;
    margin-bottom: 10px;
}

.panel p {
    margin-top: 10px;
    margin-bottom: 0;
    line-height: 1.5;
    position: relative;
    z-index: 1;
    text-align: justify;
}

.panel-content {
    position: relative;
    z-index: 1;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    align-items: center;
    padding: 0 10px;
}

/* --- Visuals/Icons in Panels --- */
.icon {
    display: block;
    margin: 10px auto 0 auto;
    font-size: 3em;
    text-align: center;
    position: relative;
    z-index: 2;
    flex-shrink: 0;
}

.icon-trophy::before { content: '🏆'; }
.icon-globe::before { content: '🌍'; }
.icon-map::before { content: '📍'; }
.icon-blockchain::before { content: '🔗'; }
.icon-gameboy::before { content: '👾'; }
.icon-machine::before { content: '📦'; font-size: 2.5em; }
.icon-leaf::before { content: '🌿'; }
.icon-star::before { content: '⭐'; }
.icon-team::before { content: '👨‍💻👩‍💻'; }
.icon-ai::before { content: '🤖'; }
.icon-code::before { content: '💻'; }
.icon-cloud::before { content: '☁️'; }
.icon-fire::before { content: '🔥'; }
.icon-lightbulb::before { content: '💡'; }
.icon-music::before { content: '🎵'; }
.icon-book::before { content: '📚'; }
.icon-rocket::before { content: '🚀'; }

.highlight {
    font-weight: bold;
    color: #1a73e8;
    font-family: 'Bangers', cursive;
}

.highlight-red {
    font-weight: bold;
    color: #e53935;
    font-family: 'Bangers', cursive;
}

@media (max-width: 768px) {
    .panel {
        width: 100%;
        min-width: auto;
    }
    .icon {
         font-size: 2em;
    }
    body:has(.comic-container) {
         padding: 10px;
    }
}

@media (max-width: 480px) {
     .panel h2 {
        font-size: 1.5em;
    }
    .icon {
         font-size: 2em;
    }
    body:has(.comic-container) {
         padding: 10px;
    }
}

.comic-header {
    text-align: center;
    margin-bottom: 30px;
    font-family: 'Bangers', cursive;
    color: #e53935;
    text-shadow: 3px 3px #333;
    font-size: 3em;
}

@media (max-width: 480px) {
    .comic-header {
        font-size: 2em;
        margin-bottom: 20px;
    }
}

body[style*="display: none"] {
    display: none !important;
}
"""

st.title("Comic App: Trasforma l'Articolo in un Fumetto Narrativo")

groq_api_key = st.secrets.get("GROQ_API_KEY", None)
if not groq_api_key:
    groq_api_key = st.text_input("Inserisci la tua chiave API per Groq:", type="password")

link = st.text_input("Inserisci il link dell'articolo:")

if st.button("Processa"):
    if not link:
        st.error("Inserisci un link valido!")
    elif not groq_api_key:
        st.error("Inserisci la tua chiave API per procedere!")
    else:
        with st.spinner("Estrazione dell'articolo in corso..."):
            article_text = get_article_content(link)
        if article_text is not None:
            with st.spinner("Trasformazione del testo in fumetto narrativo..."):
                comic_text = transform_text_narrative(groq_api_key, article_text)
            if comic_text:
                # Suddividiamo il testo trasformato in pannelli basandoci su doppie interruzioni di linea
                panels = [panel.strip() for panel in comic_text.split("\n\n") if panel.strip()]
                if len(panels) < 5:
                    panels = [line.strip() for line in comic_text.split("\n") if line.strip()]
                
                panels_html = ""
                for idx, panel in enumerate(panels):
                    # Assegniamo un titolo univoco da una lista predefinita
                    title = default_titles[idx % len(default_titles)]
                    content = panel  # Il contenuto del pannello è l'intero testo
                    # Selezioniamo un'icona casuale per aumentare la varietà
                    icon_class = random.choice(available_icons)
                    panels_html += f"""
                    <div class="panel visible">
                        <div class="panel-content">
                            <div class="icon {icon_class}"></div>
                            <h2 class="comic-header">{title}</h2>
                            <p>{content}</p>
                        </div>
                    </div>
                    """
                
                full_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                  <meta charset="utf-8">
                  <title>Articolo a Fumetti Narrativo</title>
                  <style>
                  {comic_css}
                  </style>
                </head>
                <body>
                  <div class="comic-container">
                      {panels_html}
                  </div>
                </body>
                </html>
                """
                components.html(full_html, height=900, scrolling=True)
            else:
                st.error("Impossibile trasformare il testo in un fumetto narrativo.")
