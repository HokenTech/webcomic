import os
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
    # Messaggio per trasformare il testo in uno stile fumettistico narrativo, informativo e coinvolgente.
    # Il testo trasformato deve essere suddiviso in pannelli in cui ciascun pannello contiene in prima linea
    # un titolo evocativo (senza numerazioni o simboli extra) seguito dal contenuto del pannello.
    user_message = (
        "Riscrivi il seguente articolo in formato fumettistico come se un narratore stesse raccontando la storia in maniera "
        "informativa e coinvolgente, destinata a un pubblico giovane. Suddividi il testo in numerosi pannelli, "
        "dove ogni pannello inizia con un titolo evocativo su una riga a parte, seguito dal contenuto del pannello. "
        "Non inserire numerazioni, simboli o markdown extra (ad esempio, non includere '**' o 'Pannello 1:'). "
        "Testo articolo:\n\n" + text
    )
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "user", "content": user_message}
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
            # Rimuovo eventuali markdown indesiderati
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

# Funzione per estrarre titolo ed eventuale parola evocativa dal pannello
def parse_panel(panel_text):
    # Rimuovo spazi e eventuali markdown indesiderati
    panel_text = panel_text.strip().replace("**", "")
    title = ""
    content = panel_text
    # Se esiste una rottura di riga, prendo la prima linea come titolo
    if "\n" in panel_text:
        parts = panel_text.split("\n", 1)
        title_candidate = parts[0].strip()
        # Se il titolo candidate è breve e non finisce con un segno di punteggiatura
        if title_candidate and len(title_candidate.split()) < 10:
            title = title_candidate
            content = parts[1].strip()
    # Se non abbiamo trovato titolo, cerco un separatore ":"
    if not title and ":" in panel_text:
        parts = panel_text.split(":", 1)
        title_candidate = parts[0].strip()
        if title_candidate and len(title_candidate.split()) < 10:
            title = title_candidate
            content = parts[1].strip()
    # Se ancora non c'è titolo, uso le prime 5 parole come titolo
    if not title:
        words = panel_text.split()
        if len(words) >= 5:
            title = " ".join(words[:5])
            content = " ".join(words[5:])
        else:
            title = panel_text
            content = ""
    # Per la parola evocativa, prendo la prima parola del contenuto se disponibile
    bubble_word = ""
    content_words = content.split()
    if content_words:
        bubble_word = content_words[0].strip(".,;:!?'\"")
    else:
        bubble_word = title.split()[0].strip(".,;:!?'\"")
    return title, content, bubble_word

# CSS fornito dall'utente per lo stile fumetto
comic_css = """
/* comic-style.css */

/* Aggiungi uno stile base per il body quando il fumetto è visibile */
body:has(.comic-container) {
    font-family: 'Comic Neue', cursive;
    background: linear-gradient(135deg, #f0f0f0, #e0f0f0); /* Sfondo chiaro per il fumetto */
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
    transform: translateY(20px) rotate(0deg);
    transition: opacity 0.8s ease-out, transform 0.8s ease-out;
    z-index: 0;
}

.panel.visible {
    opacity: 1;
    transform: translateY(0) rotate(var(--rotate, 0deg));
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
    z-index: 6;
    margin-bottom: 10px;
}

.panel p {
    margin-top: 10px;
    margin-bottom: 0;
    line-height: 1.5;
    position: relative;
    z-index: 6;
}

.speech-bubble {
    position: absolute;
    background-color: #fff;
    border: 3px solid #333;
    border-radius: 10px;
    padding: 8px 12px;
    max-width: 50%;
    font-size: 1em;
    line-height: 1.3;
    filter: drop-shadow(3px 3px 5px rgba(0,0,0,0.2));
    animation: bounce 0.5s ease-in-out alternate infinite;
    z-index: 5;
    top: 70px;
    right: 20px;
    left: auto;
    bottom: auto;
}

.speech-bubble::after {
    content: '';
    position: absolute;
    top: 10px;
    left: -15px;
    right: auto;
    bottom: auto;
    width: 0;
    height: 0;
    border-top: 15px solid transparent;
    border-bottom: 15px solid transparent;
    border-right: 15px solid #fff;
    border-left: none;
    filter: drop-shadow(-1px 1px 2px rgba(0,0,0,0.1));
}

.speech-bubble::before {
    content: '';
    position: absolute;
    top: 8px;
    left: -18px;
    right: auto;
    bottom: auto;
    width: 0;
    height: 0;
    border-top: 17px solid transparent;
    border-bottom: 17px solid transparent;
    border-right: 17px solid #333;
    border-left: none;
    z-index: -1;
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
    margin: 10px auto;
    font-size: 3em;
    text-align: center;
    position: relative;
    z-index: 6;
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

@keyframes bounce {
    0% { transform: translateY(0); }
    100% { transform: translateY(-5px); }
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .panel {
        width: 100%;
        min-width: auto;
    }
    .speech-bubble {
         top: 60px;
         right: 10px;
         max-width: 60%;
    }
    .speech-bubble::after, .speech-bubble::before {
         top: 8px;
    }
    .speech-bubble::before {
         top: 6px;
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
    .speech-bubble {
         font-size: 0.9em;
         padding: 6px 10px;
         top: 50px;
         right: 5px;
         max-width: 75%;
    }
    .speech-bubble::after, .speech-bubble::before {
         top: 6px;
    }
    .speech-bubble::before {
         top: 4px;
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

/* Stile per il body quando la pagina originale è nascosta */
body[style*="display: none"] {
    display: none !important;
}
"""

st.title("Comic App: Trasforma l'Articolo in un Fumetto Narrativo")

# Recupera la chiave API dai secrets o la richiede in input
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
                # Suddivide il testo trasformato in pannelli basandosi su doppie interruzioni di linea
                panels = [panel.strip() for panel in comic_text.split("\n\n") if panel.strip()]
                # Se la suddivisione non produce abbastanza pannelli, suddivide per singole linee
                if len(panels) < 5:
                    panels = [line.strip() for line in comic_text.split("\n") if line.strip()]
                
                panels_html = ""
                # Per ogni pannello, estraggo il titolo, il contenuto e una parola evocativa
                for panel in panels:
                    titolo, contenuto, bubble_word = parse_panel(panel)
                    panels_html += f"""
                    <div class="panel visible">
                        <div class="panel-content">
                            <div class="icon icon-star"></div>
                            <h2 class="comic-header">{titolo}</h2>
                            <p>{contenuto}</p>
                            <div class="speech-bubble">{bubble_word}</div>
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
