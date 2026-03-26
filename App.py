import streamlit as st
import pandas as pd
import json
import os
from collections import Counter
from datetime import datetime

# --- IMPORT HARDCODED PLAYERS FROM SEPARATE FILE ---
from players import PLAYER_MASTER

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

def load_db():
    if not os.path.exists(DB_FILE):
        players = list(PLAYER_MASTER.keys())
        # Distributed pools for your squad managers
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

# --- UI SETUP ---
st.set_page_config(page_title="Inner Circle IPL 2026", layout="wide")

st.markdown("""<style>
    .mobile-matrix { border: 1px solid #e2e8f0; padding: 6px; border-radius: 6px; background: #fff; display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px; height: 50px; }
    .jersey-dot { height: 10px; width: 10px; border-radius: 50%; margin-right: 8px; }
    .role-label { font-size: 10px; color: #64748b; font-weight: 700; }
</style>""", unsafe_allow_html=True)

db = load_db()
week = st.sidebar.selectbox("Select Week", list(SEASON_WEEKS.keys()))
is_locked = datetime.now() > datetime.strptime(SEASON_WEEKS[week]["lock"], "%Y-%m-%d %H:%M:%S")

manager = st.selectbox("Manager", list(db["pools"].keys()))
pool = db["pools"].get(manager, [])
state_key = f"sel_{manager}_{week}"

if state_key not in st.session_state:
    st.session_state[state_key] = db["selections"].get(week, {}).get(manager, {}).get("squad", [])

# SEARCH & FILTERS
f1, f2 = st.columns(2)
search = f1.text_input("🔍 Search")
team_f = f2.selectbox("Team Filter", ["All"] + list(TEAM_COLORS.keys()))

# DISPLAY GRID
cols = st.columns(2)
filtered = [p for p in pool if search.lower() in p.lower()]

for i, p in enumerate(sorted(filtered)):
    info = PLAYER_MASTER.get(p)
    if team_f != "All" and info["team"] != team_f: continue
    
    with cols[i % 2]:
        c1, c2 = st.columns([4, 1])
        with c1:
            st.markdown(f'''<div class="mobile-matrix">
                <span class="jersey-dot" style="background:{TEAM_COLORS.get(info["team"])}"></span>
                <div style="flex-grow:1; line-height:1.1;">
                    <span style="font-size:11px; font-weight:600;">{p} ({info["team"]})</span><br>
                    <span class="role-label">{ROLE_EMOJI.get(info["role"])} {info["role"]}</span>
                </div>
            </div>''', unsafe_allow_html=True)
        with c2:
            checked = p in st.session_state[state_key]
            if st.checkbox("", key=f"c_{p}", value=checked, disabled=is_locked):
                if p not in st.session_state[state_key]:
                    st.session_state[state_key].append(p); st.rerun()
            elif checked:
                st.session_state[state_key].remove(p); st.rerun()

# SQUAD VALIDATION
squad = st.session_state[state_key]
roles = Counter([PLAYER_MASTER[p]["role"] for p in squad])
os_count = sum(1 for p in squad if PLAYER_MASTER[p]["is_overseas"])

st.divider()
st.write(f"**Squad:** {len(squad)}/11 | **Bowl:** {roles['BOWL']}/4+ | **WK:** {roles['WK']}/1+ | **OS:** {os_count}/4")

if len(squad) == 11 and roles['BOWL'] >= 4 and roles['WK'] >= 1 and os_count <= 4:
    cap = st.selectbox("Captain (2x)", squad)
    if st.button("🚀 LOCK SQUAD", type="primary", use_container_width=True):
        if week not in db["selections"]: db["selections"][week] = {}
        db["selections"][week][manager] = {"squad": squad, "cap": cap}
        save_db(db)
        st.success("Squad Locked!")
else:
    st.warning("Requirements: 11 Players, 4+ Bowlers, 1+ Keeper, Max 4 Overseas.")
