import streamlit as st
import json
import random
import math
import base64
import os

st.set_page_config(page_title="Trening OWE", layout="wide", page_icon="📈")

# --- FUNKCJE POMOCNICZE UI ---
def dodaj_tlo_z_pliku(plik_tla):
    if os.path.exists(plik_tla):
        with open(plik_tla, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url(data:image/{"png"};base64,{encoded_string});
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

# Zaawansowany CSS dla przycisków, paneli i czytelności
# Zaawansowany CSS dla przycisków, paneli i czytelności (Wersja RWD - Mobile Friendly)
st.markdown("""
    <style>
    /* Ukrycie paska top Streamlita */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Globalny kolor tekstu na czarny dla czytelności na białym tle */
    .stApp, p, span, h1, h2, h3, h4, h5, h6, label {
        color: #2c3e50 !important;
    }
    
    /* Główny kontener (Desktop) */
    .block-container {
        background-color: rgba(255, 255, 255, 0.94) !important;
        border-radius: 15px;
        padding-top: 3rem !important;
        padding-bottom: 3rem !important;
        padding-left: 4rem !important;
        padding-right: 4rem !important;
        margin-top: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0px 8px 24px rgba(0, 0, 0, 0.1);
        max-width: 1000px;
    }
    
    /* Usunięcie obramowania formularza */
    div[data-testid="stForm"] {
        border: none !important;
        background-color: transparent !important;
        padding: 0 !important;
    }
    
    /* Główny przycisk: Generuj test (Zielony) */
    button[kind="primary"] {
        background-color: #7ed957 !important;
        color: #000000 !important;
        border-radius: 40px !important;
        font-size: 24px !important;
        font-weight: bold !important;
        padding: 15px 40px !important;
        border: none !important;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
        width: 100%;
        transition: transform 0.2s;
    }
    button[kind="primary"]:hover {
        transform: translateY(-2px);
    }
    
    /* Przycisk wtórny: Ustawienia (Niebieski) */
    button[kind="secondary"] {
        background-color: #1e90ff !important;
        color: white !important;
        border-radius: 5px !important;
        font-size: 14px !important;
        border: none !important;
        padding: 5px 20px !important;
        width: 100%;
    }
    
    /* Niebieski box z zasadami punktacji */
    .score-badge {
        background-color: #e3f2fd;
        border-radius: 20px;
        padding: 15px 25px;
        text-align: center;
        font-weight: bold;
        font-size: 16px;
        color: #0b5345;
        border: 2px solid #aed6f1;
    }

    /* ----- OPTYMALIZACJA POD TELEFONY (MOBILE RWD) ----- */
    @media (max-width: 768px) {
        .block-container {
            padding: 1.5rem 1rem !important; /* Ścięcie wielkich bocznych marginesów */
            margin-top: 0 !important;
            border-radius: 0px; /* Brak zaokrągleń przy krawędziach małego ekranu */
        }
        
        button[kind="primary"] {
            font-size: 18px !important; /* Mniejszy przycisk na telefony */
            padding: 12px 20px !important;
        }
        
        .score-badge {
            font-size: 13px !important; /* Zmniejszenie tekstu w niebieskim boxie */
            padding: 10px;
            margin-top: 10px;
        }
        
        h1 {
            font-size: 32px !important; /* Pomniejszenie nagłówka z wynikiem */
        }
    }
    </style>
""", unsafe_allow_html=True)

dodaj_tlo_z_pliku("tlo.png")

# --- LOGIKA APLIKACJI ---
@st.cache_data
def wczytaj_baze():
    try:
        with open("wielka_baza_zadan.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

if "ekran" not in st.session_state:
    st.session_state.ekran = "start"

DOMYSLNE = {
    "liczba_zadan": 50, # Domyślnie 50 pytań
    "zrodlo": "Mieszane (Wszystkie)",
    "proc_zarz": 16,
    "proc_fin": 20,
    "proc_dem": 15,
    "proc_fprz": 15
}

for klucz, wartosc in DOMYSLNE.items():
    if klucz not in st.session_state:
        st.session_state[klucz] = wartosc

def generuj_test():
    baza = wczytaj_baze()
    if st.session_state.zrodlo == "Tylko oficjalne (OWE)":
        baza = [z for z in baza if not z.get("wygenerowane_przez_ai", False)]
    elif st.session_state.zrodlo == "Tylko sztuczna inteligencja (AI)":
        baza = [z for z in baza if z.get("wygenerowane_przez_ai", False)]

    kategorie = {"Zarządzanie": [], "Finanse": [], "Demografia": [], "Finanse przedsiębiorstw": [], "Ekonomia i Inne": []}
    
    for zad in baza:
        kat = zad.get("kategoria", "").lower()
        zrodlo_pliku = zad.get("zrodlo", "").lower()
        if "zarządzan" in kat: kategorie["Zarządzanie"].append(zad)
        elif "finanse przedsiębiorstw" in kat: kategorie["Finanse przedsiębiorstw"].append(zad)
        elif "finans" in kat: kategorie["Finanse"].append(zad)
        elif "demografi" in kat or "dem" in zrodlo_pliku: kategorie["Demografia"].append(zad)
        else: kategorie["Ekonomia i Inne"].append(zad)

    total = st.session_state.liczba_zadan
    ile_zarz = math.floor(total * (st.session_state.proc_zarz / 100.0))
    ile_fin = math.floor(total * (st.session_state.proc_fin / 100.0))
    ile_dem = math.floor(total * (st.session_state.proc_dem / 100.0))
    ile_fprz = math.floor(total * (st.session_state.proc_fprz / 100.0))

    def bezpieczne_losowanie(pula, ile_chcemy):
        return random.sample(pula, min(ile_chcemy, len(pula)))

    # Losowanie pytań
    test_zarz = bezpieczne_losowanie(kategorie["Zarządzanie"], ile_zarz)
    
    test_reszta = []
    test_reszta.extend(bezpieczne_losowanie(kategorie["Finanse"], ile_fin))
    test_reszta.extend(bezpieczne_losowanie(kategorie["Demografia"], ile_dem))
    test_reszta.extend(bezpieczne_losowanie(kategorie["Finanse przedsiębiorstw"], ile_fprz))
    
    brakuje = total - (len(test_zarz) + len(test_reszta))
    if brakuje > 0:
        test_reszta.extend(bezpieczne_losowanie(kategorie["Ekonomia i Inne"], brakuje))
        
    # Tasowanie pytań - Zarządzanie zawsze ląduje na końcu
    random.shuffle(test_reszta)
    random.shuffle(test_zarz)
    test_ostateczny = test_reszta + test_zarz
    
    # Tasowanie wariantów odpowiedzi
    for i in range(len(test_ostateczny)):
        warianty = test_ostateczny[i]["odpowiedzi"].copy()
        random.shuffle(warianty)
        test_ostateczny[i]["warianty_potasowane"] = warianty
        
    return test_ostateczny

# ==========================================
# EKRAN 1: START 
# ==========================================
if st.session_state.ekran == "start":
    st.write("")
    st.write("")
    
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)
            
        st.write("")
        st.write("")
        
        if st.button("Generuj test", type="primary", use_container_width=True):
            st.session_state.test_dane = generuj_test()
            st.session_state.ekran = "test"
            st.rerun()
            
        if st.button("Ustawienia zaawansowane", type="secondary", use_container_width=True):
            st.session_state.ekran = "konfiguracja"
            st.rerun()

# ==========================================
# EKRAN UKRYTY: KONFIGURACJA
# ==========================================
elif st.session_state.ekran == "konfiguracja":
    st.markdown("<h2 style='text-align:center;'>Ustawienia zaawansowane</h2>", unsafe_allow_html=True)
    with st.container():
        st.session_state.liczba_zadan = st.number_input("Liczba pytań", min_value=1, max_value=200, value=st.session_state.liczba_zadan)
        st.session_state.zrodlo = st.selectbox("Źródło pytań", ["Mieszane (Wszystkie)", "Tylko oficjalne (OWE)", "Tylko sztuczna inteligencja (AI)"])
        c1, c2 = st.columns(2)
        with c1:
            st.session_state.proc_zarz = st.slider("Zarządzanie (%)", 0, 100, st.session_state.proc_zarz)
            st.session_state.proc_fin = st.slider("Finanse ogólne (%)", 0, 100, st.session_state.proc_fin)
        with c2:
            st.session_state.proc_dem = st.slider("Demografia (%)", 0, 100, st.session_state.proc_dem)
            st.session_state.proc_fprz = st.slider("Finanse Przedsięb. (%)", 0, 100, st.session_state.proc_fprz)
        
        st.write("")
        if st.button("Zapisz i wróć", type="primary"):
            st.session_state.ekran = "start"
            st.rerun()

# ==========================================
# EKRAN 2: TEST 
# ==========================================
elif st.session_state.ekran == "test":
    # Przesunięcie logo lekko w prawo dzięki zastosowaniu pustej kolumny (c_spacer)
    c_spacer, c_logo, c_punkty, c_spacer2 = st.columns([0.2, 1.5, 3, 0.2])
    with c_logo:
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)
    with c_punkty:
        st.write("") # Drobne obniżenie boxa względem logo
        st.markdown('<div class="score-badge">System punktacji: +2 pkt za poprawną, +1 pkt za błędną, 0 pkt za brak odpowiedzi.</div>', unsafe_allow_html=True)

    st.write("---")
    
    with st.form("formularz_testu"):
        for i, zad in enumerate(st.session_state.test_dane, 1):
            st.markdown(f"**{i}. {zad['tresc']}**")
            if zad.get("wygenerowane_przez_ai"):
                st.markdown(f"<span style='color:#7f8c8d; font-size:13px;'>🤖 AI | Dział: {zad.get('kategoria', 'Inne')}</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"<span style='color:#7f8c8d; font-size:13px;'>📜 OWE | Dział: {zad.get('kategoria', 'Inne')}</span>", unsafe_allow_html=True)
            
            st.write("")
            st.radio("Odp:", zad["warianty_potasowane"], key=f"pyt_{i}", index=None, label_visibility="collapsed")
            st.markdown("<br>", unsafe_allow_html=True)
            st.divider()
        
        c_btn1, c_btn2, c_btn3 = st.columns([1, 2, 1])
        with c_btn2:
            if st.form_submit_button("Zakończ test", type="primary", use_container_width=True):
                st.session_state.ekran = "wyniki"
                st.rerun()

# ==========================================
# EKRAN 3: WYNIKI 
# ==========================================
elif st.session_state.ekran == "wyniki":
    wynik, poprawne, bledne, puste = 0, 0, 0, 0
    total_q = len(st.session_state.test_dane)
    
    for i, zad in enumerate(st.session_state.test_dane, 1):
        odp_usera = st.session_state.get(f"pyt_{i}")
        poprawna = zad.get("poprawna") or zad.get("poprawna_odpowiedz") or "BRAK DANYCH"
        
        czysta_odp = odp_usera.split(". ", 1)[+1] if (odp_usera and ". " in odp_usera[:3]) else odp_usera
        czysta_poprawna = poprawna.split(". ", 1)[+1] if ". " in poprawna[:3] else poprawna
        
        trafiony = (czysta_odp == czysta_poprawna) if (odp_usera and poprawna != "BRAK DANYCH") else False

        if odp_usera is not None and trafiony:
            wynik += 2
            poprawne += 1
        elif odp_usera is not None:
            wynik += 1 # <--- POPRAWIONA LINIA
            bledne += 1
        else:
            puste += 1

    c_wynik, c_logo = st.columns([2, 1])
    with c_wynik:
        st.markdown(f"<h1 style='color: #000000; font-size: 40px;'>Twój wynik: {wynik} pkt</h1>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='color: #2c3e50; font-weight: normal;'>poprawne: <b>{poprawne}</b></h3>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='color: #2c3e50; font-weight: normal;'>błędne: <b>{bledne}</b></h3>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='color: #2c3e50; font-weight: normal;'>opuszczone: <b>{puste}</b></h3>", unsafe_allow_html=True)
    with c_logo:
        if os.path.exists("logo.png"):
            st.image("logo.png", use_container_width=True)
            
    st.divider()
    
    for i, zad in enumerate(st.session_state.test_dane, 1):
        odp_usera = st.session_state.get(f"pyt_{i}")
        poprawna = zad.get("poprawna") or zad.get("poprawna_odpowiedz") or "BRAK DANYCH"
        
        czysta_odp = odp_usera.split(". ", 1)[+1] if (odp_usera and ". " in odp_usera[:3]) else odp_usera
        czysta_poprawna = poprawna.split(". ", 1)[+1] if ". " in poprawna[:3] else poprawna
        
        st.markdown(f"**{i}. {zad['tresc']}**")
        if odp_usera and czysta_odp == czysta_poprawna:
            st.success(f"✅ {odp_usera} (+2 pkt)")
        else:
            if odp_usera:
                st.error(f"❌ {odp_usera} (+1 pkt)")
            else:
                st.warning("⚠️ Brak odpowiedzi (0 pkt)")
            st.info(f"🎯 Poprawna: {poprawna}")
        st.write("")
    
    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        if st.button("Rozwiąż nowy test", use_container_width=True, type="primary"):
            st.session_state.test_dane = generuj_test()
            st.session_state.ekran = "test"
            st.rerun()
    with c_btn2:
        if st.button("Wróć do menu", use_container_width=True, type="secondary"):
            st.session_state.ekran = "start"
            st.rerun()