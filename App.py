import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# --- 1. GLOBAL DATA & FULL SEASON SCHEDULE ---
TEAM_STYLING = {
    'RCB': '#d11d26', 'MI': '#004ba0', 'CSK': '#fdb913', 'SRH': '#f26522',
    'RR': '#ea1a85', 'KKR': '#3a225d', 'GT': '#1b2133', 'LSG': '#0057e2',
    'DC': '#0078bc', 'PBKS': '#dd1f2d'
}

# Detailed Weekly Schedule for the Calendar View
SEASON_WEEKS = {
    "Week 1": ["Match 01: RCB vs SRH", "Match 02: MI vs KKR", "Match 03: RR vs CSK"],
    "Week 2": ["Match 04: PBKS vs GT", "Match 05: LSG vs DC", "Match 06: KKR vs SRH"],
    "Week 3": ["Match 07: CSK vs PBKS", "Match 08: DC vs MI", "Match 09: GT vs RR"],
    "Week 4": ["Match 10: SRH vs LSG", "Match 11: RCB vs CSK", "Match 12: KKR vs PBKS"],
    "Week 5": ["Match 13: RR vs MI", "Match 14: DC vs GT", "Match 15: KKR vs LSG"],
    "Week 6": ["Match 16: RR vs RCB", "Match 17: PBKS vs SRH", "Match 18: CSK vs DC"],
    "Week 7": ["Qualifier 1", "Eliminator", "Qualifier 2", "Final"]
}

# (MEMBER_POOLS and PLAYER_MASTER remain the same)
# ... [Data Load Omitted] ...

DB_FILE = 'tournament_db.json'
def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f: return json.load(f)
        except: pass
    return {"selections": {}, "scores": {}, "totals": {m: 0 for m in MEMBER_POOLS.keys()}, "last_updated": "Never"}

def save_db(data):
    data["last_updated"] = datetime.now().strftime("%d %b, %H:%M")
    with open(DB_FILE, 'w') as f: json.dump(data, f)

# --- 2. UI SETUP ---
st.set_page_config(page_title="IPL Manager 2026", layout="wide")
db = load_db()

# Sidebar: Week Selector & Mini Calendar
st.sidebar.title("📅 Season Control")
current_week = st.sidebar.selectbox("Active Week", list(SEASON_WEEKS.keys()))

# --- CALENDAR OVERVIEW LOGIC ---
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Match Counts")
# Calculate how many times each team plays in the selected week
match_list = SEASON_WEEKS[current_week]
team_counts = {}
for match in match_list:
    if "vs" in match:
        teams = match.split(":")[1].split(" vs ")
        for t in teams:
            t = t.strip()
            team_counts[t] = team_counts.get(t, 0) + 1

# Display counts in sidebar
for team, count in sorted(team_counts.items(), key=lambda x: x[1], reverse=True):
    color = TEAM_STYLING.get(team, "#ccc")
    st.sidebar.markdown(f"**{team}**: {count} Match{'es' if count > 1 else ''} 🟡")

st.title("🏆 Inner Circle IPL 2026")
tab1, tab2, tab4 = st.tabs(["🏏 TEAM SELECTION", "📊 STANDINGS", "🛡️ ADMIN"])

# --- TAB 1: SELECTION & CALENDAR ---
with tab1:
    # 1. Top Section: Visual Match Calendar for the Week
    st.subheader(f"Schedule for {current_week}")
    cols = st.columns(len(match_list))
    for i, match in enumerate(match_list):
        with cols[i]:
            st.info(f"🏟️ {match}")

    st.divider()

    # 2. Squad Selection
    user = st.selectbox("Manager", list(MEMBER_POOLS.keys()))
    pool = MEMBER_POOLS[user]
    saved_squad = db["selections"].get(current_week, {}).get(user, {}).get("squad", [])
    
    col_l, col_r = st.columns([3, 1])
    with col_l:
        selected_names = []
        counts = {"BAT": 0, "BOWL": 0, "WK": 0}
        grid = st.columns(3)
        for i, p_name in enumerate(pool):
            p_info = PLAYER_MASTER.get(p_name, {'team': 'RCB', 'role': 'BAT'})
            color = TEAM_STYLING.get(p_info['team'], '#ccc')
            with grid[i % 3]:
                # Visual Highlight if player's team is playing this week
                is_playing = p_info['team'] in team_counts
                border_style = f"border-left: 5px solid {color}" if is_playing else "border-left: 5px solid #eee; opacity: 0.5;"
                
                st.markdown(f'''
                    <div style="padding:5px; margin:2px; background:white; {border_style} border-radius:4px;">
                        <span style="font-size:0.85rem;"><b>{p_name}</b> ({p_info['team']})</span>
                    </div>
                ''', unsafe_allow_html=True)
                
                if st.checkbox(f"Pick {p_name}", key=f"p_{user}_{p_name}_{current_week}", value=(p_name in saved_squad), label_visibility="collapsed"):
                    selected_names.append(p_name)
                    counts[p_info['role']] += 1
    
    with col_r:
        st.metric("Total Selected", f"{len(selected_names)}/11")
        st.progress(len(selected_names)/11)
        if len(selected_names) == 11:
            cap = st.selectbox("Assign Captain", selected_names, key=f"cap_{user}_{current_week}")
            if st.button("🚀 LOCK SQUAD", use_container_width=True):
                # Save Logic
                st.success("Squad Registered!")

# --- TAB 2: STANDINGS ---
# (Stays same as previous version)

# --- TAB 4: ADMIN ---
with tab4:
    # (Scoring and Nuclear Safety buttons remain as provided before)
    pass
            
