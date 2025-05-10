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

# Iniezione del CSS per lo stile fumetto
comic_css = """
/* Inserisci qui il tuo CSS personalizzato per lo stile fumetto */
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
"""

st.markdown(f"<style>{comic_css}</style>", unsafe_allow_html=True)
st.title("Articolo in Stile Fumetto con Groq API")

# Recupera la chiave API dai secrets, oppure la chiede in input
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
                # Dividi l'articolo in paragrafi non vuoti
                paragrafi = [p.strip() for p in article_text.split("\n") if p.strip()]
                for idx, paragrafo in enumerate(paragrafi):
                    panels_html += f"""
                    <div class="panel visible" style="--rotate: {(-5 + (idx % 3) * 5)}deg;">
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
