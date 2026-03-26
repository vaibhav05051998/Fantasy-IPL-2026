import streamlit as st
import pandas as pd
import json
import os
import sys
from collections import Counter
from datetime import datetime

# --- ROBUST PATH HANDLING ---
# This ensures players.py is found regardless of where the app is hosted
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    from players import PLAYER_MASTER
except ImportError:
    st.error("Error: 'players.py' not found in the repository root. Please ensure both files are in the same folder.")
    st.stop()

# --- 1. CONFIGURATION ---
DB_FILE = 'tournament_db.json'
TEAM_COLORS = {
    'RCB': '#d11d26', 'MI': '#004ba0', 'CSK': '#fdb913', 'SRH': '#f26522',
    'RR': '#ea1a85', 'KKR': '#3a225d', 'GT': '#1b2133', 'LSG': '#0057e2',
    'DC': '#0078bc', 'PBKS': '#dd1f2d', 'IPL': '#000080'
}
ROLE_EMOJI = {'BAT': '🏏', 'BOWL': '⚾', 'WK': '🧤'}

SEASON_WEEKS = {
    "Week 1 (Mar 28 - Apr 03)": {"lock": "2026-03-28 19:00:00"},
    "Week 2 (Apr 04 - Apr 10)": {"lock": "2026-04-04 19:00:00"},
}

# --- 2. DATABASE ENGINE ---
def load_db():
    if not os.path.exists(DB_FILE):
        players = list(PLAYER_MASTER.keys())
        # Static pools for Kazim, Aman, Aatish, Shrijeet, and Nagle
        return {
            "selections": {}, 
            "pools": {
                "Kazim": players[0:7], "Aman": players[7:14], 
                "Aatish": players[14:21], "Shrijeet": players[21:28], "Nagle": players[28:]
            }
        }
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f)

# --- 3. UI RENDERER ---
st.set_page_config(page_title="Inner Circle IPL 2026", layout="wide")

# Mobile-Optimized CSS
st.markdown("""<style>
    .mobile-matrix { border: 1px solid #e2e8f0; padding: 6px; border-radius: 6px; background: #fff; display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px; height: 50px; }
    .jersey-dot { height: 10px; width: 10px; border-radius: 50%; margin-right: 8px; }
    .role-label { font-size: 10px; color: #64748b; font-weight: 700; }
</style>""", unsafe_allow_html=True)

db = load_db()
week_label = st.sidebar.selectbox("Match Week", list(SEASON_WEEKS.keys()))
lock_time = datetime.strptime(SEASON_WEEKS[week_label]["lock"], "%Y-%m-%d %H:%M:%S")
is_locked = datetime.now() > lock_time

manager = st.selectbox("Manager Name", list(db["pools"].keys()))
pool = db["pools"].get(manager, [])
state_key = f"sel_{manager}_{week_label}"

if state_key not in st.session_state:
    saved = db["selections"].get(week_label, {}).get(manager, {}).get("squad", [])
    st.session_state[state_key] = list(saved)

# Search & Filter
f1, f2 = st.columns(2)
search_query = f1.text_input("🔍 Search Player")
team_filter = f2.selectbox("Team Filter", ["All Teams"] + list(TEAM_COLORS.keys()))

# Player Selection Grid (2-Column Matrix)
cols = st.columns(2)
players_to_show = [p for p in pool if search_query.lower() in p.lower()]

for i, p in enumerate(sorted(players_to_show)):
    info = PLAYER_MASTER.get(p)
    if team_filter != "All Teams" and info["team"] != team_filter:
        continue
    
    with cols[i % 2]:
        c_main, c_chk = st.columns([4, 1])
        with c_main:
            st.markdown(f'''<div class="mobile-matrix">
                <span class="jersey-dot" style="background:{TEAM_COLORS.get(info["team"])}"></span>
                <div style="flex-grow:1; line-height:1.1;">
                    <span style="font-size:11px; font-weight:600;">{p} ({info["team"]})</span><br>
                    <span class="role-label">{ROLE_EMOJI.get(info["role"])} {info["role"]}</span>
                </div>
            </div>''', unsafe_allow_html=True)
        with c_chk:
            in_squad = p in st.session_state[state_key]
            if st.checkbox("", key=f"chk_{p}", value=in_squad, disabled=is_locked):
                if p not in st.session_state[state_key]:
                    st.session_state[state_key].append(p)
                    st.rerun()
            elif in_squad:
                st.session_state[state_key].remove(p)
                st.rerun()

# Validation Section
squad = st.session_state[state_key]
roles = Counter([PLAYER_MASTER[p]["role"] for p in squad])
os_count = sum(1 for p in squad if PLAYER_MASTER[p]["is_overseas"])

st.divider()
st.write(f"**Current Squad:** {len(squad)}/11 | **Bowlers:** {roles['BOWL']}/4+ | **WK:** {roles['WK']}/1+ | **Overseas:** {os_count}/4 max")

if len(squad) == 11 and roles['BOWL'] >= 4 and roles['WK'] >= 1 and os_count <= 4:
    cap = st.selectbox("Assign Captain (2x Points)", squad)
    if st.button("🚀 SAVE & LOCK SQUAD", type="primary", use_container_width=True):
        if week_label not in db["selections"]: db["selections"][week_label] = {}
        db["selections"][week_label][manager] = {"squad": squad, "cap": cap}
        save_db(db)
        st.success("Squad locked successfully!")
else:
    st.warning("Requirements: 11 players total, at least 4 bowlers, at least 1 keeper, and max 4 overseas players.")
