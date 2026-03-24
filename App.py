import streamlit as st
import pandas as pd
import json
import os

# --- 1. SETTINGS & SEASON SCOPE ---
TEAM_COLORS = {'RCB': '#d11d26', 'MI': '#004ba0', 'CSK': '#fdb913', 'SRH': '#f26522', 'RR': '#ea1a85', 'KKR': '#3a225d', 'GT': '#1b2133', 'LSG': '#0057e2', 'DC': '#0078bc', 'PBKS': '#dd1f2d', 'IPL': '#000080'}
ROLE_EMOJI = {'BAT': '🏏', 'BOWL': '⚾', 'WK': '🧤'}

SEASON_WEEKS = {
    "Week 1 (Mar 28 - Apr 03)": {"M01": "RCB vs SRH", "M02": "MI vs KKR", "M03": "RR vs CSK", "M04": "PBKS vs GT", "M05": "LSG vs DC", "M06": "KKR vs SRH", "M07": "CSK vs PBKS"},
    "Week 2 (Apr 04 - Apr 10)": {"M08": "DC vs MI", "M09": "GT vs RR", "M10": "SRH vs LSG", "M11": "RCB vs CSK", "M12": "KKR vs PBKS", "M13": "RR vs MI", "M14": "DC vs GT"},
    "Playoffs": {"SF1": "TBD vs TBD", "SF2": "TBD vs TBD", "FIN": "Final Match"}
}

# --- 2. UI STYLING (Matrix & Leaderboard) ---
st.set_page_config(page_title="Inner Circle IPL", layout="wide")
st.markdown("""
<style>
    .rule-box { background: #fffbeb; border: 1px solid #fcd34d; padding: 10px; border-radius: 8px; font-size: 13px; margin-bottom: 10px; }
    .matrix-cell { border: 1px solid #e2e8f0; padding: 4px 8px; border-radius: 4px; background: #fff; display: flex; align-items: center; justify-content: space-between; height: 35px; }
    .jersey-dot { height: 8px; width: 8px; border-radius: 50%; margin-right: 6px; }
    .lb-card { background: #f8fafc; padding: 15px; border-radius: 10px; border: 1px solid #cbd5e1; text-align: center; }
    .total-pts { color: #e11d48; font-size: 1.8rem; font-weight: 800; display: block; }
</style>
""", unsafe_allow_html=True)

# --- 3. DATA ENGINE ---
DB_FILE = 'tournament_db.json'
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f: return json.load(f)
    return {"selections": {}, "scores": {}, "pools": {}, "player_master": {}}

db = load_db()

# --- 4. SIDEBAR SCHEDULE ---
st.sidebar.title("🗓️ Schedule")
sel_week = st.sidebar.selectbox("Active Week", list(SEASON_WEEKS.keys()))
current_matches = SEASON_WEEKS[sel_week]

for mid, m_text in current_matches.items():
    st.sidebar.markdown(f"**{mid}:** {m_text}")

# --- 5. MAIN APP ---
st.title("🏆 Inner Circle IPL 2026")
t1, t2, t3 = st.tabs(["🏏 SQUAD SELECTION", "📊 STANDINGS", "🛡️ ADMIN"])

# --- TAB 1: SQUAD SELECTION (MATRIX MODE) ---
with t1:
    st.markdown('<div class="rule-box"><b>Rules:</b> 11 Players | Max 4 Overseas (✈️) | 1 Captain (2x Pts)</div>', unsafe_allow_html=True)
    
    user = st.selectbox("Select Manager", list(db["pools"].keys()))
    pool = db["pools"].get(user, [])
    saved = db["selections"].get(sel_week, {}).get(user, {"squad": [], "cap": ""})
    
    # Selection Matrix
    selected, os_count = [], 0
    cols = st.columns(5) # 5-Column Matrix for zero scrolling
    
    for idx, p in enumerate(pool):
        p_info = db["player_master"].get(p, {'team': 'IPL', 'role': 'BAT', 'is_overseas': False})
        color = TEAM_COLORS.get(p_info['team'], '#ccc')
        os_icon = "✈️" if p_info['is_overseas'] else ""
        
        with cols[idx % 5]:
            # Matrix Cell: Info and Checkbox on one line
            c_info, c_check = st.columns([4, 1])
            with c_info:
                st.markdown(f'<div class="matrix-cell"><span class="jersey-dot" style="background:{color}"></span><span style="font-size:12px; overflow:hidden; white-space:nowrap;">{p} {os_icon}</span></div>', unsafe_allow_html=True)
            with c_check:
                if st.checkbox("", key=f"m_{user}_{p}", value=(p in saved["squad"]), label_visibility="collapsed"):
                    selected.append(p)
                    if p_info['is_overseas']: os_count += 1

    st.divider()
    
    # Status & Action Bar
    if len(selected) > 0:
        st.subheader("🚀 Finalize Your Squad")
        stat_col1, stat_col2, act_col = st.columns([1, 1, 2])
        
        stat_col1.metric("Squad", f"{len(selected)}/11")
        stat_col2.metric("Overseas", f"{os_count}/4")
        
        with act_col:
            if len(selected) == 11:
                if os_count <= 4:
                    cap = st.selectbox("🛡️ Choose Captain", selected, index=selected.index(saved["cap"]) if saved["cap"] in selected else 0)
                    if st.button("✅ LOCK & SUBMIT SQUAD", use_container_width=True, type="primary"):
                        if sel_week not in db["selections"]: db["selections"][sel_week] = {}
                        db["selections"][sel_week][user] = {"squad": selected, "cap": cap}
                        # save_db(db) # Call your save function here
                        st.success(f"Squad for {sel_week} submitted successfully!")
                else:
                    st.error("Too many Overseas players (Max 4)!")
            else:
                st.warning(f"Pick {11 - len(selected)} more players to enable submission.")

# --- TAB 2: STANDINGS (REVERTED TO BEST VERSION) ---
with t2:
    st.subheader("📊 Leaderboard")
    lb_data = []
    
    # Calculate for all managers
    managers = list(db["pools"].keys())
    lb_cols = st.columns(len(managers))
    
    for i, m in enumerate(managers):
        w_pts, t_pts = 0, 0
        # Total Season Logic
        for wk, matches in SEASON_WEEKS.items():
            sel = db["selections"].get(wk, {}).get(m, {"squad": [], "cap": ""})
            week_total = 0
            for p in sel["squad"]:
                p_sc = db["scores"].get(p, {})
                pts = sum([v for k, v in p_sc.items() if k in matches])
                week_total += (pts * 2) if p == sel["cap"] else pts
            
            t_pts += week_total
            if wk == sel_week: w_pts = week_total
            
        lb_data.append({"Manager": m, "Weekly": w_pts, "Total": t_pts})
        
        with lb_cols[i]:
            st.markdown(f"""
                <div class="lb-card">
                    <b style="font-size:1.2rem;">{m}</b><br>
                    <small>Week Pts: {w_pts}</small>
                    <span class="total-pts">{t_pts}</span>
                </div>
            """, unsafe_allow_html=True)

    st.divider()
    st.subheader("Full Season Breakdown")
    st.dataframe(pd.DataFrame(lb_data).sort_values("Total", ascending=False), use_container_width=True)

# --- TAB 3: ADMIN (REMAINS SMART MATCH-BASED) ---
with t3:
    st.subheader("🛡️ Scoring Console")
    all_match_ids = [mid for w in SEASON_WEEKS.values() for mid in w.keys()]
    sel_mid = st.selectbox("Select Match ID to Score", all_match_ids)
    
    # Match context
    m_context = "Unknown Match"
    for w in SEASON_WEEKS.values():
        if sel_mid in w: m_context = w[sel_mid]
    
    st.info(f"Inputting Scores for **{sel_mid}: {m_context}**")
    # ... (Smart filtering logic from previous version follows)
    
