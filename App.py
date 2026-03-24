import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# --- 1. GLOBAL DATA & STYLING ---
TEAM_STYLING = {
    'RCB': '#d11d26', 'MI': '#004ba0', 'CSK': '#fdb913', 'SRH': '#f26522',
    'RR': '#ea1a85', 'KKR': '#3a225d', 'GT': '#1b2133', 'LSG': '#0057e2',
    'DC': '#0078bc', 'PBKS': '#dd1f2d'
}

ROLE_EMOJI = {'BAT': '🏏', 'BOWL': '🎳', 'WK': '🧤'}

SEASON_WEEKS = {
    "Week 1 (Mar 28 - Apr 03)": ["Match 01: RCB vs SRH (Sat)", "Match 02: MI vs KKR (Sun)", "Match 03: RR vs CSK (Mon)", "Match 04: PBKS vs GT (Tue)", "Match 05: LSG vs DC (Wed)", "Match 06: KKR vs SRH (Thu)", "Match 07: CSK vs PBKS (Fri)"],
    "Week 2 (Apr 04 - Apr 10)": ["Match 08: DC vs MI (Sat)", "Match 09: GT vs RR (Sat)", "Match 10: SRH vs LSG (Sun)", "Match 11: RCB vs CSK (Mon)", "Match 12: KKR vs PBKS (Tue)", "Match 13: RR vs MI (Wed)", "Match 14: DC vs GT (Thu)", "Match 15: KKR vs LSG (Fri)"]
}

DB_FILE = 'tournament_db.json'

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f: return json.load(f)
        except: pass
    return {"selections": {}, "scores": {}, "pools": {'Kazim': [], 'Adi': [], 'Aatish': [], 'Shreejith': [], 'Nagle': []}, "player_master": {}}

def save_db(data):
    with open(DB_FILE, 'w') as f: json.dump(data, f)

# --- 2. UI SETUP ---
st.set_page_config(page_title="Inner Circle IPL", layout="wide")
db = load_db()

st.sidebar.title("📅 Season Control")
current_week = st.sidebar.selectbox("Select Week", list(SEASON_WEEKS.keys()))

st.markdown("""
<style>
    .player-row { display: flex; align-items: center; padding: 5px; background: white; border-radius: 5px; margin-bottom: 3px; border: 1px solid #eee; }
    .jersey-circle { height: 12px; width: 12px; border-radius: 50%; margin-right: 10px; display: inline-block; }
    .lb-card { background: #f8fafc; padding: 12px; border-radius: 8px; border: 1px solid #e2e8f0; text-align: center; }
    .total-pts { color: #e11d48; font-size: 1.5rem; font-weight: 800; display: block; }
</style>
""", unsafe_allow_html=True)

st.title("🏆 Inner Circle IPL 2026")
t1, t2, t3 = st.tabs(["🏏 SQUAD SELECTION", "📊 STANDINGS", "🛡️ ADMIN"])

# --- TAB 1: SQUAD SELECTION ---
with t1:
    user = st.selectbox("Select Manager", list(db["pools"].keys()))
    pool = db["pools"].get(user, [])
    
    if not pool:
        st.warning("No players assigned. Use ADMIN tab to redefine pools.")
    else:
        saved = db["selections"].get(current_week, {}).get(user, {"squad": [], "cap": ""})
        cl, cr = st.columns([3, 1])
        
        selected = []
        overseas_count = 0
        
        with cl:
            grid = st.columns(3)
            for i, p in enumerate(pool):
                p_info = db["player_master"].get(p, {'team': 'RCB', 'role': 'BAT', 'is_overseas': False})
                color = TEAM_STYLING.get(p_info['team'], '#ccc')
                emoji = ROLE_EMOJI.get(p_info['role'], '🏏')
                overseas_tag = "✈️ " if p_info.get('is_overseas') else ""
                
                with grid[i % 3]:
                    st.markdown(f'''
                        <div class="player-row">
                            <span class="jersey-circle" style="background-color: {color}"></span>
                            <span>{overseas_tag}{emoji} <b>{p}</b></span>
                        </div>
                    ''', unsafe_allow_html=True)
                    if st.checkbox(f"Pick {p}", key=f"sel_{user}_{p}", value=(p in saved["squad"]), label_visibility="collapsed"):
                        selected.append(p)
                        if p_info.get('is_overseas'): overseas_count += 1
        
        with cr:
            st.metric("Total Squad", f"{len(selected)}/11")
            os_color = "normal" if overseas_count <= 4 else "inverse"
            st.metric("Overseas (Max 4)", f"{overseas_count}/4", delta_color=os_color)
            
            if len(selected) == 11:
                if overseas_count > 4:
                    st.error("Too many overseas players! Max allowed: 4")
                else:
                    cap = st.selectbox("Choose Captain (2x Pts)", selected)
                    if st.button("🚀 LOCK SQUAD", use_container_width=True):
                        if current_week not in db["selections"]: db["selections"][current_week] = {}
                        db["selections"][current_week][user] = {"squad": selected, "cap": cap}
                        save_db(db)
                        st.success("Squad Locked!")

# --- TAB 3: ADMIN (Updated for Overseas Toggle) ---
with t3:
    st.subheader("🛠️ Global Pool & Player Management")
    with st.expander("Redefine Member Player Pools"):
        for member in db["pools"].keys():
            current_p_list = ", ".join(db["pools"][member])
            new_pool = st.text_area(f"Pool for {member}", value=current_p_list, key=f"pool_{member}")
            
            c1, c2, c3 = st.columns(3)
            def_team = c1.selectbox(f"Team for {member}", list(TEAM_STYLING.keys()), key=f"t_{member}")
            def_role = c2.selectbox(f"Role for {member}", ["BAT", "BOWL", "WK"], key=f"r_{member}")
            def_os = c3.checkbox(f"Overseas? ✈️", key=f"os_{member}")
            
            if st.button(f"Update {member}"):
                names = [n.strip() for n in new_pool.split(",") if n.strip()]
                db["pools"][member] = names
                for n in names:
                    # Update or add player info
                    db["player_master"][n] = {"team": def_team, "role": def_role, "is_overseas": def_os}
                save_db(db)
                st.success(f"Updated {member}!")
                
