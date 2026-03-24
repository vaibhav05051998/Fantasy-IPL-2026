import streamlit as st
import pandas as pd
import json
import os

# --- 1. CONFIG & STYLING ---
TEAM_STYLING = {
    'RCB': '#d11d26', 'MI': '#004ba0', 'CSK': '#fdb913', 'SRH': '#f26522',
    'RR': '#ea1a85', 'KKR': '#3a225d', 'GT': '#1b2133', 'LSG': '#0057e2',
    'DC': '#0078bc', 'PBKS': '#dd1f2d'
}

IPL_SCHEDULE = ["Match 01: RCB vs SRH (Mar 28)", "Match 02: MI vs KKR (Mar 29)", "Match 03: RR vs CSK (Mar 30)"]

# (PLAYER_MASTER and MEMBER_POOLS same as previous)
# ... [Data Load Omitted for Brevity] ...

DB_FILE = 'tournament_db.json'
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f: return json.load(f)
    return {"selections": {}, "scores": {}, "totals": {m: 0 for m in MEMBER_POOLS.keys()}}

def save_db(data):
    with open(DB_FILE, 'w') as f: json.dump(data, f)

# --- 2. HEADER & STYLE ---
st.set_page_config(page_title="IPL Manager 2026", layout="wide")
db = load_db()
week = "1"

st.markdown("""
<style>
    .player-row { border-radius: 5px; padding: 5px 10px; margin: 2px 0; background: white; border-left: 5px solid #ccc; display: flex; align-items: center; }
    .dot { height: 12px; width: 12px; border-radius: 50%; display: inline-block; margin-right: 10px; }
    .leaderboard-card { background: #fdfdfd; padding: 10px; border-radius: 8px; border: 1px solid #eee; text-align: center; }
    h3 { margin-bottom: 0px; font-size: 1.1rem !important; }
    .pts-text { font-size: 0.9rem; color: #666; }
</style>
""", unsafe_allow_html=True)

st.title("🏆 Inner Circle IPL 2026")

tab1, tab2, tab3, tab4 = st.tabs(["🏏 SELECTION", "📊 STANDINGS", "📜 LOGS", "🛡️ ADMIN"])

# --- TAB 1: SELECTION (COMPACT) ---
with tab1:
    user = st.selectbox("Manager", list(MEMBER_POOLS.keys()))
    pool = MEMBER_POOLS[user]
    saved_squad = db["selections"].get(week, {}).get(user, {}).get("squad", [])
    
    col_l, col_r = st.columns([3, 1])
    with col_l:
        selected_names = []
        counts = {"BAT": 0, "BOWL": 0, "WK": 0}
        grid = st.columns(3)
        for i, p_name in enumerate(pool):
            p_info = PLAYER_MASTER.get(p_name, {'team': 'RCB', 'role': 'BAT'})
            color = TEAM_STYLING.get(p_info['team'], '#ccc')
            with grid[i % 3]:
                st.markdown(f'<div class="player-row" style="border-left-color: {color}"><span class="dot" style="background-color: {color}"></span><b>{p_name}</b></div>', unsafe_allow_html=True)
                if st.checkbox("Pick", key=f"p_{user}_{p_name}", value=(p_name in saved_squad)):
                    selected_names.append(p_name)
                    counts[p_info['role']] += 1
    with col_r:
        st.metric("Total", f"{len(selected_names)}/11")
        if len(selected_names) > 0:
            cap = st.selectbox("Captain", selected_names)
            if st.button("🚀 LOCK SQUAD", use_container_width=True):
                if len(selected_names) == 11 and counts['WK'] >= 1 and counts['BOWL'] >= 5:
                    if week not in db["selections"]: db["selections"][week] = {}
                    db["selections"][week][user] = {"squad": selected_names, "cap": cap}
                    save_db(db)
                    st.success("Squad Locked!")
                else: st.error("Invalid Balance")

# --- TAB 2: LEADERBOARD (FIXED FONT & SINGLE SCREEN) ---
with tab2:
    lb_cols = st.columns(len(MEMBER_POOLS))
    lb_data = []
    for i, m in enumerate(MEMBER_POOLS.keys()):
        w_pts = 0
        m_data = db["selections"].get(week, {}).get(m, {"squad": [], "cap": ""})
        for p in m_data["squad"]:
            p_pts = sum(db["scores"].get(p, {}).values())
            w_pts += (p_pts * 2) if p == m_data["cap"] else p_pts
        total = db["totals"][m] + w_pts
        lb_data.append({"Member": m, "Weekly": w_pts, "Total": total})
        
        with lb_cols[i]:
            st.markdown(f"""
            <div class="leaderboard-card">
                <h3>{m}</h3>
                <div class="pts-text">Weekly: <b>{w_pts}</b></div>
                <div style="font-size: 1.3rem; color: #ff4b4b; font-weight: bold;">{total} Total</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("---")
    st.table(pd.DataFrame(lb_data).sort_values("Total", ascending=False))

# --- TAB 4: ADMIN (PUSH & CLEAR BUTTONS) ---
with tab4:
    st.subheader("Admin Scoring")
    selected_match = st.selectbox("Match", IPL_SCHEDULE)
    
    # Filter only selected players
    selected_by_anyone = set()
    for m in db["selections"].get(week, {}).values():
        selected_by_anyone.update(m["squad"])
    match_teams = selected_match.split(":")[1].split("(")[0].strip().split(" vs ")
    active = [p for p in selected_by_anyone if PLAYER_MASTER.get(p, {}).get('team') in match_teams]

    new_match_scores = {}
    for p_name in sorted(active):
        with st.expander(f"● {p_name} ({PLAYER_MASTER[p_name]['team']})"):
            c1, c2, c3 = st.columns(3)
            r = c1.number_input("Runs", 0, key=f"r_{p_name}")
            w = c2.number_input("Wickets", 0, key=f"w_{p_name}") if PLAYER_MASTER[p_name]['role'] != 'BAT' else 0
            f = c3.number_input("Fielding (5pt)", 0, key=f"f_{p_name}")
            new_match_scores[p_name] = r + (w * 20) + (f * 5)

    # ACTION BUTTONS
    st.markdown("---")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        if st.button("🔥 PUSH POINTS TO LEADERBOARD", use_container_width=True, type="primary"):
            for p, pts in new_match_scores.items():
                if p not in db["scores"]: db["scores"][p] = {}
                db["scores"][p][selected_match] = pts
            save_db(db)
            st.success("Points Pushed!")
    with col_p2:
        if st.button("🗑️ CLEAR ALL SCORES (RESET)", use_container_width=True):
            db["scores"] = {}
            save_db(db)
            st.warning("All match scores have been wiped.")
            st.rerun()
            
