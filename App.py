import streamlit as st
import pandas as pd
import json
import os

# --- 1. SETTINGS & SEASON SCOPE ---
TEAM_COLORS = {'RCB': '#d11d26', 'MI': '#004ba0', 'CSK': '#fdb913', 'SRH': '#f26522', 'RR': '#ea1a85', 'KKR': '#3a225d', 'GT': '#1b2133', 'LSG': '#0057e2', 'DC': '#0078bc', 'PBKS': '#dd1f2d', 'IPL': '#000080'}
ROLE_EMOJI = {'BAT': '🏏', 'BOWL': '⚾', 'WK': '🧤'}

# Saturday to Friday Logic - Extended for Playoffs
SEASON_WEEKS = {
    "Week 1 (Mar 28 - Apr 03)": {"M01": "RCB vs SRH", "M02": "MI vs KKR", "M03": "RR vs CSK", "M04": "PBKS vs GT", "M05": "LSG vs DC", "M06": "KKR vs SRH", "M07": "CSK vs PBKS"},
    "Week 2 (Apr 04 - Apr 10)": {"M08": "DC vs MI", "M09": "GT vs RR", "M10": "SRH vs LSG", "M11": "RCB vs CSK", "M12": "KKR vs PBKS", "M13": "RR vs MI", "M14": "DC vs GT"},
    "Playoffs": {"SF1": "TBD vs TBD", "SF2": "TBD vs TBD", "FIN": "Final Match"}
}

# --- 2. UI STYLING (Ultra-Compact) ---
st.set_page_config(page_title="Inner Circle IPL", layout="wide")
st.markdown("""
<style>
    .rule-box { background: #fffbeb; border: 1px solid #fcd34d; padding: 10px; border-radius: 8px; font-size: 12px; margin-bottom: 15px; }
    .player-card { border: 1px solid #e2e8f0; padding: 5px 10px; border-radius: 6px; background: #fff; display: flex; align-items: center; justify-content: space-between; }
    .jersey-dot { height: 8px; width: 8px; border-radius: 50%; margin-right: 5px; }
    .manager-stat { background: #f1f5f9; padding: 10px; border-radius: 8px; text-align: center; border: 1px solid #cbd5e1; }
    .match-count { font-size: 10px; color: #ef4444; font-weight: bold; margin-left: 5px; }
</style>
""", unsafe_allow_html=True)

# --- 3. LOGIC: CALCULATE MATCHES PER TEAM ---
def get_team_match_counts(week_name):
    counts = {}
    matches = SEASON_WEEKS[week_name]
    for m in matches.values():
        teams = m.split(" vs ")
        for t in teams:
            counts[t] = counts.get(t, 0) + 1
    return counts

# --- 4. DATA ENGINE ---
DB_FILE = 'tournament_db.json'
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f: return json.load(f)
    return {"selections": {}, "scores": {}, "pools": {}, "player_master": {}}

db = load_db()

# --- 5. SIDEBAR: FULL SEASON VIEW ---
st.sidebar.title("🗓️ Season Schedule")
sel_week = st.sidebar.selectbox("Active Week", list(SEASON_WEEKS.keys()))
team_counts = get_team_match_counts(sel_week)

for mid, m_text in SEASON_WEEKS[sel_week].items():
    teams = m_text.split(" vs ")
    t_labels = [f"{t}({team_counts.get(t,0)})" for t in teams]
    st.sidebar.markdown(f"**{mid}:** {' vs '.join(t_labels)}")

# --- 6. MAIN APP ---
st.title("🏆 Inner Circle IPL 2026")

t1, t2, t3 = st.tabs(["🏏 SQUAD & RULES", "📊 LEADERBOARD", "🛡️ ADMIN"])

with t1:
    # --- RULES SECTION ---
    st.markdown("""
    <div class="rule-box">
        <b>📏 Selection Rules:</b><br>
        • Total 11 Players • Max 4 Overseas (✈️) • Select 1 Captain (2x Pts) • Transfers reset every Saturday.
    </div>
    """, unsafe_allow_html=True)

    user = st.selectbox("Manager", list(db["pools"].keys()))
    pool = db["pools"].get(user, [])
    saved = db["selections"].get(sel_week, {}).get(user, {"squad": [], "cap": ""})
    
    # --- SELECTION GRID (4-Columns, Inline Checkbox) ---
    cols = st.columns(4)
    selected = []
    os_count = 0

    for idx, p in enumerate(pool):
        p_info = db["player_master"].get(p, {'team': 'IPL', 'role': 'BAT', 'is_overseas': False})
        color = TEAM_COLORS.get(p_info['team'], '#ccc')
        emoji = ROLE_EMOJI.get(p_info['role'], '🏏')
        os_icon = "✈️" if p_info['is_overseas'] else ""
        
        with cols[idx % 4]:
            # Container for player info and checkbox in one line
            c_label, c_box = st.columns([4, 1])
            with c_label:
                st.markdown(f'<div class="player-card"><span class="jersey-dot" style="background:{color}"></span><small>{p} {os_icon}</small></div>', unsafe_allow_html=True)
            with c_box:
                if st.checkbox("", key=f"sel_{user}_{p}", value=(p in saved["squad"]), label_visibility="collapsed"):
                    selected.append(p)
                    if p_info['is_overseas']: os_count += 1

    # --- SUBMIT BAR ---
    st.divider()
    b1, b2, b3 = st.columns([1, 1, 2])
    b1.metric("Squad", f"{len(selected)}/11")
    b2.metric("Overseas", f"{os_count}/4")
    
    if len(selected) == 11 and os_count <= 4:
        cap = b3.selectbox("Select Captain", selected, index=selected.index(saved["cap"]) if saved["cap"] in selected else 0)
        if st.button("🚀 SUBMIT SQUAD", use_container_width=True):
            if sel_week not in db["selections"]: db["selections"][sel_week] = {}
            db["selections"][sel_week][user] = {"squad": selected, "cap": cap}
            # save_db(db)
            st.success("Squad Submitted!")
    elif os_count > 4: st.error("Reduce Overseas players to 4!")

with t2:
    st.subheader("📊 Season Rankings")
    lb_data = []
    for m in db["pools"].keys():
        total_pts = 0
        # Calculate for ALL weeks
        for wk, matches in SEASON_WEEKS.items():
            sel = db["selections"].get(wk, {}).get(m, {"squad": [], "cap": ""})
            for p in sel["squad"]:
                p_sc = db["scores"].get(p, {})
                pts = sum([v for k, v in p_sc.items() if k in matches])
                total_pts += (pts * 2) if p == sel["cap"] else pts
        lb_data.append({"Manager": m, "Points": total_pts})
    
    df_lb = pd.DataFrame(lb_data).sort_values("Points", ascending=False)
    
    # Visual Cards for Top 3
    top_cols = st.columns(len(df_lb))
    for i, row in enumerate(df_lb.itertuples()):
        top_cols[i].markdown(f'<div class="manager-stat"><b>{row.Manager}</b><br><span style="font-size:20px; color:#1e293b;">{row.Points}</span></div>', unsafe_allow_html=True)

with t3:
    st.subheader("🛡️ Admin Scoring")
    sel_mid = st.selectbox("Select Match (Including Playoffs)", [m for w in SEASON_WEEKS.values() for m in w.keys()])
    # Scoring logic based on Match ID (M01, SF1, etc.)
    # ... (Filtered scoring logic from previous version)
    
