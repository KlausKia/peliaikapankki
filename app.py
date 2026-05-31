import streamlit as st
import json
import os
from datetime import datetime

DATA_FILE = "peliaika_data.json"
VANHEMMAN_PIN = "2411"  # Vaihda tämä haluamaksesi!

def lataa_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "saldot": {"Poika 1": 0, "Poika 2": 0},
        "odottavat": [],
        "historia": [],
        "tehtavat": {
            "Kodin imurointi": 20,
            "Pölyjen pyyhintä": 15,
            "Auton imurointi": 30,
            "Auton pesu ulkoa": 45,
            "Autotallin siivous": 60,
            "Pihavajan siivous": 45,
            "Tiskikoneen tyhjennys": 10
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
    """Lisää tapahtuma historiaan. tyyppi: 'ansaittu', 'käytetty', 'hylätty'"""
    merkinta = {
        "aika": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "tekija": tekija,
        "tapahtuma": tapahtuma,
        "minuutit": minuutit,
        "tyyppi": tyyppi
    }
    st.session_state.historia.insert(0, merkinta)  # Uusin ensin
    # Pidetään historia max 100 merkinnässä
    st.session_state.historia = st.session_state.historia[:100]

# Alustetaan data
if "data_ladattu" not in st.session_state:
    alustettu_data = lataa_data()
    st.session_state.saldot = alustettu_data["saldot"]
    st.session_state.odottavat = alustettu_data["odottavat"]
    st.session_state.historia = alustettu_data.get("historia", [])
    st.session_state.tehtavat = alustettu_data["tehtavat"]
    st.session_state.data_ladattu = True
    st.session_state.vanhempi_kirjautunut = False

# --- SOVELLUKSEN KÄYTTÖLIITTYMÄ ---
st.set_page_config(page_title="Peliaikapankki", page_icon="🎮", layout="centered")
st.title("🎮 Perheen Peliaikapankki")

# Välilehdet
tab_pojat, tab_vanhempi, tab_historia = st.tabs(["🚀 Pojat", "🛡️ Vanhempi", "📜 Historia"])

# ============================================================
# VÄLILEHTI 1: POJAT
# ============================================================
with tab_pojat:
    # Saldot ja edistymispalkki
    st.subheader("📊 Peliaikasaldot")
    
    TAVOITE_MIN = 90  # Minuuttia – voit muuttaa tätä
    
    col1, col2 = st.columns(2)
    with col1:
        saldo1 = st.session_state.saldot["Poika 1"]
        st.metric(label="🎮 Poika 1", value=f"{saldo1} min")
        progress1 = min(saldo1 / TAVOITE_MIN, 1.0)
        st.progress(progress1, text=f"Tavoite: {TAVOITE_MIN} min ({int(progress1*100)}%)")
    with col2:
        saldo2 = st.session_state.saldot["Poika 2"]
        st.metric(label="🎮 Poika 2", value=f"{saldo2} min")
        progress2 = min(saldo2 / TAVOITE_MIN, 1.0)
        st.progress(progress2, text=f"Tavoite: {TAVOITE_MIN} min ({int(progress2*100)}%)")

    st.markdown("---")

    # Kotityön merkitseminen
    st.subheader("✅ Merkitse kotityö tehdyksi")
    tekija = st.selectbox("Kuka teki työn?", ["Valitse...", "Poika 1", "Poika 2"])

    tehtava_vaihtoehdot = {f"{nimi} (+{minuutit} min)": nimi for nimi, minuutit in st.session_state.tehtavat.items()}
    valittu_selite = st.selectbox("Mikä työ tehtiin?", list(tehtava_vaihtoehdot.keys()))

    if st.button("📨 Lähetä vanhemman hyväksyttäväksi", use_container_width=True):
        if tekija != "Valitse...":
            alkuperainen_nimi = tehtava_vaihtoehdot[valittu_selite]
            pisteet = st.session_state.tehtavat[alkuperainen_nimi]
            st.session_state.odottavat.append({
                "id": len(st.session_state.odottavat) + 1,
                "tekija": tekija,
                "tyo": alkuperainen_nimi,
                "minuutit": pisteet,
                "aika": datetime.now().strftime("%d.%m.%Y %H:%M")
            })
            tallenna_data()
            st.success(f"Hienoa {tekija}! 🎉 Työ '{alkuperainen_nimi}' lähetetty tarkistettavaksi.")
            st.rerun()
        else:
            st.error("Valitse ensin kuka työn teki!")

    # Odottavat työt pojille näkyviin
    if st.session_state.odottavat:
        st.markdown("---")
        st.subheader("⏳ Odottaa hyväksyntää")
        for tyo in st.session_state.odottavat:
            st.info(f"**{tyo['tekija']}**: {tyo['tyo']} (+{tyo['minuutit']} min) — lähetetty {tyo.get('aika','')}")

# ============================================================
# VÄLILEHTI 2: VANHEMPI
# ============================================================
with tab_vanhempi:
    st.subheader("🛡️ Vanhemman hallintapaneeli")

    # PIN-kirjautuminen
    if not st.session_state.vanhempi_kirjautunut:
        st.info("Syötä PIN-koodi avataksesi vanhemman hallinnan.")
        pin_syote = st.text_input("PIN-koodi", type="password", max_chars=4, key="pin_input")
        if st.button("🔓 Kirjaudu", use_container_width=True):
            if pin_syote == VANHEMMAN_PIN:
                st.session_state.vanhempi_kirjautunut = True
                st.rerun()
            else:
                st.error("Väärä PIN-koodi!")
        st.caption("Vinkki: oletuskoodi on 1234. Vaihda se suoraan app.py-tiedostossa.")
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
                st.warning(f"**{tyo_item['tekija']}** teki työn: *{tyo_item['tyo']}* (+{tyo_item['minuutit']} min) — {tyo_item.get('aika','')}")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button(f"👍 Hyväksy", key=f"hyv_{tyo_item['id']}"):
                        st.session_state.saldot[tyo_item['tekija']] += tyo_item['minuutit']
                        lisaa_historia(tyo_item['tekija'], tyo_item['tyo'], tyo_item['minuutit'], "ansaittu")
                        st.session_state.odottavat.remove(tyo_item)
                        tallenna_data()
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
        vahennettava_pelaaja = st.selectbox("Kuka pelaa?", ["Poika 1", "Poika 2"], key="pelaaja_vahennys")
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

        # --- OSA 3: Saldojen nollaus ---
        st.write("### 🚨 Saldojen nollaus")
        varmistus = st.checkbox("Vahvistan, että haluan tyhjentää molempien saldot nollaan")
        if st.button("🚨 NOLLAA MOLEMPIEN SALDOT", disabled=not varmistus, use_container_width=True):
            lisaa_historia("Molemmat", "Saldot nollattu", 0, "käytetty")
            st.session_state.saldot["Poika 1"] = 0
            st.session_state.saldot["Poika 2"] = 0
            tallenna_data()
            st.success("Saldot nollattu!")
            st.rerun()

        st.markdown("---")

        # --- OSA 4: Tehtävälistan hallinta ---
        st.write("### 🛠️ Hallitse tehtäviä")
        uusi_nimi = st.text_input("Tehtävän nimi (esim. Ruohonleikkuu)")
        uudet_minuutit = st.number_input("Peliaika minuutteina", min_value=5, max_value=180, value=15, step=5)

        if st.button("➕ Lisää tehtävä", use_container_width=True):
            if uusi_nimi:
                st.session_state.tehtavat[uusi_nimi] = uudet_minuutit
                tallenna_data()
                st.success(f"Tehtävä '{uusi_nimi}' lisätty!")
                st.rerun()

        poistettava_tehtava = st.selectbox("Valitse poistettava tehtävä", list(st.session_state.tehtavat.keys()))
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
        # Suodatus
        suodatin = st.selectbox("Näytä:", ["Kaikki", "Poika 1", "Poika 2", "Vain ansaitut", "Vain käytetty", "Vain hylätyt"])

        for merkinta in st.session_state.historia:
            # Suodatuslogiikka
            if suodatin == "Poika 1" and merkinta["tekija"] != "Poika 1":
                continue
            if suodatin == "Poika 2" and merkinta["tekija"] != "Poika 2":
                continue
            if suodatin == "Vain ansaitut" and merkinta["tyyppi"] != "ansaittu":
                continue
            if suodatin == "Vain käytetty" and merkinta["tyyppi"] != "käytetty":
                continue
            if suodatin == "Vain hylätyt" and merkinta["tyyppi"] != "hylätty":
                continue

            # Värikoodaus tyypin mukaan
            if merkinta["tyyppi"] == "ansaittu":
                ikoni = "✅"
                min_teksti = f"+{merkinta['minuutit']} min"
            elif merkinta["tyyppi"] == "käytetty":
                ikoni = "🎮"
                min_teksti = f"-{merkinta['minuutit']} min" if merkinta['minuutit'] > 0 else ""
            else:  # hylätty
                ikoni = "❌"
                min_teksti = ""

            st.write(f"{ikoni} **{merkinta['tekija']}** — {merkinta['tapahtuma']} {min_teksti} _{merkinta['aika']}_")
