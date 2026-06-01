import streamlit as st
import json
import os
from datetime import datetime, timedelta

# ── SIVUN ALUSTUS (TÄYTYY OLLA ENNEN MUUTA KOODIA) ──────────────────
st.set_page_config(page_title="Peliaikapankki", page_icon="🎮", layout="centered")

DATA_FILE = "peliaika_data.json"
SOVELLUKSEN_PIN = "4321"
VANHEMMAN_PIN = "2411"

KATEGORIAT = ["Sisätyöt", "Ulkotyöt", "Urheilu"]
KATEGORIA_IKONIT = {"Sisätyöt": "🏠", "Ulkotyöt": "🌿", "Urheilu": "⚽"}
LAPSI_VARIT = ["#7C3AED", "#0EA5E9", "#10B981", "#F59E0B", "#EF4444"]

SAAVUTUKSET = [
    ("eka_tyo",      "Ensiaskel",         "🌱", "Ensimmäinen työ tehty!"),
    ("tyo_5",        "Ahkera apuri",       "⭐", "5 työtä suoritettu"),
    ("tyo_10",       "Kotityösankari",     "🏆", "10 työtä suoritettu"),
    ("tyo_25",       "Legendaarinen",      "👑", "25 työtä suoritettu"),
    ("putki_3",      "3 päivän putki",     "🔥", "Töitä 3 päivänä peräkkäin"),
    ("putki_5",      "5 päivän putki",     "🔥🔥", "Töitä 5 päivänä peräkkäin"),
    ("putki_7",      "Viikon mestari",     "💎", "Töitä 7 päivänä peräkkäin"),
]

CSS = """
<style>
html, body, [data-testid="stAppViewContainer"] { background-color: #0F0F1A; }
h1 { font-size: 2rem !important; }

.saldo-kortti {
    background: linear-gradient(135deg, var(--kortti-vari) 0%, #1A1A2E 100%);
    border: 1px solid var(--kortti-vari);
    border-radius: 16px;
    padding: 20px 16px 16px 16px;
    margin-bottom: 12px;
    text-align: center;
    cursor: pointer;
    transition: transform 0.2s, box-shadow 0.2s;
}
.saldo-kortti:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.4);
}
.saldo-nimi { font-size: 1rem; color: #CBD5E1; margin-bottom: 4px; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase; }
.saldo-arvo { font-size: 2.6rem; font-weight: 800; color: #FFFFFF; line-height: 1.1; }
.saldo-yksikko { font-size: 1rem; color: #94A3B8; font-weight: 400; }
.prog-container { background: #2D2D4A; border-radius: 99px; height: 12px; margin: 10px 0 6px 0; overflow: hidden; }
.prog-bar { height: 12px; border-radius: 99px; background: linear-gradient(90deg, var(--kortti-vari), #A78BFA); }
.prog-teksti { font-size: 0.75rem; color: #94A3B8; text-align: right; }

.badge {
    display: inline-block;
    background: #1E1B3A;
    border: 1px solid #3D3A6A;
    border-radius: 10px;
    padding: 8px 10px;
    margin: 4px;
    text-align: center;
    min-width: 80px;
}
.badge.saavutettu { border-color: #7C3AED; background: linear-gradient(135deg, #2D1B69, #1A1A2E); }
.badge-ikoni { font-size: 1.5rem; }
.badge-nimi { font-size: 0.7rem; color: #94A3B8; margin-top: 2px; }
.badge.saavutettu .badge-nimi { color: #C4B5FD; }

.putki-box {
    background: linear-gradient(135deg, #1E1B3A, #2D1B69);
    border: 1px solid #7C3AED;
    border-radius: 12px;
    padding: 12px 16px;
    margin-bottom: 10px;
    text-align: center;
}
.putki-numero { font-size: 2rem; font-weight: 800; color: #F59E0B; }
.putki-teksti { font-size: 0.85rem; color: #94A3B8; }

.login-box {
    background: #1A1A2E; border: 1px solid #7C3AED; border-radius: 20px;
    padding: 32px 24px; max-width: 340px; margin: 60px auto 0 auto; text-align: center;
}
.login-otsikko { font-size: 1.4rem; font-weight: 700; color: #E2E8F0; margin-bottom: 4px; }
.login-alaotsikko { font-size: 0.85rem; color: #64748B; margin-bottom: 20px; }

.odottava-kortti {
    background: #1E1B3A; border-left: 4px solid #F59E0B;
    border-radius: 10px; padding: 12px 16px; margin-bottom: 10px;
}
.historia-rivi {
    background: #1A1A2E; border-radius: 8px;
    padding: 8px 12px; margin-bottom: 6px; font-size: 0.9rem;
}
.raportti-kortti {
    background: #1A1A2E; border: 1px solid #2D2D4A;
    border-radius: 12px; padding: 16px; margin-bottom: 10px;
}
.raportti-otsikko { font-size: 0.8rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; }
.raportti-arvo { font-size: 1.8rem; font-weight: 700; color: #E2E8F0; }

.vahvistus-kortti {
    background: linear-gradient(135deg, #1E1B3A, #2D1B69);
    border: 2px solid #7C3AED;
    border-radius: 20px;
    padding: 28px 20px;
    text-align: center;
    margin-bottom: 16px;
}
.vahvistus-tehtava { font-size: 1.3rem; font-weight: 700; color: #E2E8F0; margin-bottom: 6px; }
.vahvistus-min { font-size: 2rem; font-weight: 800; color: #A78BFA; }
.vahvistus-teksti { font-size: 0.85rem; color: #64748B; margin-top: 4px; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ── DATAN LATAUS & TALLENNUS ───────────────────────────────────
def lataa_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return {
        "saldot": {"Poika 1": 0, "Poika 2": 0},
        "odottavat": [],
        "historia": [],
        "asetukset": {"tavoite_min": 90},
        "saavutukset": {},
        "tehtavat": {
            "Kodin imurointi":       {"minuutit": 20, "kategoria": "Sisätyöt", "bonus": False},
            "Pölyjen pyyhintä":      {"minuutit": 15, "kategoria": "Sisätyöt", "bonus": False},
            "Tiskikoneen tyhjennys": {"minuutit": 10, "kategoria": "Sisätyöt", "bonus": False},
            "Auton imurointi":       {"minuutit": 30, "kategoria": "Sisätyöt", "bonus": False},
            "Autotallin siivous":    {"minuutit": 60, "kategoria": "Ulkotyöt", "bonus": False},
            "Auton pesu ulkoa":      {"minuutit": 45, "kategoria": "Ulkotyöt", "bonus": False},
            "Pihavajan siivous":     {"minuutit": 45, "kategoria": "Ulkotyöt", "bonus": False},
        }
    }

def tallenna_data():
    data = {
        "saldot": st.session_state.saldot,
        "odottavat": st.session_state.odottavat,
        "historia": st.session_state.historia,
        "asetukset": st.session_state.asetukset,
        "saavutukset": st.session_state.saavutukset,
        "tehtavat": st.session_state.tehtavat
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def lisaa_historia(tekija, tapahtuma, minuutit, tyyppi):
    merkinta = {
        "aika": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "tekija": tekija,
        "tapahtuma": tapahtuma,
        "minuutit": minuutit,
        "tyyppi": tyyppi
    }
    st.session_state.historia.insert(0, merkinta)
    st.session_state.historia = st.session_state.historia[:200]

def migraatio_tehtavat():
    for nimi, arvo in st.session_state.tehtavat.items():
        if isinstance(arvo, int):
            st.session_state.tehtavat[nimi] = {"minuutit": arvo, "kategoria": "Sisätyöt", "bonus": False}

# ── SAAVUTUS- JA PUTKILOGIIKKA ─────────────────────────────────
def laske_putki(nimi):
    paivat = set()
    for m in st.session_state.historia:
        if m["tekija"] == nimi and m["tyyppi"] == "ansaittu":
            try:
                pvm = datetime.strptime(m["aika"], "%d.%m.%Y %H:%M").date()
                paivat.add(pvm)
            except:
                pass
    if not paivat:
        return 0
        
    tarkistus = datetime.now().date()
    if tarkistus not in paivat:
        tarkistus -= timedelta(days=1)
        
    putki = 0
    while tarkistus in paivat:
        putki += 1
        tarkistus -= timedelta(days=1)
    return putki

def laske_tyot_yhteensa(nimi):
    return sum(1 for m in st.session_state.historia if m["tekija"] == nimi and m["tyyppi"] == "ansaittu")

def tarkista_saavutukset(nimi):
    if nimi not in st.session_state.saavutukset:
        st.session_state.saavutukset[nimi] = []
    saavutetut = st.session_state.saavutukset[nimi]
    uudet = []
    tyot = laske_tyot_yhteensa(nimi)
    putki = laske_putki(nimi)

    tarkistukset = {
        "eka_tyo":  tyot >= 1,
        "tyo_5":    tyot >= 5,
        "tyo_10":   tyot >= 10,
        "tyo_25":   tyot >= 25,
        "putki_3":  putki >= 3,
        "putki_5":  putki >= 5,
        "putki_7":  putki >= 7,
    }
    for sav_id, ehto in tarkistukset.items():
        if ehto and sav_id not in saavutetut:
            saavutetut.append(sav_id)
            uudet.append(sav_id)
    return uudet

def viikko_data(nimi, viikkoja_taaksepain=0):
    nyt = datetime.now().date()
    viikon_alku = nyt - timedelta(days=nyt.weekday()) - timedelta(weeks=viikkoja_taaksepain)
    viikon_loppu = viikon_alku + timedelta(days=6)
    minuutit = 0
    tyot = 0
    for m in st.session_state.historia:
        if m["tekija"] == nimi and m["tyyppi"] == "ansaittu":
            try:
                pvm = datetime.strptime(m["aika"], "%d.%m.%Y %H:%M").date()
                if viikon_alku <= pvm <= viikon_loppu:
                    minuutit += m["minuutit"]
                    tyot += 1
            except:
                pass
    return minuutit, tyot, viikon_alku, viikon_loppu

# ── APUFUNKTIOT VISUALISOINTIIN ────────────────────────────────
def saldo_kortti_html(nimi, saldo, vari, tavoite):
    progress = min(saldo / tavoite, 1.0) if tavoite > 0 else 0
    bar_width = int(progress * 100)
    return f"""
    <div class="saldo-kortti" style="--kortti-vari: {vari};">
        <div class="saldo-nimi">🎮 {nimi}</div>
        <div class="saldo-arvo">{saldo}<span class="saldo-yksikko"> min</span></div>
        <div class="prog-container">
            <div class="prog-bar" style="width: {bar_width}%;"></div>
        </div>
        <div class="prog-teksti">{bar_width}% tavoitteesta ({tavoite} min)</div>
    </div>
    """

def lapset():
    return list(st.session_state.saldot.keys())

# ── SESSION STATE ALUSTUKSET ───────────────────────────────────
if "data_ladattu" not in st.session_state:
    d = lataa_data()
    st.session_state.saldot = d["saldot"]
    st.session_state.odottavat = d["odottavat"]
    st.session_state.historia = d.get("historia", [])
    st.session_state.tehtavat = d["tehtavat"]
    st.session_state.asetukset = d.get("asetukset", {"tavoite_min": 90})
    st.session_state.saavutukset = d.get("saavutukset", {})
    st.session_state.data_ladattu = True
    st.session_state.vanhempi_kirjautunut = False
    st.session_state.sovellus_kirjautunut = False
    st.session_state.valittu_lapsi = None
    st.session_state.valittu_tehtava = None

migraatio_tehtavat()

# ── UI / KIRJAUTUMISPORTTI ──────────────────────────────────────
if not st.session_state.sovellus_kirjautunut:
    st.markdown("""
    <div class="login-box">
        <div style="font-size:3rem;">🎮</div>
        <div class="login-otsikko">Perheen Peliaikapankki</div>
        <div class="login-alaotsikko">Syötä PIN kirjautuaksesi</div>
    </div>
    """, unsafe_allow_html=True)
    st.write("")
    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        sovellus_pin = st.text_input("PIN", type="password", max_chars=4, key="sovellus_pin", label_visibility="collapsed", placeholder="• • • •")
        if st.button("Kirjaudu sisään 🔓", use_container_width=True):
            if sovellus_pin == SOVELLUKSEN_PIN:
                st.session_state.sovellus_kirjautunut = True
                st.rerun()
            else:
                st.error("Väärä PIN-koodi!")
    st.stop()

# Varsinainen sovellusnäkymä
st.title("🎮 Perheen Peliaikapankki")
tavoite = st.session_state.asetukset.get("tavoite_min", 90)
tab_pojat, tab_vanhempi, tab_historia = st.tabs(["🚀 Lapset", "🛡️ Vanhempi", "📜 Historia"])

# ══════════════════════════════════════════════════════════════
# VÄLILEHTI 1: LAPSET (UUDISTETTU PELIMÄINEN KÄYTTÖLIITTYMÄ)
# ══════════════════════════════════════════════════════════════
with tab_pojat:
    
    # 1. NÄKYMÄ: Työn onnistunut lähettäminen
    if st.session_state.get("lahetetty"):
        lapsi_v = st.session_state.lahetetty_lapsi
        tyo_v   = st.session_state.lahetetty_tyo
        min_v   = st.session_state.lahetetty_min
        i_v     = lapset().index(lapsi_v) if lapsi_v in lapset() else 0
        vari_v  = LAPSI_VARIT[i_v % len(LAPSI_VARIT)]
        st.markdown(f"""
        <div style="text-align:center; padding: 40px 0 20px 0;">
            <div style="font-size:4rem;">🎉</div>
            <div style="font-size:1.5rem; font-weight:800; color:#E2E8F0; margin:10px 0 4px 0;">Lähetetty!</div>
            <div style="font-size:1rem; color:#94A3B8;">Vanhempi tarkistaa työn pian.</div>
        </div>
        <div class="vahvistus-kortti" style="border-color:{vari_v};">
            <div class="vahvistus-tehtava">{tyo_v}</div>
            <div class="vahvistus-min">+{min_v} min</div>
            <div class="vahvistus-teksti">odottaa hyväksyntää</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("⬅️ Takaisin alkuun", use_container_width=True):
            st.session_state.lahetetty = False
            st.session_state.valittu_lapsi = None
            st.session_state.valittu_tehtava = None
            st.rerun()
        st.stop()

    # 2. NÄKYMÄ: Valitun tehtävän tarkastelu ja lähetys
    elif st.session_state.valittu_tehtava is not None:
        lapsi_n = st.session_state.valittu_lapsi
        tyo_n   = st.session_state.valittu_tehtava
        tiedot  = st.session_state.tehtavat[tyo_n]
        i_n     = lapset().index(lapsi_n) if lapsi_n in lapset() else 0
        vari_n  = LAPSI_VARIT[i_n % len(LAPSI_VARIT)]
        kat_ikoni = KATEGORIA_IKONIT.get(tiedot["kategoria"], "")
        bonus_teksti = " ⭐ BONUS" if tiedot["bonus"] else ""

        st.markdown(f"""
        <div style="text-align:center; padding:16px 0 8px 0;">
            <div style="font-size:0.85rem; color:#64748B; text-transform:uppercase; letter-spacing:0.05em;">Vahvista työ</div>
            <div style="font-size:1.2rem; font-weight:700; color:{vari_n}; margin-top:4px;">🎮 {lapsi_n}</div>
        </div>
        <div class="vahvistus-kortti" style="border-color:{vari_n};">
            <div style="font-size:1.5rem;">{kat_ikoni}</div>
            <div class="vahvistus-tehtava">{tyo_n}{bonus_teksti}</div>
            <div class="vahvistus-min" style="color:{vari_n};">+{tiedot['minuutit']} min</div>
            <div class="vahvistus-teksti">{tiedot['kategoria']}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("📨 Lähetä vanhemman hyväksyttäväksi", use_container_width=True):
            st.session_state.odottavat.append({
                "id": len(st.session_state.odottavat) + 1,
                "tekija": lapsi_n,
                "tyo": tyo_n,
                "minuutit": tiedot["minuutit"],
                "bonus": tiedot["bonus"],
                "aika": datetime.now().strftime("%d.%m.%Y %H:%M")
            })
            tallenna_data()
            st.session_state.lahetetty = True
            st.session_state.lahetetty_lapsi = lapsi_n
            st.session_state.lahetetty_tyo = tyo_n
            st.session_state.lahetetty_min = tiedot["minuutit"]
            st.rerun()

        if st.button("⬅️ Valitse toinen tehtävä", use_container_width=True):
            st.session_state.valittu_tehtava = None
            st.rerun()

    # 3. NÄKYMÄ: Pelaajalista ja valitun pelaajan alle aukeavat tehtävät
    else:
        st.markdown("<div style='text-align:center;font-size:1rem;color:#94A3B8;margin-bottom:16px;'>Klikkaa omaa laatikkoasi:</div>", unsafe_allow_html=True)
        
        # Luodaan pelaajalaatikot vierekkäin
        cols = st.columns(len(lapset()))
        for i, nimi in enumerate(lapset()):
            vari = LAPSI_VARIT[i % len(LAPSI_VARIT)]
            saldo = st.session_state.saldot[nimi]
            putki = laske_putki(nimi)
            tuli  = ("🔥" * min(putki, 3)) if putki > 0 else ""
            
            with cols[i]:
                # Piirretään visuaalinen laatikko HTML:nä
                st.markdown(saldo_kortti_html(nimi, saldo, vari, tavoite), unsafe_allow_html=True)
                if putki > 0:
                    st.markdown(f"<div style='text-align:center;font-size:0.9rem;color:#F59E0B;margin:-6px 0 8px 0;'>{tuli} {putki} pv putki</div>", unsafe_allow_html=True)
                
                # Alapuolella oleva valintapainike aktivoi kyseisen lapsen
                on_valittu = (st.session_state.valittu_lapsi == nimi)
                nappi_teksti = f"✅ Valittu: {nimi}" if on_valittu else f"Valitse {nimi} 👋"
                if st.button(nappi_teksti, key=f"pelaaja_nappi_{nimi}", use_container_width=True, type="primary" if on_valittu else "secondary"):
                    if on_valittu:
                        st.session_state.valittu_lapsi = None # Toinen klikkaus sulkee valikon
                    else:
                        st.session_state.valittu_lapsi = nimi
                    st.rerun()

        # JOS LAPSI ON VALITTUNA: Tehtävät aukeavat suoraan laatikoiden alle ilman pudotusvalikkoa!
        if st.session_state.valittu_lapsi is not None:
            lapsi_aktiivinen = st.session_state.valittu_lapsi
            i_n = lapset().index(lapsi_aktiivinen)
            vari_n = LAPSI_VARIT[i_n % len(LAPSI_VARIT)]
            
            st.markdown("---")
            st.markdown(f"<div style='font-size:1.1rem;font-weight:700;color:{vari_n};margin:8px 0 12px 0;'>✨ Pelaajan {lapsi_aktiivinen} tehtävät:</div>", unsafe_allow_html=True)

            # Ryhmitellään tehtävät kauniisti kategorioittain
            for kat in KATEGORIAT:
                kat_ikoni = KATEGORIA_IKONIT[kat]
                kat_tehtavat = {n: t for n, t in st.session_state.tehtavat.items() if t["kategoria"] == kat}
                if not kat_tehtavat:
                    continue
                
                st.markdown(f"<div style='font-size:0.8rem;color:#94A3B8;text-transform:uppercase;letter-spacing:0.08em;margin:16px 0 8px 0;'>{kat_ikoni} {kat}</div>", unsafe_allow_html=True)
                
                # Tehtävät painikkeina
                for tyo_nimi, tyo_tiedot in sorted(kat_tehtavat.items(), key=lambda x: x[1]["minuutit"]):
                    bonus_merkki = " ⭐" if tyo_tiedot["bonus"] else ""
                    nappi_label = f"{tyo_nimi}{bonus_merkki}  ·  +{tyo_tiedot['minuutit']} min"
                    if st.button(nappi_label, key=f"tyonappi_{tyo_nimi}", use_container_width=True):
                        st.session_state.valittu_tehtava = tyo_nimi
                        st.rerun()

            if st.button("❌ Sulje tehtävälista", use_container_width=True):
                st.session_state.valittu_lapsi = None
                st.rerun()

        # Saavutukset aina näkyvissä alareunassa
        st.markdown("---")
        st.subheader("🏆 Saavutukset")
        sav_cols = st.columns(len(lapset()))
        for i, nimi in enumerate(lapset()):
            saavutetut = st.session_state.saavutukset.get(nimi, [])
            with sav_cols[i]:
                st.write(f"**{nimi}**")
                badges_html = ""
                for sav_id, sav_nimi, ikoni, kuvaus in SAAVUTUKSET:
                    on = sav_id in saavutetut
                    css_luokka = "badge saavutettu" if on else "badge"
                    opacity = "1.0" if on else "0.25"
                    badges_html += f'<div class="{css_luokka}" style="opacity:{opacity}" title="{kuvaus}"><div class="badge-ikoni">{ikoni}</div><div class="badge-nimi">{sav_nimi}</div></div>'
                st.markdown(f'<div style="display:flex;flex-wrap:wrap;">{badges_html}</div>', unsafe_allow_html=True)

        if st.session_state.odottavat:
            st.markdown("---")
            st.subheader("⏳ Odottaa hyväksyntää")
            for tyo in st.session_state.odottavat:
                bonus_teksti = " ⭐ BONUS" if tyo.get("bonus") else ""
                st.markdown(f"""
                <div class="odottava-kortti">
                    ⏳ <strong>{tyo['tekija']}</strong>: {tyo['tyo']}{bonus_teksti}
                    &nbsp;·&nbsp; <span style="color:#A78BFA">+{tyo['minuutit']} min</span>
                    &nbsp;·&nbsp; <span style="color:#64748B;font-size:0.8rem">{tyo.get('aika','')}</span>
                </div>
                """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# VÄLILEHTI 2: VANHEMPI
# ══════════════════════════════════════════════════════════════
with tab_vanhempi:
    st.subheader("🛡️ Vanhemman hallintapaneeli")

    if not st.session_state.vanhempi_kirjautunut:
        st.info("Syötä vanhemman PIN-koodi.")
        col_l, col_m, col_r = st.columns([1, 2, 1])
        with col_m:
            pin_syote = st.text_input("PIN", type="password", max_chars=4, key="pin_input", label_visibility="collapsed", placeholder="• • • •")
            if st.button("🔓 Kirjaudu", use_container_width=True):
                if pin_syote == VANHEMMAN_PIN:
                    st.session_state.vanhempi_kirjautunut = True
                    st.rerun()
                else:
                    st.error("Väärä PIN-koodi!")
    else:
        if st.button("🔒 Kirjaudu ulos", use_container_width=True):
            st.session_state.vanhempi_kirjautunut = False
            st.rerun()

        st.markdown("---")

        st.write("### 📋 Odottavat työt")
        if not st.session_state.odottavat:
            st.info("Ei odottavia töitä. 👍")
        else:
            for tyo_item in list(st.session_state.odottavat):
                bonus_teksti = " ⭐ BONUS" if tyo_item.get("bonus") else ""
                st.markdown(f"""
                <div class="odottava-kortti">
                    <strong>{tyo_item['tekija']}</strong>: {tyo_item['tyo']}{bonus_teksti}
                    &nbsp;·&nbsp; <span style="color:#A78BFA">+{tyo_item['minuutit']} min</span>
                    &nbsp;·&nbsp; <span style="color:#64748B;font-size:0.8rem">{tyo_item.get('aika','')}</span>
                </div>
                """, unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    if st.button(f"👍 Hyväksy", key=f"hyv_{tyo_item['id']}"):
                        st.session_state.saldot[tyo_item['tekija']] += tyo_item['minuutit']
                        lisaa_historia(tyo_item['tekija'], tyo_item['tyo'], tyo_item['minuutit'], "ansaittu")
                        if tyo_item.get("bonus") and tyo_item['tyo'] in st.session_state.tehtavat:
                            del st.session_state.tehtavat[tyo_item['tyo']]
                        st.session_state.odottavat.remove(tyo_item)
                        
                        uudet_sav = tarkista_saavutukset(tyo_item['tekija'])
                        tallenna_data()
                        if uudet_sav:
                            nimet = [s[1] for s in SAAVUTUKSET if s[0] in uudet_sav]
                            st.success(f"🏆 Uusi saavutus: {', '.join(nimet)}!")
                        st.balloons()
                        st.rerun()
                with c2:
                    if st.button(f"👎 Hylkää", key=f"hyl_{tyo_item['id']}"):
                        lisaa_historia(tyo_item['tekija'], tyo_item['tyo'], tyo_item['minuutit'], "hylätty")
                        st.session_state.odottavat.remove(tyo_item)
                        tallenna_data()
                        st.rerun()

        st.markdown("---")

        st.write("### 📈 Viikkoraportti")
        viikko_valinta = st.radio("Viikko:", ["Tämä viikko", "Edellinen viikko"], horizontal=True)
        taaksepain = 0 if viikko_valinta == "Tämä viikko" else 1

        for i, nimi in enumerate(lapset()):
            min_viikko, tyot_viikko, vk_alku, vk_loppu = viikko_data(nimi, taaksepain)
            min_edellinen, tyot_edellinen, _, _ = viikko_data(nimi, taaksepain + 1)
            muutos = min_viikko - min_edellinen
            muutos_teksti = f"+{muutos}" if muutos >= 0 else str(muutos)
            muutos_vari = "#10B981" if muutos >= 0 else "#EF4444"
            vari = LAPSI_VARIT[i % len(LAPSI_VARIT)]

            st.markdown(f"""
            <div class="raportti-kortti" style="border-color: {vari}40;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                    <span style="font-weight:700; color:{vari}; font-size:1.1rem;">🎮 {nimi}</span>
                    <span style="font-size:0.75rem; color:#475569;">{vk_alku.strftime('%d.%m')} – {vk_loppu.strftime('%d.%m.%Y')}</span>
                </div>
                <div style="display:flex; gap:16px;">
                    <div>
                        <div class="raportti-otsikko">Ansaittu</div>
                        <div class="raportti-arvo" style="color:{vari};">{min_viikko} min</div>
                    </div>
                    <div>
                        <div class="raportti-otsikko">Töitä</div>
                        <div class="raportti-arvo">{tyot_viikko} kpl</div>
                    </div>
                    <div>
                        <div class="raportti-otsikko">vs. ed. viikko</div>
                        <div class="raportti-arvo" style="color:{muutos_vari};">{muutos_teksti} min</div>
                    </div>
                    <div>
                        <div class="raportti-otsikko">Putki</div>
                        <div class="raportti-arvo">{laske_putki(nimi)} 🔥</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        st.write("### 💰 Peliajan käyttäminen")
        vahennettava_pelaaja = st.selectbox("Kuka pelaa?", lapset(), key="pelaaja_vahennys")
        kaytetyt_minuutit = st.number_input("Käytettävä aika minuutteina", min_value=5, max_value=300, value=15, step=5)
        if st.button("🎮 Vähennä minuutit saldosta", use_container_width=True):
            nykyinen_saldo = st.session_state.saldot[vahennettava_pelaaja]
            if nykyinen_saldo >= kaytetyt_minuutit:
                st.session_state.saldot[vahennettava_pelaaja] -= kaytetyt_minuutit
                lisaa_historia(vahennettava_pelaaja, "Pelaaminen", kaytetyt_minuutit, "käytetty")
                tallenna_data()
                st.success(f"Vähennetty {kaytetyt_minuutit} min pelaajalta {vahennettava_pelaaja}!")
                st.rerun()
            else:
                st.error(f"Ei tarpeeksi peliaikaa! Saldo: {nykyinen_saldo} min")

        st.markdown("---")

        st.write("### ⚙️ Asetukset")
        st.write("**Peliajan tavoite:**")
        uusi_tavoite = st.number_input(
            "Tavoite minuutteina (progress bar täyttyy tähän)",
            min_value=10, max_value=500,
            value=st.session_state.asetukset.get("tavoite_min", 90),
            step=10, key="tavoite_input"
        )
        if st.button("💾 Tallenna tavoite", use_container_width=True):
            st.session_state.asetukset["tavoite_min"] = uusi_tavoite
            tallenna_data()
            st.success(f"Tavoite asetettu: {uusi_tavoite} min!")
            st.rerun()

        st.markdown("---")

        st.write("### 👦 Lasten hallinta")
        st.write("**Muuta lapsen nimeä:**")
        muutettava = st.selectbox("Valitse lapsi", lapset(), key="muutettava_lapsi")
        uusi_lapsen_nimi = st.text_input("Uusi nimi", value=muutettava, key="uusi_lapsen_nimi")
        if st.button("✏️ Tallenna uusi nimi", use_container_width=True):
            uusi_lapsen_nimi = uusi_lapsen_nimi.strip()
            if uusi_lapsen_nimi and uusi_lapsen_nimi != muutettava:
                if uusi_lapsen_nimi in st.session_state.saldot:
                    st.error(f"Nimi '{uusi_lapsen_nimi}' on jo käytössä!")
                else:
                    vanha_saldo = st.session_state.saldot.pop(muutettava)
                    st.session_state.saldot[uusi_lapsen_nimi] = vanha_saldo
                    for tyo in st.session_state.odottavat:
                        if tyo["tekija"] == muutettava:
                            tyo["tekija"] = uusi_lapsen_nimi
                    for merkinta in st.session_state.historia:
                        if merkinta["tekija"] == muutettava:
                            merkinta["tekija"] = uusi_lapsen_nimi
                    if muutettava in st.session_state.saavutukset:
                        st.session_state.saavutukset[uusi_lapsen_nimi] = st.session_state.saavutukset.pop(muutettava)
                    tallenna_data()
                    st.success(f"Nimi muutettu: '{muutettava}' → '{uusi_lapsen_nimi}'")
                    st.rerun()
            elif uusi_lapsen_nimi == muutettava:
                st.info("Nimi on jo sama.")

        st.write("")
        st.write("**Lisää uusi lapsi:**")
        uuden_nimi = st.text_input("Uuden lapsen nimi", key="uuden_lapsen_nimi")
        if st.button("➕ Lisää lapsi", use_container_width=True):
            uuden_nimi = uuden_nimi.strip()
            if uuden_nimi:
                if uuden_nimi in st.session_state.saldot:
                    st.error(f"'{uuden_nimi}' on jo listalla!")
                else:
                    st.session_state.saldot[uuden_nimi] = 0
                    tallenna_data()
                    st.success(f"'{uuden_nimi}' lisätty!")
                    st.rerun()
            else:
                st.error("Syötä nimi ensin.")

        st.write("")
        st.write("**Poista lapsi:**")
        if len(lapset()) > 1:
            poistettava_lapsi = st.selectbox("Valitse poistettava", lapset(), key="poistettava_lapsi")
            poisto_varmistus = st.checkbox(f"Vahvistan poiston – '{poistettava_lapsi}' ja hänen saldonsa poistetaan")
            if st.button("🗑️ Poista lapsi", disabled=not poisto_varmistus, use_container_width=True):
                del st.session_state.saldot[poistettava_lapsi]
                st.session_state.odottavat = [t for t in st.session_state.odottavat if t["tekija"] != poistettava_lapsi]
                st.session_state.saavutukset.pop(poistettava_lapsi, None)
                tallenna_data()
                st.success(f"'{poistettava_lapsi}' poistettu.")
                st.rerun()
        else:
            st.info("Vähintään yksi lapsi täytyy olla listalla.")

        st.markdown("---")

        st.write("### 🚨 Saldojen nollaus")
        varmistus = st.checkbox("Vahvistan, että haluan tyhjentää kaikkien saldot nollaan")
        if st.button("🚨 NOLLAA KAIKKIEN SALDOT", disabled=not varmistus, use_container_width=True):
            for nimi in lapset():
                st.session_state.saldot[nimi] = 0
            lisaa_historia("Kaikki", "Saldot nollattu", 0, "käytetty")
            tallenna_data()
            st.success("Saldot nollattu!")
            st.rerun()

        st.markdown("---")

        st.write("### 🛠️ Hallitse tehtäviä")
        st.write("**Nykyiset tehtävät:**")
        for kat in KATEGORIAT:
            ikoni = KATEGORIA_IKONIT[kat]
            kat_tehtavat = {n: t for n, t in st.session_state.tehtavat.items() if t["kategoria"] == kat}
            if kat_tehtavat:
                st.write(f"{ikoni} **{kat}**")
                for nimi, tiedot in sorted(kat_tehtavat.items(), key=lambda x: x[1]["minuutit"]):
                    bonus_merkki = " ⭐" if tiedot["bonus"] else ""
                    st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;• {nimi}{bonus_merkki} — {tiedot['minuutit']} min")

        st.write("")
        st.write("**Muokkaa olemassaolevaa tehtävää:**")
        muokattava_nimi = st.selectbox("Valitse tehtävä", list(st.session_state.tehtavat.keys()), key="muokattava_tehtava")
        if muokattava_nimi:
            nykyiset = st.session_state.tehtavat[muokattava_nimi]
            uudet_min_muokkaus = st.number_input("Minuutit", min_value=5, max_value=300, value=nykyiset["minuutit"], step=5, key="muokkaa_min")
            uusi_kat_muokkaus = st.selectbox("Kategoria", KATEGORIAT,
                index=KATEGORIAT.index(nykyiset["kategoria"]) if nykyiset["kategoria"] in KATEGORIAT else 0,
                key="muokkaa_kat")
            if st.button("💾 Tallenna muutokset", use_container_width=True):
                st.session_state.tehtavat[muokattava_nimi]["minuutit"] = uudet_min_muokkaus
                st.session_state.tehtavat[muokattava_nimi]["kategoria"] = uusi_kat_muokkaus
                tallenna_data()
                st.success(f"Tehtävä '{muokattava_nimi}' päivitetty!")
                st.rerun()

        st.write("")
        st.write("**Lisää uusi tehtävä:**")
        uusi_tehtava_nimi = st.text_input("Tehtävän nimi", key="uusi_tehtava_nimi")
        uusi_tehtava_min = st.number_input("Peliaika minuutteina", min_value=5, max_value=300, value=15, step=5, key="uusi_tehtava_min")
        uusi_tehtava_kat = st.selectbox("Kategoria", KATEGORIAT, key="uusi_tehtava_kat")
        on_bonus = st.checkbox("⭐ Bonustehtävä (häviää listalta kun hyväksytty)", key="uusi_bonus")
        if st.button("➕ Lisää tehtävä", use_container_width=True):
            uusi_tehtava_nimi = uusi_tehtava_nimi.strip()
            if uusi_tehtava_nimi:
                st.session_state.tehtavat[uusi_tehtava_nimi] = {
                    "minuutit": uusi_tehtava_min,
                    "kategoria": uusi_tehtava_kat,
                    "bonus": on_bonus
                }
                tallenna_data()
                st.success(f"Tehtävä '{uusi_tehtava_nimi}' lisätty!")
                st.rerun()
            else:
                st.error("Syötä tehtävän nimi ensin.")

        st.write("")
        st.write("**Poista tehtävä:**")
        poistettava_tehtava = st.selectbox("Valitse poistettava tehtävä", list(st.session_state.tehtavat.keys()), key="poistettava_tehtava")
        if st.button("❌ Poista valittu tehtävä", use_container_width=True):
            del st.session_state.tehtavat[poistettava_tehtava]
            tallenna_data()
            st.success(f"Tehtävä '{poistettava_tehtava}' poistettu.")
            st.rerun()

# ══════════════════════════════════════════════════════════════
# VÄLILEHTI 3: HISTORIA
# ══════════════════════════════════════════════════════════════
with tab_historia:
    st.subheader("📜 Tapahtumahistoria")
    if not st.session_state.historia:
        st.info("Ei vielä tapahtumia. Merkitse ensimmäinen kotityö! 🏠")
    else:
        suodatin_vaihtoehdot = ["Kaikki"] + lapset() + ["Vain ansaitut", "Vain käytetty", "Vain hylätyt"]
        suodatin = st.selectbox("Näytä:", suodatin_vaihtoehdot)

        for merkinta in st.session_state.historia:
            if suodatin in lapset() and merkinta["tekija"] != suodatin:
                continue
            if suodatin == "Vain ansaitut" and merkinta["tyyppi"] != "ansaittu":
                continue
            if suodatin == "Vain käytetty" and merkinta["tyyppi"] != "käytetty":
                continue
            if suodatin == "Vain hylätyt" and merkinta["tyyppi"] != "hylätty":
                continue

            if merkinta["tyyppi"] == "ansaittu":
                ikoni = "✅"
                min_teksti = f'<span style="color:#10B981">+{merkinta["minuutit"]} min</span>'
            elif merkinta["tyyppi"] == "käytetty":
                ikoni = "🎮"
                min_teksti = f'<span style="color:#F59E0B">-{merkinta["minuutit"]} min</span>' if merkinta["minuutit"] > 0 else ""
            else:
                ikoni = "❌"
                min_teksti = ""

            st.markdown(f"""
            <div class="historia-rivi">
                {ikoni} <strong>{merkinta['tekija']}</strong> — {merkinta['tapahtuma']}
                &nbsp;{min_teksti}
                &nbsp;<span style="color:#475569;font-size:0.8rem">· {merkinta['aika']}</span>
            </div>
            """, unsafe_allow_html=True)