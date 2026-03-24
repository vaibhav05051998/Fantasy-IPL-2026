import streamlit as st
import pandas as pd
import json
import os

# --- 1. CONFIG & SMART MAPPING ---
TEAM_COLORS = {'RCB': '#d11d26', 'MI': '#004ba0', 'CSK': '#fdb913', 'SRH': '#f26522', 'RR': '#ea1a85', 'KKR': '#3a225d', 'GT': '#1b2133', 'LSG': '#0057e2', 'DC': '#0078bc', 'PBKS': '#dd1f2d', 'IPL': '#000080'}
ROLE_EMOJI = {'BAT': '🏏', 'BOWL': '⚾', 'WK': '🧤'}

# Saturday to Friday Week Logic with Match Numbers
SEASON_WEEKS = {
    "Week 1 (Mar 28 - Apr 03)": {
        "M01": "RCB vs SRH", "M02": "MI vs KKR", "M03": "RR vs CSK", 
        "M04": "PBKS vs GT", "M05": "LSG vs DC", "M06": "KKR vs SRH", "M07": "CSK vs PBKS"
    },
    "Week 2 (Apr 04 - Apr 10)": {
        "M08": "DC vs MI", "M09": "GT vs RR", "M10": "SRH vs LSG", 
        "M11": "RCB vs CSK", "M12": "KKR vs PBKS", "M13": "RR vs MI", "M14": "DC vs GT"
    }
}

# --- 2. DATABASE ENGINE ---
DB_FILE = 'tournament_db.json'
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f: return json.load(f)
    return {"selections": {}, "scores": {}, "pools": {}, "player_master": {}}

db = load_db()

# --- 3. UI STYLING (Compact Grid & Zero Scroll) ---
st.set_page_config(page_title="Inner Circle IPL 2026", layout="wide")
st.markdown("""
<style>
    .player-card { border: 1px solid #e2e8f0; padding: 10px; border-radius: 10px; background: #fff; margin-bottom: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .jersey-dot { height: 10px; width: 10px; border-radius: 50%; display: inline-block; margin-right: 6px; }
    .meta-text { font-size: 11px; color: #64748b; font-weight: 600; }
    .match-pill { background: #f1f5f9; padding: 2px 10px; border-radius: 20px; font-size: 12px; font-weight: 700; color: #475569; }
</style>
""", unsafe_allow_html=True)

# --- 4. SIDEBAR & NAVIGATION ---
st.sidebar.title("📅 Season Control")
sel_week = st.sidebar.selectbox("Select Week", list(SEASON_WEEKS.keys()))
matches_this_week = SEASON_WEEKS[sel_week]

st.sidebar.markdown("### Matches this Week")
for mid, teams in matches_this_week.items():
    st.sidebar.markdown(f"<span class='match-pill'>{mid}</span> {teams}", unsafe_allow_html=True)

st.title("🏆 Inner Circle IPL 2026")
t1, t2, t3 = st.tabs(["🏏 SQUAD SELECTION", "📊 STANDINGS", "🛡️ ADMIN"])

# --- TAB 1: SQUAD SELECTION (4-COL COMPACT GRID) ---
with t1:
    user = st.selectbox("Manager", list(db["pools"].keys()))
    pool = db["pools"].get(user, [])
    
    # 4 Columns to minimize scrolling
    cols = st.columns(4)
    selected = []
    
    for idx, p in enumerate(pool):
        p_info = db["player_master"].get(p, {'team': 'IPL', 'role': 'BAT', 'is_overseas': False})
        color = TEAM_COLORS.get(p_info['team'], '#ccc')
        emoji = ROLE_EMOJI.get(p_info['role'], '🏏')
        os_icon = "✈️" if p_info['is_overseas'] else ""
        
        with cols[idx % 4]:
            st.markdown(f'''
                <div class="player-card">
                    <span class="jersey-dot" style="background:{color}"></span>
                    <b>{p}</b><br>
                    <span class="meta-text">{p_info['team']} | {emoji} {os_icon}</span>
                </div>
            ''', unsafe_allow_html=True)
            if st.checkbox("Pick", key=f"sel_{user}_{p}", label_visibility="collapsed"):
                selected.append(p)
    
    # Validation & Locking logic... (Previous code remains)

# --- TAB 3: ADMIN (SMART SCORING BY MATCH NUMBER) ---
with t3:
    st.subheader("🛡️ Admin Scoring Console")
    
    # Select Match Number first
    sel_mid = st.selectbox("Select Match Number", list(matches_this_week.keys()))
    match_teams = matches_this_week[sel_mid]
    st.info(f"Scoring for **{sel_mid}: {match_teams}**")
    
    # Filter players who belong to the teams in this match
    playing_teams = match_teams.split(" vs ")
    eligible = [p for p, info in db["player_master"].items() if info['team'] in playing_teams]
    
    if not eligible:
        st.warning("No players from these teams found in any manager's pool.")
    else:
        # Show players in a clean list for scoring
        for p in sorted(eligible):
            p_team = db["player_master"][p]['team']
            with st.expander(f"{p} ({p_team})"):
                cur_sc = db["scores"].get(p, {}).get(sel_mid, 0)
                score = st.number_input(f"Points in {sel_mid}", 0, value=int(cur_sc), key=f"sc_{sel_mid}_{p}")
                if st.button(f"Update {p}"):
                    if p not in db["scores"]: db["scores"][p] = {}
                    db["scores"][p][sel_mid] = score
                    # save_db(db) logic
                    st.toast(f"Points updated for {p}!")
    
