import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# --- 1. CONFIG & DATA ---
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
    default = {
        "selections": {}, "scores": {}, "player_master": {},
        "pools": {'Kazim': [], 'Adi': [], 'Aatish': [], 'Shreejith': [], 'Nagle': []}
    }
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f:
                data = json.load(f)
                for key in default:
                    if key not in data: data[key] = default[key]
                return data
        except: return default
    return default

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
    .lb-card { background: #f8fafc; padding: 12px; border-radius: 8px; border: 1px solid #e2e8f0; text-align: center; min-width: 120px; }
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
        selected, os_count = [], 0
        
        with cl:
            grid = st.columns(3)
            for i, p in enumerate(pool):
                p_info = db["player_master"].get(p, {'team': 'RCB', 'role': 'BAT', 'is_overseas': False})
                color = TEAM_STYLING.get(p_info.get('team'), '#ccc')
                emoji = ROLE_EMOJI.get(p_info.get('role'), '🏏')
                os_tag = "✈️ " if p_info.get('is_overseas') else ""
                
                with grid[i % 3]:
                    st.markdown(f'<div class="player-row"><span class="jersey-circle" style="background-color: {color}"></span><span>{os_tag}{emoji} <b>{p}</b></span></div>', unsafe_allow_html=True)
                    if st.checkbox(f"Pick {p}", key=f"sel_{user}_{p}", value=(p in saved["squad"]), label_visibility="collapsed"):
                        selected.append(p)
                        if p_info.get('is_overseas'): os_count += 1
        with cr:
            st.metric("Total Players", f"{len(selected)}/11")
            st.metric("Overseas ✈️", f"{os_count}/4")
            if len(selected) == 11 and os_count <= 4:
                cap = st.selectbox("Choose Captain", selected, index=selected.index(saved["cap"]) if saved["cap"] in selected else 0)
                if st.button("🚀 LOCK SQUAD", use_container_width=True):
                    if current_week not in db["selections"]: db["selections"][current_week] = {}
                    db["selections"][current_week][user] = {"squad": selected, "cap": cap}
                    save_db(db)
                    st.success("Squad Saved!")
            elif os_count > 4: st.error("Max 4 Overseas!")

# --- TAB 2: STANDINGS ---
with t2:
    lb_list = []
    cols = st.columns(len(db["pools"]))
    for i, m in enumerate(db["pools"].keys()):
        w_pts = 0
        m_curr = db["selections"].get(current_week, {}).get(m, {"squad": [], "cap": ""})
        for p in m_curr["squad"]:
            pts = db["scores"].get(p, {}).get(st.session_state.get('last_match', ""), 0) # Simplified for current match view
            # Standard weekly calc
            p_scores = db["scores"].get(p, {})
            week_total = sum([v for k, v in p_scores.items() if k in SEASON_WEEKS[current_week]])
            w_pts += (week_total * 2) if p == m_curr["cap"] else week_total
        
        t_pts = 0
        for wk_key, wk_matches in SEASON_WEEKS.items():
            m_wk = db["selections"].get(wk_key, {}).get(m, {"squad": [], "cap": ""})
            for p in m_wk["squad"]:
                p_sc = db["scores"].get(p, {})
                pts = sum([v for k, v in p_sc.items() if k in wk_matches])
                t_pts += (pts * 2) if p == m_wk["cap"] else pts
        
        lb_list.append({"Manager": m, "Weekly": w_pts, "Total": t_pts})
        with cols[i]:
            st.markdown(f'<div class="lb-card"><b>{m}</b><br><small>Week: {w_pts}</small><span class="total-pts">{t_pts}</span></div>', unsafe_allow_html=True)
    
    st.divider()
    st.subheader("Leaderboard Table")
    st.dataframe(pd.DataFrame(lb_list).sort_values("Total", ascending=False), use_container_width=True)

# --- TAB 3: ADMIN ---
with t3:
    st.subheader("🏏 Primary Function: Match Scoring")
    all_m = [m for sub in SEASON_WEEKS.values() for m in sub]
    sel_m = st.selectbox("Select Match to Score", all_m)
    st.session_state['last_match'] = sel_m
    
    # Show only players selected by ANYONE this week to save space
    picked = set()
    for wk_data in db["selections"].get(current_week, {}).values():
        picked.update(wk_data["squad"])
    
    if not picked: st.info("No squads locked yet for this week.")
    else:
        for p in sorted(picked):
            with st.expander(f"Score {p} ({db['player_master'].get(p, {}).get('team', '?')})"):
                cur_sc = db["scores"].get(p, {}).get(sel_m, 0)
                val = st.number_input(f"Points in {sel_m}", 0, value=cur_sc, key=f"sc_{p}_{sel_m}")
                if st.button(f"Update {p}", key=f"btn_{p}"):
                    if p not in db["scores"]: db["scores"][p] = {}
                    db["scores"][p][sel_m] = val
                    save_db(db)
                    st.toast(f"Updated {p} to {val}")

    st.divider()
    
    st.subheader("⚙️ Secondary Function: Pool Management")
    with st.expander("Add/Remove Players from Pools"):
        member = st.selectbox("Choose Manager to Edit", list(db["pools"].keys()))
        
        # 1. Add Player
        st.write(f"--- Add to {member}'s Pool ---")
        c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
        new_p = c1.text_input("Player Name")
        new_t = c2.selectbox("Team", list(TEAM_STYLING.keys()))
        new_r = c3.selectbox("Role", ["BAT", "BOWL", "WK"])
        new_o = c4.checkbox("Overseas? ✈️")
        
        if st.button(f"➕ Add {new_p} to {member}"):
            if new_p and new_p not in db["pools"][member]:
                db["pools"][member].append(new_p)
                db["player_master"][new_p] = {"team": new_t, "role": new_r, "is_overseas": new_o}
                save_db(db)
                st.success(f"Added {new_p}")
                st.rerun()

        # 2. Remove Player
        st.write(f"--- Remove from {member}'s Pool ---")
        p_to_rem = st.selectbox("Select Player to Remove", [""] + db["pools"][member])
        if st.button(f"🗑️ Remove {p_to_rem}"):
            if p_to_rem in db["pools"][member]:
                db["pools"][member].remove(p_to_rem)
                save_db(db)
                st.warning(f"Removed {p_to_rem}")
                st.rerun()
                        
