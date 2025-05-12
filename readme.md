# WebComic

Questo documento descrive in dettaglio come ricreare da zero il progetto WebComic, un'applicazione che trasforma articoli di notizie in fumetti narrativi. La guida illustra tutti i passaggi, dalla configurazione dell'ambiente alla distribuzione dell'app, includendo informazioni su dipendenze, configurazioni e flusso dell'applicazione.

---

## Indice

1. [Introduzione](#introduzione)
2. [Caratteristiche](#caratteristiche)
3. [Requisiti](#requisiti)
4. [Installazione e Configurazione](#installazione-e-configurazione)
5. [Struttura del Progetto](#struttura-del-progetto)
6. [Utilizzo](#utilizzo)
7. [Debug e Personalizzazioni](#debug-e-personalizzazioni)
8. [Riferimenti e Risorse](#riferimenti-e-risorse)

---

## Introduzione

La **Webcomic** è un'applicazione web sviluppata in Python che sfrutta Streamlit per creare un'interfaccia utente interattiva. L'app trasforma articoli di notizie, recuperati da un URL, in fumetti narrativi. Le tecnologie principali utilizzate sono:

- **Newspaper3k** per il download e l'analisi degli articoli.
- **API Groq** per trasformare il testo in un formato narrativo suddiviso in pannelli, con titoli elaborati per ogni paragrafo.
- **Streamlit Components** per visualizzare i pannelli HTML personalizzati che compongono il fumetto.

---

## Caratteristiche

- **Estrazione automatica dei contenuti:** Scarica gli articoli da un URL fornito.
- **Trasformazione AI:** Utilizzando l'API Groq, il testo viene trasformato in un formato narrativo suddiviso in pannelli con titoli espliciti.
- **Interfaccia dinamica:** Visualizzazione interattiva dei pannelli con animazioni e stili personalizzati.
- **Debug integrato:** Visualizzazione delle informazioni di debug relative alla chiamata API per monitorare i parametri e il risultato.

---

## Requisiti

- **Python 3.8+**
- **Streamlit**
- **Newspaper3k**
- **Requests**
- **Librerie standard:** os, re, random, typing
- **API Groq:** È necessario un account su [console.groq.com](https://console.groq.com) per ottenere una chiave API.

---

## Installazione e Configurazione

### 1. Creare un Ambiente Virtuale

Eseguire nel terminale:

    python3 -m venv venv
    source venv/bin/activate  # Su Windows: venv\Scripts\activate

### 2. Installare le Dipendenze

Installare le librerie necessarie:

    pip install streamlit newspaper3k requests

### 3. Configurare la Chiave API Groq

Per utilizzare l'API Groq, è necessario configurare la chiave API. Due opzioni:

- **File dei Segreti (per piattaforme come Streamlit Sharing):**  
  Creare un file `secrets.toml` con il seguente contenuto:

      GROQ_API_KEY="la_tua_chiave_api"

- **Inserimento Manuale:**  
  Se la chiave non è configurata nei segreti, l'app chiederà di inserirla tramite l'interfaccia utente.

---

## Struttura del Progetto

Organizzare la repo in questo modo:

    webcomic/
    ├── app.py           # Codice principale dell'applicazione Streamlit
    ├── README.md        # Guida dettagliata per configurare e utilizzare il progetto
    ├── requirements.txt # Elenco delle dipendenze Python (opzionale)
    └── secrets.toml     # File di configurazione per la chiave API (opzionale)

- **app.py**  
  Contiene il codice dell'applicazione, tra cui l'estrazione degli articoli, la chiamata all'API Groq, la generazione dei pannelli HTML e l'interfaccia utente Streamlit.

- **requirements.txt**  
  File opzionale creato eseguendo:

      pip freeze > requirements.txt

- **secrets.toml**  
  Utilizzato per gestire le chiavi segrete, utile per la distribuzione su piattaforme che supportano la gestione dei segreti.

---

## Utilizzo

1. **Avviare l'Applicazione**  
   Dalla radice del progetto, eseguire:

       streamlit run app.py

2. **Inserire l'URL dell'Articolo**  
   Utilizzare l'interfaccia per inserire un URL valido (inizia con `http://` o `https://`) dell'articolo da trasformare.

3. **Fornire la Chiave API**  
   Se non impostata nei segreti, verrà richiesto di inserire la chiave API Groq.

4. **Avviare la Trasformazione**  
   Cliccare sul pulsante "Trasforma in Fumetto!". L'app effettuerà le seguenti operazioni:
   - Scarica l'articolo utilizzando Newspaper3k.
   - Trasforma il testo tramite l'API Groq, creando titoli espliciti per ogni paragrafo.
   - Visualizza il fumetto in pannelli HTML personalizzati, con animazioni ed icone.

5. **Debug e Controllo**  
   Durante il processo, vengono mostrate informazioni di debug relative alla chiamata API per controllare i parametri e il risultato.

---

## Debug e Personalizzazioni

- **Debug del Modello:**  
  Le risposte dell'API Groq con i relativi parametri vengono mostrate nel debug sull'interfaccia Streamlit.

- **Personalizzazione dei Titoli:**  
  Il prompt inviato all'API include istruzioni specifiche per elaborare titoli per ogni paragrafo. È possibile modificare il prompt nel file `app.py` per ottenere il comportamento desiderato.

- **Modifica del CSS:**  
  Il blocco `COMIC_CSS` nel file `app.py` può essere modificato per cambiare lo stile dei pannelli, inclusi font, colori e animazioni.

---

## Riferimenti e Risorse

- **Streamlit:** [https://streamlit.io](https://streamlit.io)
- **Newspaper3k:** [https://github.com/codelucas/newspaper](https://github.com/codelucas/newspaper)
- **API Groq:** [https://console.groq.com](https://console.groq.com)
- **Documentazione Python:** [https://docs.python.org/3/](https://docs.python.org/3/)

---

## Conclusioni

Questa guida fornisce una panoramica completa per ricreare e personalizzare la **WebComic**. Seguendo i passaggi descritti, chiunque potrà configurare l'ambiente di sviluppo, avviare l'applicazione e sfruttare le funzionalità offerte dall'integrazione di Newspaper3k, l'API Groq e Streamlit. Le sezioni dedicate al debug e alle personalizzazioni consentono di adattare l'applicazione alle proprie esigenze e di estenderne le funzionalità per ulteriori evoluzioni.

Buon divertimento con il vostro progetto!

---
