import streamlit as st
from datetime import datetime
import db

# ── SIVUN ALUSTUS ────────────────────────────────────────────────────
st.set_page_config(page_title="ChoreQuest", page_icon="🎮", layout="centered")

KATEGORIAT    = ["Sisätyöt", "Ulkotyöt", "Urheilu"]
KATEGORIA_IKONIT = {"Sisätyöt": "🏠", "Ulkotyöt": "🌿", "Urheilu": "⚽"}
LAPSI_VARIT   = ["#7C3AED", "#0EA5E9", "#10B981", "#F59E0B", "#EF4444"]

SAAVUTUKSET = [
    ("eka_tyo",  "Ensiaskel",      "🌱", "Ensimmäinen työ tehty!"),
    ("tyo_5",    "Ahkera apuri",   "⭐", "5 työtä suoritettu"),
    ("tyo_10",   "Kotityösankari", "🏆", "10 työtä suoritettu"),
    ("tyo_25",   "Legendaarinen",  "👑", "25 työtä suoritettu"),
    ("putki_3",  "3 pv putki",     "🔥", "Töitä 3 päivänä peräkkäin"),
    ("putki_5",  "5 pv putki",     "🔥🔥","Töitä 5 päivänä peräkkäin"),
    ("putki_7",  "Viikon mestari", "💎", "Töitä 7 päivänä peräkkäin"),
]

CSS = """
<style>
html, body, [data-testid="stAppViewContainer"] { background-color: #0F0F1A; }
h1 { font-size: 2rem !important; }
.login-box {
    background: #1A1A2E; border: 1px solid #7C3AED; border-radius: 20px;
    padding: 32px 24px; max-width: 360px; margin: 40px auto 0 auto; text-align: center;
}
.login-otsikko    { font-size: 1.4rem; font-weight: 700; color: #E2E8F0; margin-bottom: 4px; }
.login-alaotsikko { font-size: 0.85rem; color: #64748B; margin-bottom: 20px; }
.odottava-kortti  { background: #1E1B3A; border-left: 4px solid #F59E0B; border-radius: 10px; padding: 12px 16px; margin-bottom: 10px; }
.historia-rivi    { background: #1A1A2E; border-radius: 8px; padding: 8px 12px; margin-bottom: 6px; font-size: 0.9rem; }
.raportti-kortti  { background: #1A1A2E; border: 1px solid #2D2D4A; border-radius: 12px; padding: 16px; margin-bottom: 10px; }
.raportti-otsikko { font-size: 0.8rem; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; }
.raportti-arvo    { font-size: 1.8rem; font-weight: 700; color: #E2E8F0; }
.vahvistus-kortti { background: linear-gradient(135deg, #1E1B3A, #2D1B69); border: 2px solid #7C3AED; border-radius: 20px; padding: 28px 20px; text-align: center; margin-bottom: 16px; }
.vahvistus-tehtava { font-size: 1.3rem; font-weight: 700; color: #E2E8F0; margin-bottom: 6px; }
.vahvistus-min    { font-size: 2rem; font-weight: 800; color: #A78BFA; }
.vahvistus-teksti { font-size: 0.85rem; color: #64748B; margin-top: 4px; }
.badge { display: inline-block; background: #1E1B3A; border: 1px solid #3D3A6A; border-radius: 10px; padding: 8px 10px; margin: 4px; text-align: center; min-width: 80px; }
.badge.saavutettu { border-color: #7C3AED; background: linear-gradient(135deg, #2D1B69, #1A1A2E); }
.badge-ikoni { font-size: 1.5rem; }
.badge-nimi  { font-size: 0.7rem; color: #94A3B8; margin-top: 2px; }
.badge.saavutettu .badge-nimi { color: #C4B5FD; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ── APUFUNKTIOT ──────────────────────────────────────────────────────
def saldo_kortti_html(nimi, saldo, vari, tavoite, valittu=False, putki=0):
    progress  = min(saldo / tavoite, 1.0) if tavoite > 0 else 0
    bar_width = int(progress * 100)
    tuli      = ("🔥" * min(putki, 3)) if putki > 0 else ""
    putki_html = f'<div style="font-size:0.8rem;color:#F59E0B;margin-top:4px;">{tuli} {putki} pv putki</div>' if putki > 0 else ""
    reuna  = f"3px solid {vari}" if valittu else f"1px solid {vari}"
    shadow = f"0 0 0 2px {vari}, 0 8px 24px rgba(0,0,0,0.5)" if valittu else "none"
    nosto  = "translateY(-3px)" if valittu else "translateY(0)"
    check  = '<div style="position:absolute;top:10px;right:12px;font-size:1.1rem;">✅</div>' if valittu else ""
    return f"""<div style="background:linear-gradient(135deg,{vari}33 0%,#1A1A2E 100%);border:{reuna};border-radius:16px;padding:20px 16px 16px 16px;margin-bottom:8px;text-align:center;position:relative;box-shadow:{shadow};transform:{nosto};transition:transform 0.2s,box-shadow 0.2s;">
{check}
<div style="font-size:0.85rem;color:#CBD5E1;margin-bottom:4px;font-weight:600;letter-spacing:0.05em;text-transform:uppercase;">🎮 {nimi}</div>
<div style="font-size:2.4rem;font-weight:800;color:#FFFFFF;line-height:1.1;">{saldo}<span style="font-size:0.9rem;color:#94A3B8;font-weight:400;"> min</span></div>
<div style="background:#2D2D4A;border-radius:99px;height:10px;margin:10px 0 5px 0;overflow:hidden;"><div style="height:10px;border-radius:99px;background:linear-gradient(90deg,{vari},#A78BFA);width:{bar_width}%;"></div></div>
<div style="font-size:0.75rem;color:#94A3B8;text-align:right;">{bar_width}% tavoitteesta ({tavoite} min)</div>
{putki_html}
</div>"""

def lataa_perhedata():
    fid = st.session_state.family["id"]
    st.session_state.lapset    = db.hae_lapset(fid)
    st.session_state.tehtavat  = db.hae_tehtavat(fid)
    st.session_state.odottavat = db.hae_odottavat(fid)
    st.session_state.historia  = db.hae_historia(fid)

def lapset():
    return st.session_state.get("lapset", [])

def tehtavat():
    return st.session_state.get("tehtavat", [])

def etsi_lapsi_nimella(nimi):
    return next((l for l in lapset() if l["nimi"] == nimi), None)

def etsi_tehtava_nimella(nimi):
    return next((t for t in tehtavat() if t["nimi"] == nimi), None)

# ── SESSION STATE ALUSTUS ────────────────────────────────────────────
def alusta_session():
    defaults = {
        "nakyma": "login",
        "family": None,
        "vanhempi_kirjautunut": False,
        "valittu_lapsi": None,
        "valittu_tehtava": None,
        "lahetetty": False,
        "lahetetty_lapsi": None,
        "lahetetty_tyo": None,
        "lahetetty_min": None,
        "lapset": [],
        "tehtavat": [],
        "odottavat": [],
        "historia": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

alusta_session()

# ══════════════════════════════════════════════════════════════════════
# NÄKYMÄ: KIRJAUTUMINEN
# ══════════════════════════════════════════════════════════════════════
if st.session_state.nakyma == "login":
    st.markdown("""
    <div class="login-box">
        <div style="font-size:3rem;">🎮</div>
        <div class="login-otsikko">ChoreQuest</div>
        <div class="login-alaotsikko">Kirjaudu perheen tunnuksella</div>
    </div>
    """, unsafe_allow_html=True)
    st.write("")

    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        tunnus = st.text_input("Perheen tunnus", placeholder="esim. mäkinen", key="login_tunnus")
        pin    = st.text_input("PIN-koodi", type="password", max_chars=6, placeholder="• • • •", key="login_pin")

        if st.button("🔓 Kirjaudu sisään", use_container_width=True, type="primary"):
            if not tunnus or not pin:
                st.error("Syötä tunnus ja PIN.")
            else:
                perhe = db.hae_perhe_tunnuksella(tunnus)
                if perhe is None:
                    st.error("Perhettä ei löydy. Tarkista tunnus tai luo uusi perhe.")
                elif perhe["perhe_pin"] != pin:
                    st.error("Väärä PIN-koodi!")
                else:
                    st.session_state.family = perhe
                    st.session_state.nakyma = "sovellus"
                    lataa_perhedata()
                    st.rerun()

        st.write("")
        st.markdown("<div style='text-align:center;color:#64748B;font-size:0.85rem;'>Uusi perhe?</div>", unsafe_allow_html=True)
        if st.button("✨ Luo uusi perhetunnus", use_container_width=True):
            st.session_state.nakyma = "rekisterointi"
            st.rerun()

    st.stop()

# ══════════════════════════════════════════════════════════════════════
# NÄKYMÄ: REKISTERÖINTI
# ══════════════════════════════════════════════════════════════════════
if st.session_state.nakyma == "rekisterointi":
    st.markdown("""
    <div class="login-box">
        <div style="font-size:3rem;">🏠</div>
        <div class="login-otsikko">Luo uusi perhe</div>
        <div class="login-alaotsikko">Täytä tiedot ja aloita heti</div>
    </div>
    """, unsafe_allow_html=True)
    st.write("")

    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        uusi_tunnus    = st.text_input("Perheen tunnus", placeholder="esim. mäkinen", key="rek_tunnus",
                                       help="Tällä tunnuksella kirjaudutaan sovellukseen")
        uusi_perhe_pin = st.text_input("Perheen PIN (lasten kirjautuminen)", type="password",
                                       max_chars=6, placeholder="• • • •", key="rek_perhe_pin")
        uusi_admin_pin = st.text_input("Vanhemman PIN (hallintapaneeli)", type="password",
                                       max_chars=6, placeholder="• • • •", key="rek_admin_pin")
        lapsen_nimi1   = st.text_input("Ensimmäisen lapsen nimi", placeholder="esim. Toppe", key="rek_lapsi1")
        lapsen_nimi2   = st.text_input("Toisen lapsen nimi (valinnainen)", placeholder="esim. Luppu", key="rek_lapsi2")

        if st.button("🚀 Luo perhe ja aloita!", use_container_width=True, type="primary"):
            virheet = []
            if not uusi_tunnus.strip():          virheet.append("Syötä perheen tunnus.")
            if len(uusi_perhe_pin) < 4:          virheet.append("Perheen PIN vähintään 4 merkkiä.")
            if len(uusi_admin_pin) < 4:          virheet.append("Vanhemman PIN vähintään 4 merkkiä.")
            if uusi_perhe_pin == uusi_admin_pin: virheet.append("Perheen PIN ja vanhemman PIN eivät voi olla samat.")
            if not lapsen_nimi1.strip():         virheet.append("Syötä ainakin ensimmäisen lapsen nimi.")
            if not db.tunnus_vapaa(uusi_tunnus): virheet.append(f"Tunnus '{uusi_tunnus}' on jo käytössä.")

            if virheet:
                for v in virheet:
                    st.error(v)
            else:
                try:
                    perhe = db.luo_perhe(uusi_tunnus, uusi_perhe_pin, uusi_admin_pin)
                    fid   = perhe["id"]
                    db.lisaa_lapsi(fid, lapsen_nimi1.strip())
                    if lapsen_nimi2.strip():
                        db.lisaa_lapsi(fid, lapsen_nimi2.strip())
                    st.session_state.family = perhe
                    st.session_state.nakyma = "sovellus"
                    lataa_perhedata()
                    st.success(f"Perhe '{uusi_tunnus}' luotu! Tervetuloa! 🎉")
                    st.rerun()
                except Exception as e:
                    st.error(f"Virhe luotaessa perhettä: {e}")

        if st.button("⬅️ Takaisin kirjautumiseen", use_container_width=True):
            st.session_state.nakyma = "login"
            st.rerun()

    st.stop()

# ══════════════════════════════════════════════════════════════════════
# VARSINAINEN SOVELLUS
# ══════════════════════════════════════════════════════════════════════
family    = st.session_state.family
family_id = family["id"]
tavoite   = family.get("tavoite_min", 90)

st.title("🎮 ChoreQuest")

col_title, col_logout = st.columns([4, 1])
with col_logout:
    if st.button("🚪 Ulos", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

tab_pojat, tab_vanhempi, tab_historia = st.tabs(["🚀 Lapset", "🛡️ Vanhempi", "📜 Historia"])

# ══════════════════════════════════════════════════════════════════════
# VÄLILEHTI 1: LAPSET
# ══════════════════════════════════════════════════════════════════════
with tab_pojat:

    if st.session_state.lahetetty:
        lapsi_v = st.session_state.lahetetty_lapsi
        tyo_v   = st.session_state.lahetetty_tyo
        min_v   = st.session_state.lahetetty_min
        kaikki  = lapset()
        i_v     = next((i for i, l in enumerate(kaikki) if l["nimi"] == lapsi_v), 0)
        vari_v  = LAPSI_VARIT[i_v % len(LAPSI_VARIT)]

        st.markdown(f"""
        <div style="text-align:center;padding:40px 0 20px 0;">
            <div style="font-size:4rem;">🎉</div>
            <div style="font-size:1.5rem;font-weight:800;color:#E2E8F0;margin:10px 0 4px 0;">Lähetetty!</div>
            <div style="font-size:1rem;color:#94A3B8;">Vanhempi tarkistaa työn pian.</div>
        </div>
        <div class="vahvistus-kortti" style="border-color:{vari_v};">
            <div class="vahvistus-tehtava">{tyo_v}</div>
            <div class="vahvistus-min">+{min_v} min</div>
            <div class="vahvistus-teksti">odottaa hyväksyntää</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("⬅️ Takaisin alkuun", use_container_width=True):
            st.session_state.lahetetty       = False
            st.session_state.valittu_lapsi   = None
            st.session_state.valittu_tehtava = None
            st.rerun()

    elif st.session_state.valittu_tehtava is not None:
        lapsi_obj = etsi_lapsi_nimella(st.session_state.valittu_lapsi)
        tyo_obj   = etsi_tehtava_nimella(st.session_state.valittu_tehtava)

        if not lapsi_obj or not tyo_obj:
            st.session_state.valittu_tehtava = None
            st.rerun()
        else:
            kaikki = lapset()
            i_n    = next((i for i, l in enumerate(kaikki) if l["nimi"] == lapsi_obj["nimi"]), 0)
            vari_n = LAPSI_VARIT[i_n % len(LAPSI_VARIT)]
            kat_ikoni    = KATEGORIA_IKONIT.get(tyo_obj["kategoria"], "")
            bonus_teksti = " ⭐ BONUS" if tyo_obj["bonus"] else ""

            st.markdown(f"""
            <div style="text-align:center;padding:16px 0 8px 0;">
                <div style="font-size:0.85rem;color:#64748B;text-transform:uppercase;letter-spacing:0.05em;">Vahvista työ</div>
                <div style="font-size:1.2rem;font-weight:700;color:{vari_n};margin-top:4px;">🎮 {lapsi_obj['nimi']}</div>
            </div>
            <div class="vahvistus-kortti" style="border-color:{vari_n};">
                <div style="font-size:1.5rem;">{kat_ikoni}</div>
                <div class="vahvistus-tehtava">{tyo_obj['nimi']}{bonus_teksti}</div>
                <div class="vahvistus-min" style="color:{vari_n};">+{tyo_obj['minuutit']} min</div>
                <div class="vahvistus-teksti">{tyo_obj['kategoria']}</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("📨 Lähetä vanhemman hyväksyttäväksi", use_container_width=True):
                db.lisaa_odottava(
                    family_id=family_id,
                    child_id=lapsi_obj["id"],
                    task_id=tyo_obj["id"],
                    tyo_nimi=tyo_obj["nimi"],
                    minuutit=tyo_obj["minuutit"],
                    bonus=tyo_obj["bonus"]
                )
                st.session_state.lahetetty       = True
                st.session_state.lahetetty_lapsi = lapsi_obj["nimi"]
                st.session_state.lahetetty_tyo   = tyo_obj["nimi"]
                st.session_state.lahetetty_min   = tyo_obj["minuutit"]
                lataa_perhedata()
                st.rerun()

            if st.button("⬅️ Valitse toinen tehtävä", use_container_width=True):
                st.session_state.valittu_tehtava = None
                st.rerun()

    else:
        st.markdown("<div style='text-align:center;font-size:1rem;color:#94A3B8;margin-bottom:16px;'>Klikkaa omaa laatikkoasi:</div>", unsafe_allow_html=True)

        kaikki_lapset = lapset()
        if not kaikki_lapset:
            st.info("Ei lapsia. Lisää lapsi vanhemman paneelista.")
        else:
            cols = st.columns(len(kaikki_lapset))
            for i, lapsi in enumerate(kaikki_lapset):
                vari       = LAPSI_VARIT[i % len(LAPSI_VARIT)]
                putki      = db.laske_putki(lapsi["id"], st.session_state.historia)
                on_valittu = (st.session_state.valittu_lapsi == lapsi["nimi"])

                with cols[i]:
                    st.markdown(saldo_kortti_html(
                        lapsi["nimi"], lapsi["saldo"], vari, tavoite,
                        valittu=on_valittu, putki=putki
                    ), unsafe_allow_html=True)
                    if st.button(
                        "✅ Valittu" if on_valittu else "👆 Olen tämä!",
                        key=f"pelaaja_nappi_{lapsi['id']}",
                        use_container_width=True,
                        type="primary" if on_valittu else "secondary",
                    ):
                        st.session_state.valittu_lapsi = None if on_valittu else lapsi["nimi"]
                        st.rerun()

            if st.session_state.valittu_lapsi:
                lapsi_aktiivinen = etsi_lapsi_nimella(st.session_state.valittu_lapsi)
                if lapsi_aktiivinen:
                    i_n    = next((i for i, l in enumerate(kaikki_lapset) if l["nimi"] == lapsi_aktiivinen["nimi"]), 0)
                    vari_n = LAPSI_VARIT[i_n % len(LAPSI_VARIT)]
                    st.markdown("---")
                    st.markdown(f"<div style='font-size:1.1rem;font-weight:700;color:{vari_n};margin:8px 0 12px 0;'>✨ Pelaajan {lapsi_aktiivinen['nimi']} tehtävät:</div>", unsafe_allow_html=True)

                    for kat in KATEGORIAT:
                        kat_ikoni    = KATEGORIA_IKONIT[kat]
                        kat_tehtavat = [t for t in tehtavat() if t["kategoria"] == kat]
                        if not kat_tehtavat:
                            continue
                        st.markdown(f"<div style='font-size:0.8rem;color:#94A3B8;text-transform:uppercase;letter-spacing:0.08em;margin:16px 0 8px 0;'>{kat_ikoni} {kat}</div>", unsafe_allow_html=True)
                        for tyo in sorted(kat_tehtavat, key=lambda x: x["minuutit"]):
                            bonus_merkki = " ⭐" if tyo["bonus"] else ""
                            nappi_label  = f"{tyo['nimi']}{bonus_merkki}  ·  +{tyo['minuutit']} min"
                            if st.button(nappi_label, key=f"tyonappi_{tyo['id']}", use_container_width=True):
                                st.session_state.valittu_tehtava = tyo["nimi"]
                                st.rerun()

                    if st.button("❌ Sulje tehtävälista", use_container_width=True):
                        st.session_state.valittu_lapsi = None
                        st.rerun()

        st.markdown("---")
        st.subheader("🏆 Saavutukset")
        kaikki_lapset = lapset()
        if kaikki_lapset:
            sav_cols = st.columns(len(kaikki_lapset))
            for i, lapsi in enumerate(kaikki_lapset):
                saavutetut = lapsi.get("saavutukset") or []
                with sav_cols[i]:
                    st.write(f"**{lapsi['nimi']}**")
                    badges_html = ""
                    for sav_id, sav_nimi, ikoni, kuvaus in SAAVUTUKSET:
                        on      = sav_id in saavutetut
                        css     = "badge saavutettu" if on else "badge"
                        opacity = "1.0" if on else "0.25"
                        badges_html += f'<div class="{css}" style="opacity:{opacity}" title="{kuvaus}"><div class="badge-ikoni">{ikoni}</div><div class="badge-nimi">{sav_nimi}</div></div>'
                    st.markdown(f'<div style="display:flex;flex-wrap:wrap;">{badges_html}</div>', unsafe_allow_html=True)

        odottavat = st.session_state.odottavat
        if odottavat:
            st.markdown("---")
            st.subheader("⏳ Odottaa hyväksyntää")
            for tyo in odottavat:
                lapsi_nimi   = tyo.get("children", {}).get("nimi", "?") if isinstance(tyo.get("children"), dict) else "?"
                bonus_teksti = " ⭐ BONUS" if tyo.get("bonus") else ""
                try:
                    aika_fmt = datetime.fromisoformat(tyo.get("luotu_at", "")).strftime("%d.%m.%Y %H:%M")
                except Exception:
                    aika_fmt = tyo.get("luotu_at", "")
                st.markdown(f"""
                <div class="odottava-kortti">
                    ⏳ <strong>{lapsi_nimi}</strong>: {tyo['tyo_nimi']}{bonus_teksti}
                    &nbsp;·&nbsp; <span style="color:#A78BFA">+{tyo['minuutit']} min</span>
                    &nbsp;·&nbsp; <span style="color:#64748B;font-size:0.8rem">{aika_fmt}</span>
                </div>
                """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
# VÄLILEHTI 2: VANHEMPI
# ══════════════════════════════════════════════════════════════════════
with tab_vanhempi:
    st.subheader("🛡️ Vanhemman hallintapaneeli")

    if not st.session_state.vanhempi_kirjautunut:
        st.info("Syötä vanhemman PIN-koodi.")
        col_l, col_m, col_r = st.columns([1, 2, 1])
        with col_m:
            pin_syote = st.text_input("PIN", type="password", max_chars=6, key="admin_pin_input",
                                      label_visibility="collapsed", placeholder="• • • •")
            if st.button("🔓 Kirjaudu", use_container_width=True):
                if pin_syote == family["admin_pin"]:
                    st.session_state.vanhempi_kirjautunut = True
                    st.rerun()
                else:
                    st.error("Väärä PIN-koodi!")
    else:
        if st.button("🔒 Kirjaudu ulos hallinnasta", use_container_width=True):
            st.session_state.vanhempi_kirjautunut = False
            st.rerun()

        st.markdown("---")

        st.write("### 📋 Odottavat työt")
        odottavat = st.session_state.odottavat
        if not odottavat:
            st.info("Ei odottavia töitä. 👍")
        else:
            for tyo in list(odottavat):
                lapsi_nimi   = tyo.get("children", {}).get("nimi", "?") if isinstance(tyo.get("children"), dict) else "?"
                bonus_teksti = " ⭐ BONUS" if tyo.get("bonus") else ""
                try:
                    aika_fmt = datetime.fromisoformat(tyo.get("luotu_at", "")).strftime("%d.%m.%Y %H:%M")
                except Exception:
                    aika_fmt = tyo.get("luotu_at", "")

                st.markdown(f"""
                <div class="odottava-kortti">
                    <strong>{lapsi_nimi}</strong>: {tyo['tyo_nimi']}{bonus_teksti}
                    &nbsp;·&nbsp; <span style="color:#A78BFA">+{tyo['minuutit']} min</span>
                    &nbsp;·&nbsp; <span style="color:#64748B;font-size:0.8rem">{aika_fmt}</span>
                </div>
                """, unsafe_allow_html=True)

                c1, c2 = st.columns(2)
                with c1:
                    if st.button("👍 Hyväksy", key=f"hyv_{tyo['id']}"):
                        lapsi_obj = next((l for l in lapset() if l["id"] == tyo["child_id"]), None)
                        if lapsi_obj:
                            db.paivita_saldo(lapsi_obj["id"], lapsi_obj["saldo"] + tyo["minuutit"])
                            db.lisaa_historia(family_id, lapsi_obj["id"], lapsi_obj["nimi"],
                                              tyo["tyo_nimi"], tyo["minuutit"], "ansaittu")
                            if tyo.get("bonus") and tyo.get("task_id"):
                                db.poista_tehtava(tyo["task_id"])
                            db.poista_odottava(tyo["id"])
                            lataa_perhedata()
                            uudet = db.tarkista_saavutukset(lapsi_obj, st.session_state.historia)
                            if uudet:
                                nimet = [s[1] for s in SAAVUTUKSET if s[0] in uudet]
                                st.success(f"🏆 Uusi saavutus: {', '.join(nimet)}!")
                            st.balloons()
                            st.rerun()
                with c2:
                    if st.button("👎 Hylkää", key=f"hyl_{tyo['id']}"):
                        lapsi_obj = next((l for l in lapset() if l["id"] == tyo["child_id"]), None)
                        if lapsi_obj:
                            db.lisaa_historia(family_id, lapsi_obj["id"], lapsi_obj["nimi"],
                                              tyo["tyo_nimi"], tyo["minuutit"], "hylätty")
                        db.poista_odottava(tyo["id"])
                        lataa_perhedata()
                        st.rerun()

        st.markdown("---")

        st.write("### 📈 Viikkoraportti")
        viikko_valinta = st.radio("Viikko:", ["Tämä viikko", "Edellinen viikko"], horizontal=True)
        taaksepain     = 0 if viikko_valinta == "Tämä viikko" else 1

        for i, lapsi in enumerate(lapset()):
            min_v, tyot_v, vk_alku, vk_loppu = db.viikko_data(lapsi["id"], st.session_state.historia, taaksepain)
            min_ed, _, _, _                   = db.viikko_data(lapsi["id"], st.session_state.historia, taaksepain + 1)
            muutos      = min_v - min_ed
            muutos_txt  = f"+{muutos}" if muutos >= 0 else str(muutos)
            muutos_vari = "#10B981" if muutos >= 0 else "#EF4444"
            putki       = db.laske_putki(lapsi["id"], st.session_state.historia)
            vari        = LAPSI_VARIT[i % len(LAPSI_VARIT)]

            st.markdown(f"""
            <div class="raportti-kortti" style="border-color:{vari}40;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
                    <span style="font-weight:700;color:{vari};font-size:1.1rem;">🎮 {lapsi['nimi']}</span>
                    <span style="font-size:0.75rem;color:#475569;">{vk_alku.strftime('%d.%m')} – {vk_loppu.strftime('%d.%m.%Y')}</span>
                </div>
                <div style="display:flex;gap:16px;">
                    <div><div class="raportti-otsikko">Ansaittu</div><div class="raportti-arvo" style="color:{vari};">{min_v} min</div></div>
                    <div><div class="raportti-otsikko">Töitä</div><div class="raportti-arvo">{tyot_v} kpl</div></div>
                    <div><div class="raportti-otsikko">vs. ed. viikko</div><div class="raportti-arvo" style="color:{muutos_vari};">{muutos_txt} min</div></div>
                    <div><div class="raportti-otsikko">Putki</div><div class="raportti-arvo">{putki} 🔥</div></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        st.write("### 💰 Peliajan käyttäminen")
        kaikki_lapset = lapset()
        if kaikki_lapset:
            vahennettava = st.selectbox("Kuka pelaa?", [l["nimi"] for l in kaikki_lapset], key="pelaaja_vahennys")
            kaytetyt     = st.number_input("Käytettävä aika (min)", min_value=5, max_value=300, value=15, step=5)
            if st.button("🎮 Vähennä minuutit saldosta", use_container_width=True):
                lapsi_obj = etsi_lapsi_nimella(vahennettava)
                if lapsi_obj:
                    if lapsi_obj["saldo"] >= kaytetyt:
                        db.paivita_saldo(lapsi_obj["id"], lapsi_obj["saldo"] - kaytetyt)
                        db.lisaa_historia(family_id, lapsi_obj["id"], lapsi_obj["nimi"],
                                          "Pelaaminen", kaytetyt, "käytetty")
                        lataa_perhedata()
                        st.success(f"Vähennetty {kaytetyt} min!")
                        st.rerun()
                    else:
                        st.error(f"Ei tarpeeksi saldoa! Saldo: {lapsi_obj['saldo']} min")

        st.markdown("---")

        st.write("### 🔑 Vaihda PIN-koodit")
        uusi_pp = st.text_input("Uusi perheen PIN", type="password", max_chars=6, key="uusi_pp")
        uusi_ap = st.text_input("Uusi vanhemman PIN", type="password", max_chars=6, key="uusi_ap")
        if st.button("💾 Tallenna uudet PIN-koodit", use_container_width=True):
            if len(uusi_pp) < 4 or len(uusi_ap) < 4:
                st.error("PIN vähintään 4 merkkiä.")
            elif uusi_pp == uusi_ap:
                st.error("Perheen ja vanhemman PIN eivät voi olla samat.")
            else:
                db.paivita_pinit(family_id, uusi_pp, uusi_ap)
                st.session_state.family["perhe_pin"] = uusi_pp
                st.session_state.family["admin_pin"] = uusi_ap
                st.success("PIN-koodit päivitetty!")

        st.markdown("---")

        st.write("### ⚙️ Asetukset")
        uusi_tavoite = st.number_input("Peliajan tavoite (min)", min_value=10, max_value=500,
                                       value=tavoite, step=10, key="tavoite_input")
        if st.button("💾 Tallenna tavoite", use_container_width=True):
            db.paivita_tavoite(family_id, uusi_tavoite)
            st.session_state.family["tavoite_min"] = uusi_tavoite
            st.success(f"Tavoite asetettu: {uusi_tavoite} min!")
            st.rerun()

        st.markdown("---")

        st.write("### 👦 Lasten hallinta")
        kaikki_lapset = lapset()

        st.write("**Muuta nimeä:**")
        if kaikki_lapset:
            muutettava_nimi  = st.selectbox("Valitse lapsi", [l["nimi"] for l in kaikki_lapset], key="muutettava")
            uusi_lapsen_nimi = st.text_input("Uusi nimi", value=muutettava_nimi, key="uusi_lapsen_nimi")
            if st.button("✏️ Tallenna nimi", use_container_width=True):
                uusi_lapsen_nimi = uusi_lapsen_nimi.strip()
                if uusi_lapsen_nimi and uusi_lapsen_nimi != muutettava_nimi:
                    lapsi_obj = etsi_lapsi_nimella(muutettava_nimi)
                    if lapsi_obj:
                        db.paivita_lapsen_nimi(lapsi_obj["id"], uusi_lapsen_nimi)
                        lataa_perhedata()
                        st.success(f"Nimi muutettu: '{muutettava_nimi}' → '{uusi_lapsen_nimi}'")
                        st.rerun()

        st.write("**Lisää lapsi:**")
        uuden_nimi = st.text_input("Uuden lapsen nimi", key="uuden_lapsen_nimi")
        if st.button("➕ Lisää lapsi", use_container_width=True):
            uuden_nimi = uuden_nimi.strip()
            if uuden_nimi:
                if any(l["nimi"] == uuden_nimi for l in kaikki_lapset):
                    st.error(f"'{uuden_nimi}' on jo listalla!")
                else:
                    db.lisaa_lapsi(family_id, uuden_nimi)
                    lataa_perhedata()
                    st.success(f"'{uuden_nimi}' lisätty!")
                    st.rerun()
            else:
                st.error("Syötä nimi ensin.")

        st.write("**Poista lapsi:**")
        if len(kaikki_lapset) > 1:
            poistettava = st.selectbox("Valitse poistettava", [l["nimi"] for l in kaikki_lapset], key="poistettava_lapsi")
            vahvistus   = st.checkbox(f"Vahvistan poiston – '{poistettava}' poistetaan pysyvästi")
            if st.button("🗑️ Poista lapsi", disabled=not vahvistus, use_container_width=True):
                lapsi_obj = etsi_lapsi_nimella(poistettava)
                if lapsi_obj:
                    db.poista_lapsi(lapsi_obj["id"])
                    lataa_perhedata()
                    st.success(f"'{poistettava}' poistettu.")
                    st.rerun()
        else:
            st.info("Vähintään yksi lapsi täytyy olla listalla.")

        st.markdown("---")

        st.write("### 🚨 Saldojen nollaus")
        nollaus_vahvistus = st.checkbox("Vahvistan, että haluan tyhjentää kaikkien saldot nollaan")
        if st.button("🚨 NOLLAA KAIKKIEN SALDOT", disabled=not nollaus_vahvistus, use_container_width=True):
            db.nollaa_saldot(family_id)
            db.lisaa_historia(family_id, None, "Kaikki", "Saldot nollattu", 0, "käytetty")
            lataa_perhedata()
            st.success("Saldot nollattu!")
            st.rerun()

        st.markdown("---")

        st.write("### 🛠️ Hallitse tehtäviä")
        st.write("**Nykyiset tehtävät:**")
        for kat in KATEGORIAT:
            ikoni        = KATEGORIA_IKONIT[kat]
            kat_tehtavat = [t for t in tehtavat() if t["kategoria"] == kat]
            if kat_tehtavat:
                st.write(f"{ikoni} **{kat}**")
                for t in sorted(kat_tehtavat, key=lambda x: x["minuutit"]):
                    bonus_merkki = " ⭐" if t["bonus"] else ""
                    st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;• {t['nimi']}{bonus_merkki} — {t['minuutit']} min")

        st.write("**Muokkaa tehtävää:**")
        kaikki_tehtavat = tehtavat()
        if kaikki_tehtavat:
            muokattava_nimi = st.selectbox("Valitse tehtävä", [t["nimi"] for t in kaikki_tehtavat], key="muokattava_tehtava")
            muokattava_obj  = etsi_tehtava_nimella(muokattava_nimi)
            if muokattava_obj:
                uudet_min = st.number_input("Minuutit", min_value=5, max_value=300,
                                            value=muokattava_obj["minuutit"], step=5, key="muokkaa_min")
                uusi_kat  = st.selectbox("Kategoria", KATEGORIAT,
                                         index=KATEGORIAT.index(muokattava_obj["kategoria"]) if muokattava_obj["kategoria"] in KATEGORIAT else 0,
                                         key="muokkaa_kat")
                if st.button("💾 Tallenna muutokset", use_container_width=True):
                    db.paivita_tehtava(muokattava_obj["id"], uudet_min, uusi_kat)
                    lataa_perhedata()
                    st.success(f"'{muokattava_nimi}' päivitetty!")
                    st.rerun()

        st.write("**Lisää uusi tehtävä:**")
        suositut = db.hae_suositut_tehtavat()
        if suositut:
            with st.expander("💡 Mitä muut perheet käyttävät?"):
                for s in suositut[:8]:
                    if st.button(f"➕ {s['nimi']} ({int(s['keskiarvo_min'])} min) — {s['perheita']} perhettä",
                                 key=f"suositus_{s['nimi']}"):
                        db.lisaa_tehtava(family_id, s["nimi"], int(s["keskiarvo_min"]), s["kategoria"], False)
                        lataa_perhedata()
                        st.success(f"'{s['nimi']}' lisätty!")
                        st.rerun()

        uusi_tnimi = st.text_input("Tehtävän nimi", key="uusi_tehtava_nimi")
        uusi_tmin  = st.number_input("Peliaika (min)", min_value=5, max_value=300, value=15, step=5, key="uusi_tehtava_min")
        uusi_tkat  = st.selectbox("Kategoria", KATEGORIAT, key="uusi_tehtava_kat")
        on_bonus   = st.checkbox("⭐ Bonustehtävä (häviää listalta kun hyväksytty)", key="uusi_bonus")
        if st.button("➕ Lisää tehtävä", use_container_width=True):
            uusi_tnimi = uusi_tnimi.strip()
            if uusi_tnimi:
                db.lisaa_tehtava(family_id, uusi_tnimi, uusi_tmin, uusi_tkat, on_bonus)
                lataa_perhedata()
                st.success(f"'{uusi_tnimi}' lisätty!")
                st.rerun()
            else:
                st.error("Syötä tehtävän nimi ensin.")

        st.write("**Poista tehtävä:**")
        if kaikki_tehtavat:
            poistettava_tyo = st.selectbox("Valitse poistettava", [t["nimi"] for t in kaikki_tehtavat], key="poistettava_tehtava")
            if st.button("❌ Poista valittu tehtävä", use_container_width=True):
                tyo_obj = etsi_tehtava_nimella(poistettava_tyo)
                if tyo_obj:
                    db.poista_tehtava(tyo_obj["id"])
                    lataa_perhedata()
                    st.success(f"'{poistettava_tyo}' poistettu.")
                    st.rerun()

# ══════════════════════════════════════════════════════════════════════
# VÄLILEHTI 3: HISTORIA
# ══════════════════════════════════════════════════════════════════════
with tab_historia:
    st.subheader("📜 Tapahtumahistoria")
    historia = st.session_state.historia

    if not historia:
        st.info("Ei vielä tapahtumia. Merkitse ensimmäinen kotityö! 🏠")
    else:
        lapsi_nimet = [l["nimi"] for l in lapset()]
        suodatin_vaihtoehdot = ["Kaikki"] + lapsi_nimet + ["Vain ansaitut", "Vain käytetty", "Vain hylätyt"]
        suodatin = st.selectbox("Näytä:", suodatin_vaihtoehdot)

        for merkinta in historia:
            tekija = merkinta.get("tekija_nimi", "?")
            if suodatin in lapsi_nimet and tekija != suodatin:
                continue
            if suodatin == "Vain ansaitut" and merkinta["tyyppi"] != "ansaittu":
                continue
            if suodatin == "Vain käytetty" and merkinta["tyyppi"] != "käytetty":
                continue
            if suodatin == "Vain hylätyt" and merkinta["tyyppi"] != "hylätty":
                continue

            if merkinta["tyyppi"] == "ansaittu":
                ikoni      = "✅"
                min_teksti = f'<span style="color:#10B981">+{merkinta["minuutit"]} min</span>'
            elif merkinta["tyyppi"] == "käytetty":
                ikoni      = "🎮"
                min_teksti = f'<span style="color:#F59E0B">-{merkinta["minuutit"]} min</span>' if merkinta["minuutit"] > 0 else ""
            else:
                ikoni      = "❌"
                min_teksti = ""

            try:
                aika_fmt = datetime.fromisoformat(merkinta["luotu_at"]).strftime("%d.%m.%Y %H:%M")
            except Exception:
                aika_fmt = merkinta.get("luotu_at", "")

            st.markdown(f"""
            <div class="historia-rivi">
                {ikoni} <strong>{tekija}</strong> — {merkinta['tapahtuma']}
                &nbsp;{min_teksti}
                &nbsp;<span style="color:#475569;font-size:0.8rem">· {aika_fmt}</span>
            </div>
            """, unsafe_allow_html=True)
