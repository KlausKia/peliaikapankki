# ── db.py — ChoreQuest tietokantakerros ──────────────────────────────
# Kaikki Supabase-kutsut tässä tiedostossa. app.py ei koskaan tee suoria
# tietokantakyselyitä — se kutsuu aina tämän tiedoston funktioita.

import streamlit as st
from supabase import create_client, Client
from datetime import datetime, timedelta
import bcrypt

def hashaa_pin(pin: str) -> str:
    """Hashaa PIN bcrypt:llä tallennusta varten."""
    return bcrypt.hashpw(pin.encode(), bcrypt.gensalt()).decode()

def tarkista_pin(pin: str, hash: str) -> bool:
    """Vertaa syötettyä PIN:iä tallennettuun hashiin."""
    try:
        return bcrypt.checkpw(pin.encode(), hash.encode())
    except Exception:
        # Tuki vanhoille selkoteksti-PIN:eille migraation aikana
        return pin == hash

# ── OLETUSTEHTÄVÄT uudelle perheelle ─────────────────────────────────
OLETUSTEHTAVAT = [
    {"nimi": "Kodin imurointi",       "minuutit": 20, "kategoria": "Sisätyöt", "bonus": False},
    {"nimi": "Pölyjen pyyhintä",      "minuutit": 15, "kategoria": "Sisätyöt", "bonus": False},
    {"nimi": "Tiskikoneen tyhjennys", "minuutit": 10, "kategoria": "Sisätyöt", "bonus": False},
    {"nimi": "Auton imurointi",       "minuutit": 30, "kategoria": "Sisätyöt", "bonus": False},
    {"nimi": "Autotallin siivous",    "minuutit": 60, "kategoria": "Ulkotyöt", "bonus": False},
    {"nimi": "Auton pesu ulkoa",      "minuutit": 45, "kategoria": "Ulkotyöt", "bonus": False},
    {"nimi": "Pihavajan siivous",     "minuutit": 45, "kategoria": "Ulkotyöt", "bonus": False},
]

# ── YHTEYS ───────────────────────────────────────────────────────────
@st.cache_resource
def get_client() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

def db() -> Client:
    return get_client()

# ══════════════════════════════════════════════════════════════════════
# PERHEET
# ══════════════════════════════════════════════════════════════════════

def hae_perhe_tunnuksella(tunnus: str) -> dict | None:
    """Palauttaa perheen dict tai None jos ei löydy."""
    res = db().table("families").select("*").eq("tunnus", tunnus.strip().lower()).execute()
    return res.data[0] if res.data else None

def tunnus_vapaa(tunnus: str) -> bool:
    """Tarkistaa onko perheen tunnus vapaana."""
    return hae_perhe_tunnuksella(tunnus) is None

def luo_perhe(tunnus: str, perhe_pin: str, admin_pin: str) -> dict:
    """Luo uuden perheen ja lisää oletustehtävät. Palauttaa family-rivin."""
    tunnus = tunnus.strip().lower()
    res = db().table("families").insert({
        "tunnus": tunnus,
        "perhe_pin": hashaa_pin(perhe_pin),
        "admin_pin": hashaa_pin(admin_pin),
        "tavoite_min": 90
    }).execute()
    family = res.data[0]
    family_id = family["id"]

    # Lisää oletustehtävät
    tehtavat = [{"family_id": family_id, **t} for t in OLETUSTEHTAVAT]
    db().table("tasks").insert(tehtavat).execute()

    return family

def paivita_pinit(family_id: str, uusi_perhe_pin: str, uusi_admin_pin: str):
    """Vanhempi vaihtaa PIN-koodit — tallennetaan hashattuina."""
    db().table("families").update({
        "perhe_pin": hashaa_pin(uusi_perhe_pin),
        "admin_pin": hashaa_pin(uusi_admin_pin)
    }).eq("id", family_id).execute()

def paivita_tavoite(family_id: str, tavoite_min: int):
    db().table("families").update({"tavoite_min": tavoite_min}).eq("id", family_id).execute()

# ══════════════════════════════════════════════════════════════════════
# LAPSET
# ══════════════════════════════════════════════════════════════════════

def hae_lapset(family_id: str) -> list[dict]:
    """Palauttaa perheen lapset listana."""
    res = db().table("children").select("*").eq("family_id", family_id).execute()
    return res.data

def lisaa_lapsi(family_id: str, nimi: str) -> dict:
    res = db().table("children").insert({
        "family_id": family_id,
        "nimi": nimi.strip(),
        "saldo": 0,
        "saavutukset": []
    }).execute()
    return res.data[0]

def paivita_lapsen_nimi(child_id: str, uusi_nimi: str):
    db().table("children").update({"nimi": uusi_nimi.strip()}).eq("id", child_id).execute()

def poista_lapsi(child_id: str):
    db().table("children").delete().eq("id", child_id).execute()

def paivita_saldo(child_id: str, uusi_saldo: int):
    db().table("children").update({"saldo": uusi_saldo}).eq("id", child_id).execute()

def paivita_saavutukset(child_id: str, saavutukset: list[str]):
    db().table("children").update({"saavutukset": saavutukset}).eq("id", child_id).execute()

def nollaa_saldot(family_id: str):
    """Nollaa kaikkien perheen lasten saldot."""
    db().table("children").update({"saldo": 0}).eq("family_id", family_id).execute()

# ══════════════════════════════════════════════════════════════════════
# TEHTÄVÄT
# ══════════════════════════════════════════════════════════════════════

def hae_tehtavat(family_id: str) -> list[dict]:
    res = db().table("tasks").select("*").eq("family_id", family_id).execute()
    return res.data

def lisaa_tehtava(family_id: str, nimi: str, minuutit: int, kategoria: str, bonus: bool) -> dict:
    res = db().table("tasks").insert({
        "family_id": family_id,
        "nimi": nimi.strip(),
        "minuutit": minuutit,
        "kategoria": kategoria,
        "bonus": bonus
    }).execute()
    return res.data[0]

def paivita_tehtava(task_id: str, minuutit: int, kategoria: str):
    db().table("tasks").update({
        "minuutit": minuutit,
        "kategoria": kategoria
    }).eq("id", task_id).execute()

def poista_tehtava(task_id: str):
    db().table("tasks").delete().eq("id", task_id).execute()

def hae_suositut_tehtavat() -> list[dict]:
    """Palauttaa popular_tasks-näkymän — vain nimet ja suosio, ei perhetietoja."""
    try:
        res = db().table("popular_tasks").select("*").execute()
        return res.data
    except Exception:
        return []

# ══════════════════════════════════════════════════════════════════════
# ODOTTAVAT TEHTÄVÄT
# ══════════════════════════════════════════════════════════════════════

def hae_odottavat(family_id: str) -> list[dict]:
    res = (db().table("pending_tasks")
           .select("*, children(nimi)")
           .eq("family_id", family_id)
           .order("luotu_at")
           .execute())
    return res.data

def lisaa_odottava(family_id: str, child_id: str, task_id: str,
                   tyo_nimi: str, minuutit: int, bonus: bool) -> dict:
    res = db().table("pending_tasks").insert({
        "family_id": family_id,
        "child_id": child_id,
        "task_id": task_id,
        "tyo_nimi": tyo_nimi,
        "minuutit": minuutit,
        "bonus": bonus
    }).execute()
    return res.data[0]

def poista_odottava(pending_id: str):
    db().table("pending_tasks").delete().eq("id", pending_id).execute()

# ══════════════════════════════════════════════════════════════════════
# HISTORIA
# ══════════════════════════════════════════════════════════════════════

def hae_historia(family_id: str, limit: int = 200) -> list[dict]:
    res = (db().table("history")
           .select("*")
           .eq("family_id", family_id)
           .order("luotu_at", desc=True)
           .limit(limit)
           .execute())
    return res.data

def lisaa_historia(family_id: str, child_id: str | None,
                   tekija_nimi: str, tapahtuma: str,
                   minuutit: int, tyyppi: str):
    db().table("history").insert({
        "family_id": family_id,
        "child_id": child_id,
        "tekija_nimi": tekija_nimi,
        "tapahtuma": tapahtuma,
        "minuutit": minuutit,
        "tyyppi": tyyppi
    }).execute()

# ══════════════════════════════════════════════════════════════════════
# APUFUNKTIOT — LOGIIKKA (ei Streamlit-riippuvuuksia)
# ══════════════════════════════════════════════════════════════════════

def laske_putki(child_id: str, historia: list[dict]) -> int:
    """Laskee peräkkäisten päivien putken historiasta."""
    paivat = set()
    for m in historia:
        if m["child_id"] == child_id and m["tyyppi"] == "ansaittu":
            try:
                pvm = datetime.fromisoformat(m["luotu_at"]).date()
                paivat.add(pvm)
            except Exception:
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

def laske_tyot_yhteensa(child_id: str, historia: list[dict]) -> int:
    return sum(1 for m in historia if m["child_id"] == child_id and m["tyyppi"] == "ansaittu")

def tarkista_saavutukset(lapsi: dict, historia: list[dict]) -> list[str]:
    """
    Tarkistaa uudet saavutukset ja päivittää tietokantaan.
    Palauttaa listan uusista saavutuksista (id:t).
    """
    SAAVUTUKSET_KYNNYKSET = {
        "eka_tyo":  lambda t, p: t >= 1,
        "tyo_5":    lambda t, p: t >= 5,
        "tyo_10":   lambda t, p: t >= 10,
        "tyo_25":   lambda t, p: t >= 25,
        "putki_3":  lambda t, p: p >= 3,
        "putki_5":  lambda t, p: p >= 5,
        "putki_7":  lambda t, p: p >= 7,
    }
    child_id = lapsi["id"]
    saavutetut = lapsi.get("saavutukset") or []
    tyot = laske_tyot_yhteensa(child_id, historia)
    putki = laske_putki(child_id, historia)
    uudet = []
    for sav_id, ehto in SAAVUTUKSET_KYNNYKSET.items():
        if ehto(tyot, putki) and sav_id not in saavutetut:
            saavutetut.append(sav_id)
            uudet.append(sav_id)
    if uudet:
        paivita_saavutukset(child_id, saavutetut)
        lapsi["saavutukset"] = saavutetut
    return uudet

def viikko_data(child_id: str, historia: list[dict], viikkoja_taaksepain: int = 0):
    """Palauttaa (minuutit, tyot, viikon_alku, viikon_loppu)."""
    nyt = datetime.now().date()
    viikon_alku = nyt - timedelta(days=nyt.weekday()) - timedelta(weeks=viikkoja_taaksepain)
    viikon_loppu = viikon_alku + timedelta(days=6)
    minuutit = 0
    tyot = 0
    for m in historia:
        if m["child_id"] == child_id and m["tyyppi"] == "ansaittu":
            try:
                pvm = datetime.fromisoformat(m["luotu_at"]).date()
                if viikon_alku <= pvm <= viikon_loppu:
                    minuutit += m["minuutit"]
                    tyot += 1
            except Exception:
                pass
    return minuutit, tyot, viikon_alku, viikon_loppu
