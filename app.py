import streamlit as st
import json
import os
from datetime import datetime

DATA_FILE = "peliaika_data.json"
SOVELLUKSEN_PIN = "4321"
VANHEMMAN_PIN = "2411"
TAVOITE_MIN = 90

KATEGORIAT = ["Sisätyöt", "Ulkotyöt", "Urheilu"]
KATEGORIA_IKONIT = {"Sisätyöt": "🏠", "Ulkotyöt": "🌿", "Urheilu": "⚽"}

# Värit kullekin lapselle (ensimmäiset kaksi + fallback)
LAPSI_VARIT = ["#7C3AED", "#0EA5E9", "#10B981", "#F59E0B", "#EF4444"]

CSS = """
<style>
/* Yleiset */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0F0F1A;
}
h1 { font-size: 2rem !important; }

/* Saldokortit */
.saldo-kortti {
    background: linear-gradient(135deg, var(--kortti-vari) 0%, #1A1A2E 100%);
    border: 1px solid var(--kortti-vari);
    border-radius: 16px;
    padding: 20px 16px 16px 16px;
    margin-bottom: 12px;
    text-align: center;
}
.saldo-nimi {
    font-size: 1rem;
    color: #CBD5E1;
    margin-bottom: 4px;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.saldo-arvo {
    font-size: 2.6rem;
    font-weight: 800;
    color: #FFFFFF;
    line-height: 1.1;
}
.saldo-yksikko {
    font-size: 1rem;
    color: #94A3B8;
    font-weight: 400;
}

/* Edistymispalkki */
.prog-container {
    background: #2D2D4A;
    border-radius: 99px;
    height: 12px;
    margin: 10px 0 6px 0;
    overflow: hidden;
}
.prog-bar {
    height: 12px;
    border-radius: 99px;
    background: linear-gradient(90deg, var(--kortti-vari), #A78BFA);
    transition: width 0.5s ease;
}
.prog-teksti {
    font-size: 0.75rem;
    color: #94A3B8;
    text-align: right;
}

/* Kirjautumissivu */
.login-box {
    background: #1A1A2E;
    border: 1px solid #7C3AED;
    border-radius: 20px;
    padding: 32px 24px;
    max-width: 340px;
    margin: 60px auto 0 auto;
    text-align: center;
}
.login-otsikko {
    font-size: 1.4rem;
    font-weight: 700;
    color: #E2E8F0;
    margin-bottom: 4px;
}
.login-alaotsikko {
    font-size: 0.85rem;
    color: #64748B;
    margin-bottom: 20px;
}

/* Odottava työ -kortti */
.odottava-kortti {
    background: #1E1B3A;
    border-left: 4px solid #F59E0B;
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 10px;
}
.historia-rivi {
    background: #1A1A2E;
    border-radius: 8px;
    padding: 8px 12px;
    margin-bottom: 6px;
    font-size: 0.9rem;
}
</style>
"""

def lataa_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "saldot": {"Poika 1": 0, "Poika 2": 0},
        "odottavat": [],
        "historia": [],
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
    st.session_state.historia = st.session_state.historia[:100]

def migraatio_tehtavat():
    for nimi, arvo in st.session_state.tehtavat.items():
        if isinstance(arvo, int):
            st.session_state.tehtavat[nimi] = {"minuutit": arvo, "kategoria": "Sisätyöt", "bonus": False}

def saldo_kortti_html(nimi, saldo, vari):
    progress = min(saldo / TAVOITE_MIN, 1.0)
    bar_width = int(progress * 100)
    return f"""
    <div class="saldo-kortti" style="--kortti-vari: {vari};">
        <div class="saldo-nimi">🎮 {nimi}</div>
        <div class="saldo-arvo">{saldo}<span class="saldo-yksikko"> min</span></div>
        <div class="prog-container">
            <div class="prog-bar" style="width: {bar_width}%;"></div>
        </div>
        <div class="prog-teksti">{bar_width}% tavoitteesta ({TAVOITE_MIN} min)</div>
    </div>
    """

# Alustetaan data
if "data_ladattu" not in st.session_state:
    alustettu_data = lataa_data()
    st.session_state.saldot = alustettu_data["saldot"]
    st.session_state.odottavat = alustettu_data["odottavat"]
    st.session_state.historia = alustettu_data.get("historia", [])
    st.session_state.tehtavat = alustettu_data["tehtavat"]
    st.session_state.data_ladattu = True
    st.session_state.vanhempi_kirjautunut = False
    st.session_state.sovellus_kirjautunut = False

migraatio_tehtavat()

def lapset():
    return list(st.session_state.saldot.keys())

# --- KÄYTTÖLIITTYMÄ ---
st.set_page_config(page_title="Peliaikapankki", page_icon="🎮", layout="centered")
st.markdown(CSS, unsafe_allow_html=True)

# --- SISÄÄNKIRJAUTUMISPORTTI ---
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
        sovellus_pin = st.text_input("PIN-koodi", type="password", max_chars=4, key="sovellus_pin", label_visibility="collapsed", placeholder="• • • •")
        if st.button("Kirjaudu sisään 🔓", use_container_width=True):
            if sovellus_pin == SOVELLUKSEN_PIN:
                st.session_state.sovellus_kirjautunut = True
                st.rerun()
            else:
                st.error("Väärä PIN-koodi!")
    st.stop()

st.title("🎮 Perheen Peliaikapankki")
tab_pojat, tab_vanhempi, tab_historia = st.tabs(["🚀 Lapset", "🛡️ Vanhempi", "📜 Historia"])

# ============================================================
# VÄLILEHTI 1: LAPSET
# ============================================================
with tab_pojat:
    # Saldokortit
    cols = st.columns(len(lapset()))
    for i, nimi in enumerate(lapset()):
        vari = LAPSI_VARIT[i % len(LAPSI_VARIT)]
        saldo = st.session_state.saldot[nimi]
        with cols[i]:
            st.markdown(saldo_kortti_html(nimi, saldo, vari), unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("✅ Merkitse kotityö tehdyksi")
    tekija = st.selectbox("Kuka teki työn?", ["Valitse..."] + lapset())

    tehtava_valinnat = []
    for kat in KATEGORIAT:
        ikoni = KATEGORIA_IKONIT[kat]
        for nimi, tiedot in sorted(st.session_state.tehtavat.items(), key=lambda x: x[1]["minuutit"]):
            if tiedot["kategoria"] == kat:
                bonus_merkki = " ⭐ BONUS" if tiedot["bonus"] else ""
                tehtava_valinnat.append(f"{ikoni} {kat} — {nimi} (+{tiedot['minuutit']} min){bonus_merkki}")

    valittu_selite = st.selectbox("Mikä työ tehtiin?", tehtava_valinnat)

    if st.button("📨 Lähetä vanhemman hyväksyttäväksi", use_container_width=True):
        if tekija != "Valitse...":
            alkuperainen_nimi = None
            for nimi, tiedot in st.session_state.tehtavat.items():
                kat = tiedot["kategoria"]
                ikoni = KATEGORIA_IKONIT[kat]
                bonus_merkki = " ⭐ BONUS" if tiedot["bonus"] else ""
                if valittu_selite == f"{ikoni} {kat} — {nimi} (+{tiedot['minuutit']} min){bonus_merkki}":
                    alkuperainen_nimi = nimi
                    break
            if alkuperainen_nimi:
                pisteet = st.session_state.tehtavat[alkuperainen_nimi]["minuutit"]
                on_bonus = st.session_state.tehtavat[alkuperainen_nimi]["bonus"]
                st.session_state.odottavat.append({
                    "id": len(st.session_state.odottavat) + 1,
                    "tekija": tekija,
                    "tyo": alkuperainen_nimi,
                    "minuutit": pisteet,
                    "bonus": on_bonus,
                    "aika": datetime.now().strftime("%d.%m.%Y %H:%M")
                })
                tallenna_data()
                st.success(f"Hienoa {tekija}! 🎉 Työ '{alkuperainen_nimi}' lähetetty tarkistettavaksi.")
                st.rerun()
        else:
            st.error("Valitse ensin kuka työn teki!")

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

# ============================================================
# VÄLILEHTI 2: VANHEMPI
# ============================================================
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

        # --- OSA 1: Töiden hyväksyntä ---
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
                        tallenna_data()
                        st.balloons()
                        st.rerun()
                with c2:
                    if st.button(f"👎 Hylkää", key=f"hyl_{tyo_item['id']}"):
                        lisaa_historia(tyo_item['tekija'], tyo_item['tyo'], tyo_item['minuutit'], "hylätty")
                        st.session_state.odottavat.remove(tyo_item)
                        tallenna_data()
                        st.rerun()

        st.markdown("---")

        # --- OSA 2: Peliajan käyttäminen ---
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

        # --- OSA 3: Lasten hallinta ---
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
            poisto_varmistus = st.checkbox(f"Vahvistan poiston – '{poistettava_lapsi}' ja hänen saldонsa poistetaan")
            if st.button("🗑️ Poista lapsi", disabled=not poisto_varmistus, use_container_width=True):
                del st.session_state.saldot[poistettava_lapsi]
                st.session_state.odottavat = [t for t in st.session_state.odottavat if t["tekija"] != poistettava_lapsi]
                tallenna_data()
                st.success(f"'{poistettava_lapsi}' poistettu.")
                st.rerun()
        else:
            st.info("Vähintään yksi lapsi täytyy olla listalla.")

        st.markdown("---")

        # --- OSA 4: Saldojen nollaus ---
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

        # --- OSA 5: Tehtävälistan hallinta ---
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

# ============================================================
# VÄLILEHTI 3: HISTORIA
# ============================================================
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
