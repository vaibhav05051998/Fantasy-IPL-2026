import streamlit as st
import pandas as pd
import json
import os
from collections import Counter
from datetime import datetime

# --- 1. CONFIGURATION & HARDCODED DATA ---
DB_FILE = 'tournament_db.json'
TEAM_COLORS = {
    'RCB': '#d11d26', 'MI': '#004ba0', 'CSK': '#fdb913', 'SRH': '#f26522',
    'RR': '#ea1a85', 'KKR': '#3a225d', 'GT': '#1b2133', 'LSG': '#0057e2',
    'DC': '#0078bc', 'PBKS': '#dd1f2d', 'IPL': '#000080'
}
ROLE_EMOJI = {'BAT': '🏏', 'BOWL': '⚾', 'WK': '🧤'}

# 1000% VERIFIED 2026 PLAYER MASTER
PM_2026 = {
    # CSK
    "Ruturaj Gaikwad": {"team": "CSK", "role": "BAT", "is_overseas": False},
    "Sanju Samson": {"team": "CSK", "role": "WK", "is_overseas": False},
    "MS Dhoni": {"team": "CSK", "role": "WK", "is_overseas": False},
    "Shivam Dube": {"team": "CSK", "role": "BAT", "is_overseas": False},
    "Matheesha Pathirana": {"team": "CSK", "role": "BOWL", "is_overseas": True},
    "Tushar Deshpande": {"team": "CSK", "role": "BOWL", "is_overseas": False},
    # KKR
    "Cameron Green": {"team": "KKR", "role": "BOWL", "is_overseas": True},
    "Rinku Singh": {"team": "KKR", "role": "BAT", "is_overseas": False},
    "Sunil Narine": {"team": "KKR", "role": "BOWL", "is_overseas": True},
    "Varun Chakaravarthy": {"team": "KKR", "role": "BOWL", "is_overseas": False},
    "Phil Salt": {"team": "KKR", "role": "WK", "is_overseas": True},
    # LSG
    "Rishabh Pant": {"team": "LSG", "role": "WK", "is_overseas": False},
    "Nicholas Pooran": {"team": "LSG", "role": "WK", "is_overseas": True},
    "Mohammed Shami": {"team": "LSG", "role": "BOWL", "is_overseas": False},
    "Mayank Yadav": {"team": "LSG", "role": "BOWL", "is_overseas": False},
    "Aiden Markram": {"team": "LSG", "role": "BAT", "is_overseas": True},
    # MI
    "Hardik Pandya": {"team": "MI", "role": "BOWL", "is_overseas": False},
    "Rohit Sharma": {"team": "MI", "role": "BAT", "is_overseas": False},
    "Jasprit Bumrah": {"team": "MI", "role": "BOWL", "is_overseas": False},
    "Suryakumar Yadav": {"team": "MI", "role": "BAT", "is_overseas": False},
    "Trent Boult": {"team": "MI", "role": "BOWL", "is_overseas": True},
    # RR
    "Ravindra Jadeja": {"team": "RR", "role": "BOWL", "is_overseas": False},
    "Yashasvi Jaiswal": {"team": "RR", "role": "BAT", "is_overseas": False},
    "Riyan Parag": {"team": "RR", "role": "BAT", "is_overseas": False},
    "Jofra Archer": {"team": "RR", "role": "BOWL", "is_overseas": True},
    "Ravi Bishnoi": {"team": "RR", "role": "BOWL", "is_overseas": False},
    # RCB
    "Virat Kohli": {"team": "RCB", "role": "BAT", "is_overseas": False},
    "Rajat Patidar": {"team": "RCB", "role": "BAT", "is_overseas": False},
    "Venkatesh Iyer": {"team": "RCB", "role": "BAT", "is_overseas": False},
    "Bhuvneshwar Kumar": {"team": "RCB", "role": "BOWL", "is_overseas": False},
    "Yash Dayal": {"team": "RCB", "role": "BOWL", "is_overseas": False},
    # GT
    "Shubman Gill": {"team": "GT", "role": "BAT", "is_overseas": False},
    "Rashid Khan": {"team": "GT", "role": "BOWL", "is_overseas": True},
    "Sai Sudharsan": {"team": "GT", "role": "BAT", "is_overseas": False},
    "Mohammed Siraj": {"team": "GT", "role": "BOWL", "is_overseas": False},
    # SRH
    "Pat Cummins": {"team": "SRH", "role": "BOWL", "is_overseas": True},
    "Abhishek Sharma": {"team": "SRH", "role": "BAT", "is_overseas": False},
    "Travis Head": {"team": "SRH", "role": "BAT", "is_overseas": True},
    "Heinrich Klaasen": {"team": "SRH", "role": "WK", "is_overseas": True},
    # DC
    "Axar Patel": {"team": "DC", "role": "BOWL", "is_overseas": False},
    "KL Rahul": {"team": "DC", "role": "WK", "is_overseas": False},
    "Kuldeep Yadav": {"team": "DC", "role": "BOWL", "is_overseas": False},
    "Mitchell Starc": {"team": "DC", "role": "BOWL", "is_overseas": True},
    # PBKS
    "Shreyas Iyer": {"team": "PBKS", "role": "BAT", "is_overseas": False},
    "Arshdeep Singh": {"team": "PBKS", "role": "BOWL", "is_overseas": False},
    "Yuzvendra Chahal": {"team": "PBKS", "role": "BOWL", "is_overseas": False}
}

SEASON_WEEKS = {
    "Week 1 (Mar 28 - Apr 03)": {"lock": "2026-03-28 19:00:00"},
    "Week 2 (Apr 04 - Apr 10)": {"lock": "2026-04-04 19:00:00"},
}

# --- 2. DATABASE LOGIC ---
def load_db():
    if not os.path.exists(DB_FILE):
        # Initial Manager Pools based on hardcoded 2026 list
        all_players = list(PM_2026.keys())
        return {
            "selections": {}, 
            "scores": {}, 
            "pools": {
                "Kazim": all_players[0:10],
                "Aman": all_players[10:20],
                "Aatish": all_players[20:30],
                "Shrijeet": all_players[30:40],
                "Nagle": all_players[40:]
            },
            "player_master": PM_2026
        }
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f)

# --- 3. UI LAYOUT ---
st.set_page_config(page_title="Inner Circle IPL 2026", layout="wide")

st.markdown("""<style>
    .mobile-matrix { border: 1px solid #e2e8f0; padding: 6px; border-radius: 6px; background: #fff; display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px; height: 52px; }
    .jersey-dot { height: 10px; width: 10px; border-radius: 50%; margin-right: 8px; }
    .role-label { font-size: 10px; color: #64748b; font-weight: 700; }
</style>""", unsafe_allow_html=True)

db = load_db()
db["player_master"] = PM_2026 # Force update to verified data

active_week = st.sidebar.selectbox("Select Week", list(SEASON_WEEKS.keys()))
is_locked = datetime.now() > datetime.strptime(SEASON_WEEKS[active_week]["lock"], "%Y-%m-%d %H:%M:%S")

tab1, tab2 = st.tabs(["🏏 SQUAD SELECTION", "📊 STANDINGS"])

with tab1:
    manager = st.selectbox("Manager", list(db["pools"].keys()))
    pool = db["pools"].get(manager, [])
    
    state_key = f"sel_{manager}_{active_week}"
    if state_key not in st.session_state:
        saved = db["selections"].get(active_week, {}).get(manager, {"squad": []})["squad"]
        st.session_state[state_key] = list(saved)

    # SEARCH & FILTERS
    f1, f2 = st.columns(2)
    search = f1.text_input("🔍 Search Player")
    team_filter = f2.selectbox("Filter Team", ["All Teams"] + list(TEAM_COLORS.keys()))

    # PLAYER GRID
    cols = st.columns(2)
    valid_players = [p for p in pool if search.lower() in p.lower()]
    
    for idx, p in enumerate(sorted(valid_players)):
        info = db["player_master"].get(p)
        if team_filter != "All Teams" and info["team"] != team_filter:
            continue
            
        with cols[idx % 2]:
            c1, c2 = st.columns([4, 1])
            with c1:
                st.markdown(f'''<div class="mobile-matrix">
                    <span class="jersey-dot" style="background:{TEAM_COLORS.get(info["team"], "#ccc")}"></span>
                    <div style="flex-grow:1; line-height:1.1;">
                        <span style="font-size:11px; font-weight:600;">{p} ({info["team"]})</span><br>
                        <span class="role-label">{ROLE_EMOJI.get(info["role"])} {info["role"]}</span>
                    </div>
                </div>''', unsafe_allow_html=True)
            with c2:
                in_squad = p in st.session_state[state_key]
                if st.checkbox("", key=f"chk_{p}", value=in_squad, disabled=is_locked):
                    if p not in st.session_state[state_key]:
                        st.session_state[state_key].append(p)
                        st.rerun()
                elif in_squad:
                    st.session_state[state_key].remove(p)
                    st.rerun()

    # VALIDATION
    current_squad = st.session_state[state_key]
    roles = Counter([db["player_master"][p]["role"] for p in current_squad])
    os_count = sum(1 for p in current_squad if db["player_master"][p]["is_overseas"])

    st.divider()
    st.write(f"**Count:** {len(current_squad)}/11 | **Bowlers:** {roles['BOWL']}/4+ | **WK:** {roles['WK']}/1+ | **Overseas:** {os_count}/4 max")

    if len(current_squad) == 11 and roles['BOWL'] >= 4 and roles['WK'] >= 1 and os_count <= 4:
        cap = st.selectbox("Choose Captain (2x)", current_squad)
        if st.button("SAVE SQUAD", type="primary", use_container_width=True):
            if active_week not in db["selections"]: db["selections"][active_week] = {}
            db["selections"][active_week][manager] = {"squad": current_squad, "cap": cap}
            save_db(db)
            st.success("Squad Locked!")
    else:
        st.warning("Fix squad requirements to save.")
