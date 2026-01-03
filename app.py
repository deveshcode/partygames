# app.py — Party Games (Host Mode)
# Beautiful UI + big buttons + game cards + progress timer
# Single device, mobile-friendly, no repeats, reset anytime

import random
import time
from collections import Counter
import streamlit as st

st.set_page_config(page_title="Party Games", page_icon="🎉", layout="centered")

# ----------------------------
# Your data (unchanged, kept as-is)
# ----------------------------

DUMB_CHARADES = {
    "Bollywood movies or Tv Serial": [
        "Andaz Apna Apna", "Om Shanti Om", "Kal Ho Naa Ho", "Lagaan", "Gully Boy",
        "Dangal", "Bajrangi Bhaijaan", "Zindagi Na Milegi Dobara", "Jab We Met",
        "Kabir Singh", "Dil Chahta Hai", "Barfi!", "Queen", "Rockstar", "Kahaani",
        "Bhool Bhulaiyaa", "Hera Pheri", "Welcome", "Golmaal", "Chennai Express",
        "Yeh Jawaani Hai Deewani", "Swades", "Taare Zameen Par", "PK", "Don",
        "Don 2", "Race", "Race 2", "Tanu Weds Manu", "Stree", "Drishyam",
        "Sholay", "Deewar", "Black", "My Name Is Khan", "Sultan",
        "Taarak Mehta Ka Ooltah Chashmah", "CID", "Crime Patrol", "Balika Vadhu",
        "Naagin", "Bigg Boss", "Indian Idol", "Kaun Banega Crorepati",
    ]
}

PICTIONARY = {
    "Could be an Indian food or a Profession or Festival Thing": [
        "Pani Puri", "Vada Pav", "Dosa", "Idli", "Sambar", "Biryani", "Butter Chicken",
        "Rajma Chawal", "Chole Bhature", "Poha", "Upma", "Pav Bhaji", "Jalebi",
        "Gulab Jamun", "Samosa", "Kachori", "Pakora", "Misal Pav", "Dhaba",
        "Lassi", "Kulfi", "Rasgulla", "Modak", "Thepla", "Khichdi",
        "Fafda", "Dhokla", "Kheer", "Aloo Paratha", "Paneer Tikka",
        "Tandoor", "Chutney", "Pickle", "Papad",
        "Doctor", "Dentist", "Teacher", "Cricketer", "Chef", "Engineer", "Lawyer", "Police",
        "Pilot", "Singer", "Actor", "Auto Rickshaw Driver", "Delivery Rider", "Journalist",
        "Photographer", "Tailor", "Carpenter", "Mechanic", "Barber", "Nurse",
        "Data Scientist", "YouTuber", "Stand-up Comedian",
        "Rangoli", "Dhol", "Firecrackers", "Laddoo", "Aarti", "Garba", "Dandiya", "Gulal",
        "Diya", "Lantern", "Pandal", "Modak", "Ganesha Idol", "Christmas Tree", "Eidi",
        "Shehnai", "Mehendi", "Haldi Ceremony", "Dussehra Ravan", "Kite", "Bonfire",
        "Sweets Box", "New Clothes", "Thali", "Pooja Bell",
    ],
    "Indian food": [
        "Pani Puri", "Vada Pav", "Dosa", "Idli", "Sambar", "Biryani", "Butter Chicken",
        "Rajma Chawal", "Chole Bhature", "Poha", "Upma", "Pav Bhaji", "Jalebi",
        "Gulab Jamun", "Samosa", "Kachori", "Pakora", "Misal Pav", "Dhaba",
        "Lassi", "Kulfi", "Rasgulla", "Modak", "Thepla", "Khichdi",
        "Fafda", "Dhokla", "Kheer", "Aloo Paratha", "Paneer Tikka",
        "Tandoor", "Chutney", "Pickle", "Papad",
    ],
    "Professions": [
        "Doctor", "Dentist", "Teacher", "Cricketer", "Chef", "Engineer", "Lawyer", "Police",
        "Pilot", "Singer", "Actor", "Auto Rickshaw Driver", "Delivery Rider", "Journalist",
        "Photographer", "Tailor", "Carpenter", "Mechanic", "Barber", "Nurse",
        "Data Scientist", "YouTuber", "Stand-up Comedian",
    ],
    "Festival things": [
        "Rangoli", "Dhol", "Firecrackers", "Laddoo", "Aarti", "Garba", "Dandiya", "Gulal",
        "Diya", "Lantern", "Pandal", "Modak", "Ganesha Idol", "Christmas Tree", "Eidi",
        "Shehnai", "Mehendi", "Haldi Ceremony", "Dussehra Ravan", "Kite", "Bonfire",
        "Sweets Box", "New Clothes", "Thali", "Pooja Bell",
    ],
}

# ----------------------------
# Helpers (yours, with pretty timer)
# ----------------------------

def ss_set(key: str, default):
    if key not in st.session_state:
        st.session_state[key] = default

def draw_unique(deck_key: str, items):
    used_key = f"used::{deck_key}"
    ss_set(used_key, set())
    used = st.session_state[used_key]

    remaining_idx = [i for i in range(len(items)) if i not in used]
    if not remaining_idx:
        return None

    i = random.choice(remaining_idx)
    used.add(i)
    st.session_state[used_key] = used
    return items[i]

def reset_deck(deck_key: str):
    st.session_state[f"used::{deck_key}"] = set()

def big_btn(label: str, key: str):
    return st.button(label, use_container_width=True, key=key)

def countdown_pretty(seconds: int):
    """
    Nice host-mode countdown: big number + progress bar.
    (Blocks while running, which is fine for single-device party hosting.)
    """
    seconds = int(seconds)
    big = st.empty()
    bar = st.progress(0)
    for t in range(seconds, -1, -1):
        big.markdown(f"<div class='timer'>⏱️ {t}s</div>", unsafe_allow_html=True)
        done = (seconds - t) / max(seconds, 1)
        bar.progress(min(max(done, 0.0), 1.0))
        time.sleep(1)
    st.success("✅ Time’s up!")

def build_roles(num_players: int, mafia: int, detective: int, doctor: int):
    roles = (["Mafia"] * mafia) + (["Detective"] * detective) + (["Doctor"] * doctor)
    if len(roles) > num_players:
        return None
    roles += ["Villager"] * (num_players - len(roles))
    random.shuffle(roles)
    return roles

# ----------------------------
# Styling (frontend polish)
# ----------------------------

st.markdown(
    """
    <style>
      /* Layout width on desktop */
      .block-container { padding-top: 1.2rem; padding-bottom: 2.5rem; max-width: 900px; }

      /* Hero */
      .hero {
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 20px;
        padding: 18px 18px 14px 18px;
        background: linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03));
        box-shadow: 0 12px 24px rgba(0,0,0,0.12);
        margin-bottom: 14px;
      }
      .hero h1 { margin: 0; font-size: 30px; line-height: 1.1; }
      .hero p  { margin: 6px 0 0 0; opacity: 0.85; }

      /* Card */
      .card {
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 18px;
        padding: 16px;
        background: rgba(255,255,255,0.04);
        box-shadow: 0 10px 20px rgba(0,0,0,0.10);
      }
      .card h2 { margin-top: 0; }

      /* Big display text */
      .big-word {
        font-size: 40px;
        font-weight: 800;
        letter-spacing: 0.2px;
        text-align: center;
        padding: 16px 8px;
        border-radius: 16px;
        border: 1px dashed rgba(255,255,255,0.20);
        background: rgba(255,255,255,0.03);
        margin: 10px 0 6px 0;
      }

      /* Timer */
      .timer {
        font-size: 44px;
        font-weight: 900;
        text-align: center;
        padding: 8px 0 4px 0;
      }

      /* Make buttons feel chunky */
      button[kind="primary"], .stButton>button {
        border-radius: 14px !important;
        padding: 0.8rem 1rem !important;
        font-weight: 700 !important;
      }

      /* Remove extra top whitespace sometimes */
      header { visibility: hidden; height: 0px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------
# Top hero + global controls
# ----------------------------

st.markdown(
    """
    <div class="hero">
      <h1>🎉 Party Games</h1>
      <p>Host-mode • single device • mobile-friendly • no repeats • reset anytime</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("⚙️ Host Controls")
    st.caption("Quick actions while hosting")
    if st.button("🔄 Reset ALL used cards", use_container_width=True):
        # Clears only our used::* keys
        for k in list(st.session_state.keys()):
            if str(k).startswith("used::"):
                del st.session_state[k]
        st.toast("Reset done ✅", icon="✅")

    st.divider()
    st.caption("Tip: Open on phone + connect to TV (AirPlay/Chromecast)")

# ----------------------------
# Navigation (cleaner than radio)
# ----------------------------

tabs = st.tabs(["🤫 Dumb Charades", "✏️ Speed Pictionary", "🕵️ Mafia"])

# ----------------------------
# Tab 1: Dumb Charades
# ----------------------------
with tabs[0]:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("🤫 Dumb Charades")
    st.caption("Teams of 2–3 • tap Next • act it out • optional timer")

    deck = st.selectbox("Deck", list(DUMB_CHARADES.keys()))
    deck_key = f"charades::{deck}"
    ss_set("charades_item", None)

    c1, c2 = st.columns(2)
    with c1:
        if big_btn("🎲 Next title (no repeats)", key="char_next"):
            st.session_state.charades_item = draw_unique(deck_key, DUMB_CHARADES[deck])
    with c2:
        if big_btn("🧼 Reset deck", key="char_reset"):
            reset_deck(deck_key)
            st.session_state.charades_item = None

    item = st.session_state.charades_item
    if item is None:
        st.info("Tap Next to start. Reset if you finish the deck.")
    else:
        st.markdown(f"<div class='big-word'>{item}</div>", unsafe_allow_html=True)

    st.divider()
    seconds = st.slider("Round timer", min_value=5, max_value=120, value=30, step=5)
    c3, c4 = st.columns(2)
    with c3:
        if big_btn("⏱️ Start timer", key="char_timer"):
            countdown_pretty(seconds)
    with c4:
        if big_btn("🎈 Celebrate (optional)", key="char_party"):
            st.balloons()

    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# Tab 2: Speed Pictionary
# ----------------------------
with tabs[1]:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("✏️ Speed Pictionary")
    st.caption("Teams of 2–3 • draw fast • 30s default • no repeats")

    cat = st.selectbox("Category", list(PICTIONARY.keys()))
    seconds = st.slider("Timer", min_value=10, max_value=120, value=30, step=5)

    deck_key = f"pictionary::{cat}"
    ss_set("pict_word", None)

    c1, c2 = st.columns(2)
    with c1:
        if big_btn("🎲 Next word (no repeats)", key="pic_next"):
            st.session_state.pict_word = draw_unique(deck_key, PICTIONARY[cat])
    with c2:
        if big_btn("🧼 Reset category", key="pic_reset"):
            reset_deck(deck_key)
            st.session_state.pict_word = None

    word = st.session_state.pict_word
    if word is None:
        st.info("Tap Next to start. Reset if you finish the category.")
    else:
        st.markdown(f"<div class='big-word'>{word}</div>", unsafe_allow_html=True)

    c3, c4 = st.columns(2)
    with c3:
        if big_btn("⏱️ Start timer", key="pic_timer"):
            countdown_pretty(seconds)
    with c4:
        if big_btn("✅ Mark as guessed", key="pic_guess"):
            st.toast("Point! ✅", icon="✅")

    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# Tab 3: Mafia Host Tool
# ----------------------------
with tabs[2]:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("🕵️ Mafia Host Tool")
    st.caption("Pass phone around • Reveal → Hide → Next player")

    ss_set("mafia_roles", None)
    ss_set("mafia_index", 0)
    ss_set("mafia_revealed", False)

    num_players = st.number_input("Players", min_value=4, max_value=20, value=8, step=1)

    with st.expander("Role counts (simple party setup)"):
        mafia = st.number_input("Mafia", min_value=1, max_value=6, value=2, step=1)
        detective = st.number_input("Detective", min_value=0, max_value=2, value=1, step=1)
        doctor = st.number_input("Doctor", min_value=0, max_value=2, value=1, step=1)

    c1, c2 = st.columns(2)
    with c1:
        if big_btn("🎭 Generate roles", key="maf_gen"):
            roles = build_roles(int(num_players), int(mafia), int(detective), int(doctor))
            if roles is None:
                st.error("Too many special roles for the number of players.")
            else:
                st.session_state.mafia_roles = roles
                st.session_state.mafia_index = 0
                st.session_state.mafia_revealed = False
                st.toast("Roles ready ✅", icon="✅")
    with c2:
        if big_btn("🧹 Clear", key="maf_clear"):
            st.session_state.mafia_roles = None
            st.session_state.mafia_index = 0
            st.session_state.mafia_revealed = False

    roles = st.session_state.mafia_roles
    if not roles:
        st.info("Generate roles to start.")
    else:
        i = st.session_state.mafia_index
        total = len(roles)

        st.markdown(f"### Player **{i+1} / {total}**")

        if not st.session_state.mafia_revealed:
            if big_btn("👁️ Reveal role", key="maf_reveal"):
                st.session_state.mafia_revealed = True
        else:
            st.markdown(f"<div class='big-word'>✅ {roles[i]}</div>", unsafe_allow_html=True)
            st.caption("Memorize it. Don’t let others see.")

            c3, c4 = st.columns(2)
            with c3:
                if big_btn("🙈 Hide", key="maf_hide"):
                    st.session_state.mafia_revealed = False
            with c4:
                if big_btn("➡️ Next player", key="maf_next"):
                    st.session_state.mafia_revealed = False
                    st.session_state.mafia_index = (i + 1) % total

        with st.expander("Host summary (counts only)"):
            counts = Counter(roles)
            st.write({k: int(v) for k, v in counts.items()})

    st.markdown("</div>", unsafe_allow_html=True)
