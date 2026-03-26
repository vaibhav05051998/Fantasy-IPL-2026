import streamlit as st
import pandas as pd
import json
import os

# --- 1. CONFIG & CALENDAR ---
TEAM_COLORS = {'RCB': '#d11d26', 'MI': '#004ba0', 'CSK': '#fdb913', 'SRH': '#f26522', 'RR': '#ea1a85', 'KKR': '#3a225d', 'GT': '#1b2133', 'LSG': '#0057e2', 'DC': '#0078bc', 'PBKS': '#dd1f2d', 'IPL': '#000080'}
ROLE_EMOJI = {'BAT': '🏏 Batter', 'BOWL': '⚾ Bowler', 'WK': '🧤 Keeper'}

SEASON_WEEKS = {
    "Week 1 (Mar 28 - Apr 03)": {"M01": "RCB vs SRH", "M02": "MI vs KKR", "M03": "RR vs CSK", "M04": "PBKS vs GT", "M05": "LSG vs DC", "M06": "KKR vs SRH", "M07": "CSK vs PBKS"},
    "Week 2 (Apr 04 - Apr 10)": {"M08": "DC vs MI", "M09": "GT vs RR", "M10": "SRH vs LSG", "M11": "RCB vs CSK", "M12": "KKR vs PBKS", "M13": "RR vs MI", "M14": "DC vs GT"},
    "Playoffs": {"SF1": "Qualifier 1", "SF2": "Eliminator", "SF3": "Qualifier 2", "FIN": "Grand Final"}
}

# --- 2. DATABASE ENGINE ---
DB_FILE = 'tournament_db.json'
def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f: return json.load(f)
        except: pass
    # INITIAL PREFILL DATA BASED ON YOUR SQUAD HISTORY
    return {
        "selections": {}, "scores": {}, 
        "pools": {"Kazim": [], "Adi": [], "Aatish": [], "Shrijeet": [], "Nagle": []}, 
        "player_master": {
            "Virat Kohli": {"team": "RCB", "role": "BAT", "is_overseas": False},
            "MS Dhoni": {"team": "CSK", "role": "WK", "is_overseas": False},
            "Pat Cummins": {"team": "SRH", "role": "BOWL", "is_overseas": True},
            # Add other known players here...
        }
    }

def save_db(data):
    with open(DB_FILE, 'w') as f: json.dump(data, f)

db = load_db()

# --- 3. UI STYLING ---
st.set_page_config(page_title="Inner Circle IPL", layout="centered")
st.markdown("""
<style>
    .mobile-matrix { border: 1px solid #e2e8f0; padding: 6px; border-radius: 6px; background: #fff; display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px; height: 42px; }
    .jersey-dot { height: 8px; width: 8px; border-radius: 50%; margin-right: 5px; }
    .role-text { font-size: 10px; color: #64748b; }
    .lb-card { background: #f8fafc; padding: 10px; border-radius: 8px; border: 1px solid #cbd5e1; text-align: center; margin-bottom: 10px; }
    .total-pts { color: #e11d48; font-size: 1.5rem; font-weight: 800; display: block; }
</style>
""", unsafe_allow_html=True)

# --- 4. SIDEBAR ---
st.sidebar.title("🗓️ Season Logic")
active_week = st.sidebar.selectbox("Active Week", list(SEASON_WEEKS.keys()))
week_matches = SEASON_WEEKS[active_week]
team_counts = {}
for m_text in week_matches.values():
    for t in m_text.split(" vs "): team_counts[t] = team_counts.get(t, 0) + 1
st.sidebar.markdown("### Team Matches")
for t, c in sorted(team_counts.items()): st.sidebar.write(f"**{t}:** {c}")

# --- 5. TABS ---
t1, t2, t3 = st.tabs(["🏏 SQUAD", "📊 STANDINGS", "🛡️ ADMIN"])

# --- TAB 1: SQUAD (MATRIX + ROLE) ---
with t1:
    user = st.selectbox("Manager", list(db["pools"].keys()))
    pool = db["pools"].get(user, [])
    saved = db["selections"].get(active_week, {}).get(user, {"squad": [], "cap": ""})
    
    selected, os_count = [], 0
    cols = st.columns(2)
    for idx, p in enumerate(pool):
        info = db["player_master"].get(p, {"team": "IPL", "role": "BAT", "is_overseas": False})
        with cols[idx % 2]:
            c1, c2 = st.columns([4, 1])
            with c1:
                st.markdown(f'''<div class="mobile-matrix">
                    <span class="jersey-dot" style="background:{TEAM_COLORS.get(info["team"], "#ccc")}"></span>
                    <div style="flex-grow:1; line-height:1;">
                        <span style="font-size:12px;">{p} {"✈️" if info["is_overseas"] else ""}</span><br>
                        <span class="role-text">{ROLE_EMOJI.get(info["role"], "BAT")}</span>
                    </div>
                </div>''', unsafe_allow_html=True)
            with c2:
                if st.checkbox("", key=f"sel_{user}_{p}", value=(p in saved["squad"]), label_visibility="collapsed"):
                    selected.append(p)
                    if info["is_overseas"]: os_count += 1
    
    if len(selected) == 11 and os_count <= 4:
        cap = st.selectbox("🛡️ Captain", selected, index=selected.index(saved["cap"]) if saved["cap"] in selected else 0)
        if st.button("🚀 SUBMIT SQUAD", use_container_width=True, type="primary"):
            if active_week not in db["selections"]: db["selections"][active_week] = {}
            db["selections"][active_week][user] = {"squad": selected, "cap": cap}
            save_db(db)
            st.success("Locked!")

# --- TAB 2: STANDINGS (SAME AS BEFORE) ---
with t2:
    st.subheader("📊 Leaderboard")
    # ... (Previous Standings logic remains identical)

# --- TAB 3: ADMIN (REFINED EDITING) ---
with t3:
    adm_t1, adm_t2, adm_t3 = st.tabs(["📝 SCORING", "👥 POOLS", "🛠️ PLAYER MASTER"])

    # ADMIN: POOLS (Kazim, Adi, etc)
    with adm_t2:
        m_edit = st.selectbox("Edit Manager Pool", list(db["pools"].keys()))
        current_list = db["pools"][m_edit]
        
        # Multiselect for prefilled editing
        updated_pool = st.multiselect(f"Manage {m_edit}'s Squad", options=list(db["player_master"].keys()), default=current_list)
        if st.button(f"Save {m_edit} Squad"):
            db["pools"][m_edit] = updated_pool
            save_db(db)
            st.toast("Squad updated!")

    # ADMIN: PLAYER ATTRIBUTES
    with adm_t3:
        st.write("### Edit Player Master Data")
        p_name = st.selectbox("Select Player to Edit", ["Add New"] + sorted(list(db["player_master"].keys())))
        
        if p_name == "Add New":
            p_name = st.text_input("Player Name")
            
        col_a, col_b, col_c = st.columns(3)
        p_team = col_a.selectbox("Team", list(TEAM_COLORS.keys()), key="p_team")
        p_role = col_b.selectbox("Role", ["BAT", "BOWL", "WK"], key="p_role")
        p_os = col_c.checkbox("Overseas?", key="p_os")
        
        if st.button("Save Player to Master List"):
            db["player_master"][p_name] = {"team": p_team, "role": p_role, "is_overseas": p_os}
            save_db(db)
            st.success(f"{p_name} saved!")
