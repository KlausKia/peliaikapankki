import streamlit as st
import json
import os
from datetime import datetime

DATA_FILE = "peliaika_data.json"
SOVELLUKSEN_PIN = "4321"
VANHEMMAN_PIN = "2411"
TAVOITE_MIN = 90

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
    merkinta = {
        "aika": datetime.now().strftime("%d.%m.%Y %H:%M"),
        "tekija": tekija,
        "tapahtuma": tapahtuma,
        "minuutit": minuutit,
        "tyyppi": tyyppi
    }
    st.session_state.historia.insert(0, merkinta)
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
    st.session_state.sovellus_kirjautunut = False

# Apufunktio: lista lapsista
def lapset():
    return list(st.session_state.saldot.keys())

# --- SOVELLUKSEN KÄYTTÖLIITTYMÄ ---
st.set_page_config(page_title="Peliaikapankki", page_icon="🎮", layout="centered")

# --- SISÄÄNKIRJAUTUMISPORTTI ---
if not st.session_state.sovellus_kirjautunut:
    st.title("🎮 Perheen Peliaikapankki")
    st.markdown("### 🔐 Kirjaudu sisään")
    sovellus_pin = st.text_input("PIN-koodi", type="password", max_chars=4, key="sovellus_pin")
    if st.button("Kirjaudu", use_container_width=True):
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
    st.subheader("📊 Peliaikasaldot")

    cols = st.columns(len(lapset()))
    for i, nimi in enumerate(lapset()):
        with cols[i]:
            saldo = st.session_state.saldot[nimi]
            st.metric(label=f"🎮 {nimi}", value=f"{saldo} min")
            progress = min(saldo / TAVOITE_MIN, 1.0)
            st.progress(progress, text=f"Tavoite: {TAVOITE_MIN} min ({int(progress*100)}%)")

    st.markdown("---")

    st.subheader("✅ Merkitse kotityö tehdyksi")
    tekija = st.selectbox("Kuka teki työn?", ["Valitse..."] + lapset())

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

    if not st.session_state.vanhempi_kirjautunut:
        st.info("Syötä PIN-koodi avataksesi vanhemman hallinnan.")
        pin_syote = st.text_input("PIN-koodi", type="password", max_chars=4, key="pin_input")
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

        # Nimen muuttaminen
        st.write("**Muuta lapsen nimeä:**")
        muutettava = st.selectbox("Valitse lapsi", lapset(), key="muutettava_lapsi")
        uusi_lapsen_nimi = st.text_input("Uusi nimi", value=muutettava, key="uusi_lapsen_nimi")
        if st.button("✏️ Tallenna uusi nimi", use_container_width=True):
            uusi_lapsen_nimi = uusi_lapsen_nimi.strip()
            if uusi_lapsen_nimi and uusi_lapsen_nimi != muutettava:
                if uusi_lapsen_nimi in st.session_state.saldot:
                    st.error(f"Nimi '{uusi_lapsen_nimi}' on jo käytössä!")
                else:
                    # Päivitetään saldot
                    vanha_saldo = st.session_state.saldot.pop(muutettava)
                    st.session_state.saldot[uusi_lapsen_nimi] = vanha_saldo
                    # Päivitetään odottavat
                    for tyo in st.session_state.odottavat:
                        if tyo["tekija"] == muutettava:
                            tyo["tekija"] = uusi_lapsen_nimi
                    # Päivitetään historia
                    for merkinta in st.session_state.historia:
                        if merkinta["tekija"] == muutettava:
                            merkinta["tekija"] = uusi_lapsen_nimi
                    tallenna_data()
                    st.success(f"Nimi muutettu: '{muutettava}' → '{uusi_lapsen_nimi}'")
                    st.rerun()
            elif uusi_lapsen_nimi == muutettava:
                st.info("Nimi on jo sama.")

        st.write("")

        # Uuden lapsen lisääminen
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
                    st.success(f"'{uuden_nimi}' lisätty! Saldo alkaa nollasta.")
                    st.rerun()
            else:
                st.error("Syötä nimi ensin.")

        st.write("")

        # Lapsen poistaminen
        st.write("**Poista lapsi:**")
        if len(lapset()) > 1:
            poistettava_lapsi = st.selectbox("Valitse poistettava", lapset(), key="poistettava_lapsi")
            poisto_varmistus = st.checkbox(f"Vahvistan poiston – '{poistettava_lapsi}' ja hänen saldонsa poistetaan")
            if st.button("🗑️ Poista lapsi", disabled=not poisto_varmistus, use_container_width=True):
                del st.session_state.saldot[poistettava_lapsi]
                # Poistetaan myös odottavat ko. lapselta
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
                min_teksti = f"+{merkinta['minuutit']} min"
            elif merkinta["tyyppi"] == "käytetty":
                ikoni = "🎮"
                min_teksti = f"-{merkinta['minuutit']} min" if merkinta['minuutit'] > 0 else ""
            else:
                ikoni = "❌"
                min_teksti = ""

            st.write(f"{ikoni} **{merkinta['tekija']}** — {merkinta['tapahtuma']} {min_teksti} _{merkinta['aika']}_")
