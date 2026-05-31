import streamlit as st
import json
import os

# 1. Tiedostotallennuksen asetukset
DATA_FILE = "peliaika_data.json"

def lataa_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "saldot": {"Poika 1": 0, "Poika 2": 0},
        "odottavat": [],
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
        "tehtavat": st.session_state.tehtavat
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Alustetaan data sovelluksen muistiin tiedostosta
if "data_ladattu" not in st.session_state:
    alustettu_data = lataa_data()
    st.session_state.saldot = alustettu_data["saldot"]
    st.session_state.odottavat = alustettu_data["odottavat"]
    st.session_state.tehtavat = alustettu_data["tehtavat"]
    st.session_state.data_ladattu = True

# --- SOVELLUKSEN KÄYTTÖLIITTYMÄ ---
st.set_page_config(page_title="Peliaikapankki", page_icon="🎮")
st.title("🎮 Perheen Peliaikapankki")

# Saldot
st.subheader("📊 Nykyiset peliaikasaldot")
col1, col2 = st.columns(2)
with col1:
    st.metric(label="Poika 1 saldo", value=f"{st.session_state.saldot['Poika 1']} min")
with col2:
    st.metric(label="Poika 2 saldo", value=f"{st.session_state.saldot['Poika 2']} min")

st.markdown("---")

# Poikien näkymä
st.subheader("🚀 Merkitse kotityö tehdyksi")
tekija = st.selectbox("Kuka teki työn?", ["Valitse...", "Poika 1", "Poika 2"])

# Luodaan poikia varten selkeät selitteet, joissa näkyy minuuttimäärä
tehtava_vaihtoehdot = {f"{nimi} (+{minuutit} min)": nimi for nimi, minuutit in st.session_state.tehtavat.items()}
valittu_selite = st.selectbox("Mikä työ tehtiin?", list(tehtava_vaihtoehdot.keys()))

if st.button("Lähetä vanhemman hyväksyttäväksi"):
    if tekija != "Valitse...":
        # Haetaan alkuperäinen tehtävän nimi selitteen perusteella
        alkuperainen_nimi = tehtava_vaihtoehdot[valittu_selite]
        pisteet = st.session_state.tehtavat[alkuperainen_nimi]
        
        st.session_state.odottavat.append({
            "id": len(st.session_state.odottavat) + 1,
            "tekija": tekija,
            "tyo": alkuperainen_nimi,
            "minuutit": pisteet
        })
        tallenna_data()
        st.success(f"Hienoa {tekija}! Työ '{alkuperainen_nimi}' lähetetty tarkistettavaksi.")
        st.rerun()
    else:
        st.error("Valitse ensin kuka työn teki!")

st.markdown("---")

# Vanhemman näkymä
st.subheader("🛡️ Vanhemman hallintapaneeli")
vanhempi_paikalla = st.checkbox("Olen vanhempi (Avaa työkaluvalikko)")

if vanhempi_paikalla:
    st.write("### 📋 Odottavat työt")
    if not st.session_state.odottavat:
        st.info("Ei odottavia töitä.")
    else:
        for tyo_item in list(st.session_state.odottavat):
            st.warning(f"**{tyo_item['tekija']}** teki työn: *{tyo_item['tyo']}* (+{tyo_item['minuutit']} min)")
            c1, c2 = st.columns(2)
            with c1:
                if st.button(f"👍 Hyväksy ({tyo_item['id']})", key=f"hyv_{tyo_item['id']}"):
                    st.session_state.saldot[tyo_item['tekija']] += tyo_item['minuutit']
                    st.session_state.odottavat.remove(tyo_item)
                    tallenna_data()
                    st.rerun()
            with c2:
                if st.button(f"👎 Hylkää ({tyo_item['id']})", key=f"hyl_{tyo_item['id']}"):
                    st.session_state.odottavat.remove(tyo_item)
                    tallenna_data()
                    st.rerun()

    st.markdown("---")
    st.write("### 🛠️ Hallitse tehtäviä")
    uusi_nimi = st.text_input("Tehtävän nimi (esim. Ruohonleikkuu)")
    uudet_minuutit = st.number_input("Peliaika minuutteina", min_value=5, max_value=180, value=15, step=5)
    
    if st.button("Tallenna uusi tehtävä"):
        if uusi_nimi:
            st.session_state.tehtavat[uusi_nimi] = uudet_minuutit
            tallenna_data()
            st.success(f"Tehtävä '{uusi_nimi}' lisätty!")
            st.rerun()

    # Myös poistovalikossa näytetään dynaamisesti nykyiset tehtävät
    poistettava_tehtava = st.selectbox("Valitse poistettava tehtävä", list(st.session_state.tehtavat.keys()))
    if st.button("❌ Poista valittu tehtävä"):
        del st.session_state.tehtavat[poistettava_tehtava]
        tallenna_data()
        st.success(f"Tehtävä '{poistettava_tehtava}' poistettu.")
        st.rerun()