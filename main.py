import streamlit as st
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
        return None

# Funzione per ottenere il sommario usando l'API di Groq
def summarize_text(text, api_key):
    api_url = "https://api.tuodominio.com/summarize"  # Sostituisci con l'endpoint corretto
    headers = {"Authorization": f"Bearer {api_key}"}  # Usa la chiave API fornita dall'utente
    payload = {"text": text}
    
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        summary = response.json().get("summary", "Nessun sommario disponibile")
        return summary
    except Exception as e:
        st.error("Errore durante la chiamata all'API per il sommario.")
        return None

# Iniezione del CSS per lo stile fumetto
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
    width: 0;
    height: 0;
    border-top: 15px solid transparent;
    border-bottom: 15px solid transparent;
    border-right: 15px solid #fff;
    filter: drop-shadow(-1px 1px 2px rgba(0,0,0,0.1));
}

.speech-bubble::before {
    content: '';
    position: absolute;
    top: 8px;
    left: -18px;
    width: 0;
    height: 0;
    border-top: 17px solid transparent;
    border-bottom: 17px solid transparent;
    border-right: 17px solid #333;
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

body[style*="display: none"] {
    display: none !important;
}
"""

# Inietta il CSS nella pagina
st.markdown(f"<style>{comic_css}</style>", unsafe_allow_html=True)

# Titolo dell'applicazione
st.title("Articolo in Stile Fumetto con Groq API")

# Input per la chiave API, da usare in Streamlit Cloud
groq_api_key = st.text_input("Inserisci la tua chiave API per Groq:", type="password")

# Inserimento del link dell’articolo
link = st.text_input("Inserisci il link dell'articolo:")

if st.button("Processa"):
    if not link:
        st.error("Inserisci un link valido!")
    elif not groq_api_key:
        st.error("Inserisci la tua chiave API per procedere!")
    else:
        st.info("Estrazione dell'articolo in corso...")
        article_text = get_article_content(link)
        if article_text is not None:
            st.info("Richiamo API per il sommario...")
            summary = summarize_text(article_text, groq_api_key)
            if summary:
                st.markdown("### Sommario")
                st.write(summary)
                
                st.markdown("### Articolo in Stile Fumetto")
                # Creiamo il markup HTML per visualizzare l'articolo in stile fumetto.
                panels_html = ""
                paragrafi = [p.strip() for p in article_text.split("\n") if p.strip()]
                for idx, paragrafo in enumerate(paragrafi):
                    panels_html += f"""
                    <div class="panel visible" style="--rotate: {(-5 + idx % 3 * 5 )}deg;">
                        <div class="panel-content">
                            <h2 class="comic-header">Pannello {idx+1}</h2>
                            <p>{paragrafo}</p>
                        </div>
                    </div>
                    """
                comic_html = f"""
                <div class="comic-container">
                    {panels_html}
                </div>
                """
                st.markdown(comic_html, unsafe_allow_html=True)
            else:
                st.error("Impossibile ottenere il sommario.")
