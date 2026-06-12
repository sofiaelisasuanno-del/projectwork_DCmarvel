import streamlit as st
import joblib
import json
import numpy as np
import requests
import re

# ── FUNZIONE IMMAGINE WIKIPEDIA ──────────────────────────────────────
def get_wiki_image(character_name):
    clean_name = re.sub(r'\s*\(.*?\)', '', character_name).strip()
    headers = {"User-Agent": "DCMarvelQuiz/1.0 (educational project)"}

    for query in [clean_name, clean_name + " comics", character_name]:
        try:
            # Cerca il titolo della pagina
            search_params = {
                "action": "opensearch",
                "search": query,
                "limit": 1,
                "format": "json"
            }
            r = requests.get("https://en.wikipedia.org/w/api.php",
                           params=search_params, headers=headers, timeout=6)
            results = r.json()
            if not results[1]:
                continue
            title = results[1][0]

            # Prendi l'immagine dalla pagina trovata
            img_params = {
                "action": "query",
                "titles": title,
                "prop": "pageimages",
                "format": "json",
                "pithumbsize": 400,
            }
            r2 = requests.get("https://en.wikipedia.org/w/api.php",
                            params=img_params, headers=headers, timeout=6)
            data = r2.json()
            pages = data["query"]["pages"]
            page = next(iter(pages.values()))
            if "thumbnail" in page:
                return page["thumbnail"]["source"]
        except Exception:
            continue
    return None

# ── CARICA MODELLO ───────────────────────────────────────────────────
model = joblib.load("model.pkl")
encoders = joblib.load("encoders.pkl")
with open("options.json") as f:
    options = json.load(f)

# ── CONFIGURAZIONE PAGINA ────────────────────────────────────────────
st.set_page_config(
    page_title="Quale personaggio DC/Marvel sei?",
    page_icon="🦸",
    layout="centered"
)

# ── CSS TEMA FUMETTO ─────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bangers&family=Comic+Neue:wght@400;700&display=swap');

.stApp {
    background: linear-gradient(135deg, #0a0a1a 0%, #1a0a2e 50%, #0a1a2e 100%);
    color: white;
}
h1 {
    font-family: 'Bangers', cursive !important;
    font-size: 3rem !important;
    letter-spacing: 3px !important;
    text-align: center;
    background: linear-gradient(90deg, #ff2d2d, #4444ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
h2, h3 {
    font-family: 'Bangers', cursive !important;
    letter-spacing: 2px !important;
    color: #ffcc00 !important;
}
.question-card {
    background: rgba(255,255,255,0.05);
    border: 2px solid rgba(255, 45, 45, 0.4);
    border-radius: 16px;
    padding: 2rem;
    margin: 1rem 0;
    box-shadow: 0 0 20px rgba(255, 45, 45, 0.2);
}
.question-text {
    font-family: 'Bangers', cursive;
    font-size: 1.8rem;
    color: #ffffff;
    letter-spacing: 2px;
    margin-bottom: 1rem;
}
.stButton > button {
    background: linear-gradient(90deg, #ff2d2d, #cc0000) !important;
    color: white !important;
    font-family: 'Bangers', cursive !important;
    font-size: 1.3rem !important;
    letter-spacing: 2px !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6rem 2rem !important;
    box-shadow: 0 4px 15px rgba(255, 45, 45, 0.4) !important;
}
.stRadio > label { color: white !important; }
.stRadio div[role="radiogroup"] label p { color: white !important; }
.stRadio div[role="radiogroup"] label { color: white !important; }
.stProgress > div > div {
    background: linear-gradient(90deg, #ff2d2d, #4444ff) !important;
}
.result-banner {
    background: linear-gradient(135deg, #1a0a2e, #0a1a3e);
    border: 3px solid #ffcc00;
    border-radius: 20px;
    padding: 2rem;
    text-align: center;
    box-shadow: 0 0 30px rgba(255, 204, 0, 0.3);
}
.result-name {
    font-family: 'Bangers', cursive;
    font-size: 2.8rem;
    color: #ffcc00;
    letter-spacing: 4px;
}
.character-img {
    border-radius: 16px;
    border: 3px solid #ffcc00;
    box-shadow: 0 0 25px rgba(255, 204, 0, 0.4);
    max-width: 280px;
    margin: 1rem auto;
    display: block;
}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ── MAPPE DOMANDE ────────────────────────────────────────────────────
domande = [
    {
        "testo": "⚖️ Come ti descriveresti moralmente?",
        "chiave": "ALIGN",
        "opzioni": {
            "Sono un eroe, difendo i più deboli 🦸": "Good Characters",
            "Sono un villain, faccio le mie regole 😈": "Bad Characters",
            "Dipende dalla situazione... 🤷": "Neutral Characters",
        }
    },
    {
        "testo": "👤 Qual è il tuo genere?",
        "chiave": "SEX",
        "opzioni": {
            "Maschio 👦": "Male Characters",
            "Femmina 👧": "Female Characters",
            "Agender 🌐": "Agender Characters",
            "Genderless 🌀": "Genderless Characters",
            "Genderfluid 🌈": "Genderfluid Characters",
        }
    },
    {
        "testo": "👁️ Di che colore sono i tuoi occhi?",
        "chiave": "EYE",
        "opzioni": {
            "Occhi blu 🔵": "Blue Eyes",
            "Occhi marroni 🟤": "Brown Eyes",
            "Occhi neri ⚫": "Black Eyes",
            "Occhi verdi 🟢": "Green Eyes",
            "Occhi rossi 🔴": "Red Eyes",
            "Occhi gialli 🟡": "Yellow Eyes",
            "Occhi bianchi ⚪": "White Eyes",
            "Occhi grigi 🩶": "Grey Eyes",
            "Occhi nocciola": "Hazel Eyes",
            "Altro / variabili ✨": "Variable Eyes",
        }
    },
    {
        "testo": "💇 Di che colore sono i tuoi capelli?",
        "chiave": "HAIR",
        "opzioni": {
            "Capelli neri 🖤": "Black Hair",
            "Capelli castani 🟤": "Brown Hair",
            "Capelli biondi 💛": "Blond Hair",
            "Capelli rossi 🔴": "Red Hair",
            "Capelli bianchi / grigi 🤍": "White Hair",
            "Capelli grigi": "Grey Hair",
            "Calvo / senza capelli": "Bald",
            "Capelli colorati (blu, verde, viola...) 🌈": "Blue Hair",
            "Altro": "Variable Hair",
        }
    },
    {
        "testo": "🎭 Come gestisci la tua identità?",
        "chiave": "ID",
        "opzioni": {
            "Tengo tutto segreto, nessuno sa chi sono 🤫": "Secret Identity",
            "Sono trasparente, tutti sanno chi sono 📢": "Public Identity",
            "Non ho un alter ego, sono sempre me stesso": "No Dual Identity",
            "Le autorità mi conoscono, ma non il pubblico 🚔": "Known to Authorities Identity",
        }
    },
    {
        "testo": "💓 Sei ancora attivo e in vita?",
        "chiave": "ALIVE",
        "opzioni": {
            "Sì, sono vivo e vegeto 💪": "Living Characters",
            "Ho vissuto tempi migliori... ☠️": "Deceased Characters",
        }
    },
    {
        "testo": "🌍 Con quale universo ti identifichi?",
        "chiave": "publisher",
        "opzioni": {
            "Marvel 🕷️ (Spider-Man, Iron Man, X-Men...)": "Marvel",
            "DC 🦇 (Batman, Superman, Wonder Woman...)": "DC",
        }
    },
    {
        "testo": "🌟 Quanto sei famoso / popolare?",
        "chiave": "POPULARITY",
        "opzioni": {
            "Poche persone mi conoscono davvero 🔍": "Bassa",
            "Ho un buon giro di amici e conoscenti 👥": "Media",
            "Sono abbastanza famoso nel mio ambiente 🌟": "Alta",
            "Sono una leggenda, tutti mi conoscono 🏆": "Leggenda",
        }
    },
    {
        "testo": "🔄 Hai mai cambiato lato?",
        "chiave": None,
        "opzioni": {
            "No, sono sempre rimasto coerente ✊": None,
            "Sì, ho cambiato strada 🔄": None,
        }
    },
    {
        "testo": "⚡ Come risolvi i conflitti?",
        "chiave": None,
        "opzioni": {
            "Con la forza e l'azione diretta 💥": None,
            "Con la strategia e l'astuzia 🧩": None,
            "Cerco sempre una via di mezzo 🤝": None,
        }
    },
]

TOTALE = len(domande)

# ── SESSION STATE ────────────────────────────────────────────────────
if "step" not in st.session_state:
    st.session_state.step = 0
if "risposte" not in st.session_state:
    st.session_state.risposte = {}
if "risultato" not in st.session_state:
    st.session_state.risultato = None

# ── HEADER ───────────────────────────────────────────────────────────
st.markdown("<h1>🦸 QUALE EROE SEI? 🦹</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#aaaacc; font-size:1.1rem;'>Scopri il tuo alter ego DC/Marvel</p>", unsafe_allow_html=True)

# ── QUIZ ─────────────────────────────────────────────────────────────
if st.session_state.risultato is None:

    step = st.session_state.step
    progresso = step / TOTALE
    st.progress(progresso)
    st.markdown(f"<p style='text-align:center; color:#aaaacc;'>Domanda {step + 1} di {TOTALE}</p>", unsafe_allow_html=True)

    if step < TOTALE:
        domanda = domande[step]

        st.markdown(f"""
        <div class='question-card'>
            <div class='question-text'>{domanda['testo']}</div>
        </div>
        """, unsafe_allow_html=True)

        scelta = st.radio(
            "",
            list(domanda["opzioni"].keys()),
            key=f"q_{step}",
            label_visibility="collapsed"
        )

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("AVANTI ➡️" if step < TOTALE - 1 else "🔍 SCOPRI CHI SEI!", use_container_width=True):
                if domanda["chiave"]:
                    st.session_state.risposte[domanda["chiave"]] = domanda["opzioni"][scelta]
                st.session_state.step += 1

                if st.session_state.step == TOTALE:
                    feature_cols = ["ALIGN", "SEX", "EYE", "HAIR", "ID", "ALIVE", "publisher", "POPULARITY"]
                    encoded = []
                    for col in feature_cols:
                        le = encoders[col]
                        val = st.session_state.risposte.get(col, le.classes_[0])
                        if val in le.classes_:
                            encoded.append(le.transform([val])[0])
                        else:
                            encoded.append(0)

                    X_input = np.array(encoded).reshape(1, -1)
                    prediction = model.predict(X_input)[0]
                    st.session_state.risultato = prediction

                st.rerun()

# ── RISULTATO ────────────────────────────────────────────────────────
else:
    prediction = st.session_state.risultato

    st.progress(1.0)
    st.balloons()

    st.markdown(f"""
    <div class='result-banner'>
        <p style='color:#aaaacc; font-size:1.2rem; font-family: Bangers, cursive; letter-spacing:2px;'>IL TUO ALTER EGO È...</p>
        <div class='result-name'>✨ {prediction} ✨</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Cerca immagine Wikipedia
    with st.spinner("🔍 Cerco l'immagine del personaggio..."):
        img_url = get_wiki_image(prediction)

    if img_url:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f"<img src='{img_url}' class='character-img'>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='text-align:center; color:#aaaacc;'>🖼️ Immagine non disponibile per questo personaggio</p>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 RIGIOCA!", use_container_width=True):
            st.session_state.step = 0
            st.session_state.risposte = {}
            st.session_state.risultato = None
            st.rerun()