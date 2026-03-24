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
    # Initialize default structure
    default = {
        "selections": {}, 
        "scores": {}, 
        "pools": {'Kazim': [], 'Adi': [], 'Aatish': [], 'Shreejith': [], 'Nagle': []}, 
        "player_master": {}
    }
    
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f:
                data = json.load(f)
                # Self-healing: Ensure all keys exist
                for key in default:
                    if key not in data:
                        data[key] = default[key]
                return data
        except:
            return default
    return default

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f)

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
        st.warning("⚠️ No players in your pool. Admin must add players in the ADMIN tab.")
    else:
        saved = db["selections"].get(current_week, {}).get(user, {"squad": [], "cap": ""})
        cl, cr = st.columns([3, 1])
        
        selected = []
        os_count = 0
        
        with cl:
            grid = st.columns(3)
            for i, p in enumerate(pool):
                p_info = db["player_master"].get(p, {'team': 'RCB', 'role': 'BAT', 'is_overseas': False})
                color = TEAM_STYLING.get(p_info.get('team', 'RCB'), '#ccc')
                emoji = ROLE_EMOJI.get(p_info.get('role', 'BAT'), '🏏')
                os_tag = "✈️ " if p_info.get('is_overseas') else ""
                
                with grid[i % 3]:
                    st.markdown(f'''
                        <div class="player-row">
                            <span class="jersey-circle" style="background-color: {color}"></span>
                            <span>{os_tag}{emoji} <b>{p}</b></span>
                        </div>
                    ''', unsafe_allow_html=True)
                    if st.checkbox(f"Pick {p}", key=f"sel_{user}_{p}", value=(p in saved["squad"]), label_visibility="collapsed"):
                        selected.append(p)
                        if p_info.get('is_overseas'): os_count += 1
        
        with cr:
            st.metric("Total Players", f"{len(selected)}/11")
            st.metric("Overseas ✈️", f"{os_count}/4")
            
            if len(selected) == 11:
                if os_count > 4:
                    st.error("Too many overseas! Limit is 4.")
                else:
                    cap = st.selectbox("Choose Captain", selected, index=selected.index(saved["cap"]) if saved["cap"] in selected else 0)
                    if st.button("🚀 LOCK SQUAD", use_container_width=True):
                        if current_week not in db["selections"]: db["selections"][current_week] = {}
                        db["selections"][current_week][user] = {"squad": selected, "cap": cap}
                        save_db(db)
                        st.success("Squad Saved!")

# --- TAB 2: STANDINGS ---
with t2:
    lb_list = []
    cols = st.columns(len(db["pools"]))
    for i, m in enumerate(db["pools"].keys()):
        w_pts = 0
        m_curr = db["selections"].get(current_week, {}).get(m, {"squad": [], "cap": ""})
        for p in m_curr["squad"]:
            sc = db["scores"].get(p, {})
            pts = sum([v for k, v in sc.items() if k in SEASON_WEEKS[current_week]])
            w_pts += (pts * 2) if p == m_curr["cap"] else pts
        
        t_pts = 0
        for wk, matches in SEASON_WEEKS.items():
            m_wk = db["selections"].get(wk, {}).get(m, {"squad": [], "cap": ""})
            for p in m_wk["squad"]:
                sc = db["scores"].get(p, {})
                pts = sum([v for k, v in sc.items() if k in matches])
                t_pts += (pts * 2) if p == m_wk["cap"] else pts
        
        lb_list.append({"Manager": m, "Total": t_pts})
        with cols[i]:
            st.markdown(f'<div class="lb-card"><b>{m}</b><br><small>Week: {w_pts}</small><span class="total-pts">{t_pts}</span></div>', unsafe_allow_html=True)

# --- TAB 3: ADMIN ---
with t3:
    st.subheader("🛡️ Pool Management")
    for member in db["pools"].keys():
        with st.expander(f"Edit {member}'s Pool"):
            cur_names = ", ".join(db["pools"][member])
            new_names = st.text_area("Names (Comma separated)", value=cur_names, key=f"area_{member}")
            
            c1, c2, c3 = st.columns(3)
            t = c1.selectbox("Team", list(TEAM_STYLING.keys()), key=f"t_{member}")
            r = c2.selectbox("Role", ["BAT", "BOWL", "WK"], key=f"r_{member}")
            o = c3.checkbox("Overseas? ✈️", key=f"o_{member}")
            
            if st.button(f"Update {member}"):
                name_list = [n.strip() for n in new_names.split(",") if n.strip()]
                db["pools"][member] = name_list
                for n in name_list:
                    db["player_master"][n] = {"team": t, "role": r, "is_overseas": o}
                save_db(db)
                st.rerun()

    st.divider()
    st.subheader("🏏 Scoring")
    all_m = [m for sub in SEASON_WEEKS.values() for m in sub]
    sel_m = st.selectbox("Select Match", all_m)
    
    # Simple scoring logic for players in that week
    picked = set()
    for wk_data in db["selections"].get(current_week, {}).values():
        picked.update(wk_data["squad"])
    
    for p in sorted(picked):
        with st.expander(f"Score {p}"):
            val = st.number_input("Total Points", 0, key=f"sc_{p}_{sel_m}")
            if st.button(f"Save {p}"):
                if p not in db["scores"]: db["scores"][p] = {}
                db["scores"][p][sel_m] = val
                save_db(db)
                st.toast(f"Saved {p}")
