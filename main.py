import os
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
        st.error(e)
        return None

# Funzione per ottenere il sommario utilizzando l'API Chat di Groq
def summarize_text_groq(text, api_key):
    api_url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    # Costruiamo il messaggio per il sommario
    user_message = (
        "Per favore, riassumi il seguente articolo in poche frasi concise:\n\n" + text
    )
    payload = {
        "model": "llama-3.3-70b-versatile",  # Modifica il modello se necessario
        "messages": [
            {"role": "user", "content": user_message}
        ]
    }
    
    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        # Debug (opzionale): visualizzare la risposta completa per il debug
        st.write("Risposta API Groq (debug):", data)
        # Estrarre il sommario dalla risposta
        choices = data.get("choices", [])
        if choices and "message" in choices[0]:
            summary = choices[0]["message"].get("content", "Nessun sommario disponibile")
            return summary
        else:
            return None
    except Exception as e:
        st.error("Errore durante la chiamata all'API per il sommario.")
        if hasattr(e, 'response') and e.response is not None:
            st.error("Dettagli errore API: " + e.response.text)
        st.error(e)
        return None

# CSS migliorato per il layout in stile fumetto
comic_css = """
/* Stile di base per il corpo */
body {
    background: #f2f2f2;
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
}

/* Contenitore fumetto con layout a griglia responsiva */
.comic-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 20px;
    padding: 20px;
    max-width: 1200px;
    margin: 20px auto;
}

/* Stile dei pannelli del fumetto */
.panel {
    background-color: #fff;
    border: 3px solid #000;
    border-radius: 10px;
    padding: 20px;
    position: relative;
    box-shadow: 5px 5px 0 rgba(0,0,0,0.1);
    transition: transform 0.3s ease;
}

/* Effetto alternato di rotazione per i pannelli */
.panel:nth-child(odd) {
    transform: rotate(-2deg);
}
.panel:nth-child(even) {
    transform: rotate(2deg);
}

/* Titolo e paragrafo del pannello */
.panel h2 {
    font-family: 'Bangers', cursive;
    font-size: 1.8em;
    color: #e53935;
    margin-top: 0;
    text-align: center;
}
.panel p {
    font-size: 1.1em;
    line-height: 1.5;
    margin: 10px 0;
}

/* Aggiunta di una pseudo-bubble per dare effetto fumetto */
.panel::before {
    content: "";
    position: absolute;
    bottom: -20px;
    left: 20px;
    width: 0;
    height: 0;
    border: 20px solid transparent;
    border-top-color: #fff;
    z-index: -1;
}
"""

st.markdown(f"<style>{comic_css}</style>", unsafe_allow_html=True)
st.title("Articolo in Stile Fumetto con Groq API")

# Recupera la chiave API dai secrets o la chiede in input
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
            with st.spinner("Richiamo API Groq per il sommario..."):
                summary = summarize_text_groq(article_text, groq_api_key)
            if summary:
                st.markdown("### Sommario")
                st.write(summary)
                st.markdown("### Articolo in Stile Fumetto")
                
                panels_html = ""
                # Divide l'articolo in paragrafi non vuoti e li incapsula nei pannelli
                paragrafi = [p.strip() for p in article_text.split("\n") if p.strip()]
                for idx, paragrafo in enumerate(paragrafi):
                    panels_html += f"""
                    <div class="panel">
                        <h2>Pannello {idx+1}</h2>
                        <p>{paragrafo}</p>
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
