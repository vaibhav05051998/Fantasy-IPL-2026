import streamlit as st
import pandas as pd
import json
import os

# --- 1. CONFIGURATION & FULL SEASON CALENDAR ---
TEAM_COLORS = {
    'RCB': '#d11d26', 'MI': '#004ba0', 'CSK': '#fdb913', 'SRH': '#f26522',
    'RR': '#ea1a85', 'KKR': '#3a225d', 'GT': '#1b2133', 'LSG': '#0057e2',
    'DC': '#0078bc', 'PBKS': '#dd1f2d', 'IPL': '#000080'
}

ROLE_EMOJI = {'BAT': '🏏 BAT', 'BOWL': '⚾ BOWL', 'WK': '🧤 WK'}

# FULL SEASON FIXTURES (8 Weeks + Playoffs)
SEASON_WEEKS = {
    "Week 1 (Mar 28 - Apr 03)": {"M01": "RCB vs SRH", "M02": "MI vs KKR", "M03": "RR vs CSK", "M04": "PBKS vs GT", "M05": "LSG vs DC", "M06": "KKR vs SRH", "M07": "CSK vs PBKS"},
    "Week 2 (Apr 04 - Apr 10)": {"M08": "DC vs MI", "M09": "GT vs RR", "M10": "SRH vs LSG", "M11": "RCB vs CSK", "M12": "KKR vs PBKS", "M13": "RR vs MI", "M14": "DC vs GT"},
    "Week 3 (Apr 11 - Apr 17)": {"M15": "SRH vs RCB", "M16": "KKR vs MI", "M17": "CSK vs RR", "M18": "GT vs PBKS", "M19": "DC vs LSG", "M20": "SRH vs KKR", "M21": "PBKS vs CSK"},
    "Week 4 (Apr 18 - Apr 24)": {"M22": "MI vs DC", "M23": "RR vs GT", "M24": "LSG vs SRH", "M25": "CSK vs RCB", "M26": "PBKS vs KKR", "M27": "MI vs RR", "M28": "GT vs DC"},
    "Week 5 (Apr 25 - May 01)": {"M29": "LSG vs KKR", "M30": "RCB vs GT", "M31": "SRH vs RR", "M32": "DC vs CSK", "M33": "MI vs PBKS", "M34": "KKR vs RCB", "M35": "RR vs LSG"},
    "Week 6 (May 02 - May 08)": {"M36": "GT vs SRH", "M37": "CSK vs MI", "M38": "PBKS vs DC", "M39": "RCB vs LSG", "M40": "RR vs KKR", "M41": "SRH vs PBKS", "M42": "GT vs CSK"},
    "Week 7 (May 09 - May 15)": {"M43": "DC vs RCB", "M44": "LSG vs MI", "M45": "KKR vs GT", "M46": "CSK vs SRH", "M47": "PBKS vs RR", "M48": "MI vs LSG", "M49": "RCB vs DC"},
    "Week 8 (May 16 - May 22)": {"M50": "GT vs KKR", "M51": "SRH vs CSK", "M52": "RR vs PBKS", "M53": "DC vs RR", "M54": "KKR vs PBKS", "M55": "LSG vs GT", "M56": "MI vs RCB"},
    "Playoffs (May 23 - May 30)": {"SF1": "Qualifier 1", "SF2": "Eliminator", "SF3": "Qualifier 2", "FIN": "Grand Final"}
}

# --- 2. DATABASE ENGINE WITH PREFILLED SQUADS ---
DB_FILE = 'tournament_db.json'

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f: return json.load(f)
    
    # Prefilled Data if no database exists
    initial_db = {
        "selections": {}, "scores": {},
        "pools": {
            "Kazim": ["Rajat Patidar", "Devdutt Padikkal", "Shimron Hetmyer", "Pat Cummins", "Jos Buttler"],
            "Adi": ["Philip Salt", "Yashasvi Jaiswal", "Nicholas Pooran", "Jasprit Bumrah", "Shubman Gill"],
            "Aatish": ["Tim David", "Quinton de Kock", "Rohit Sharma", "MS Dhoni", "Hardik Pandya"],
            "Shrijeet": ["Travis Head", "Ishan Kishan", "Shreyas Iyer", "Trent Boult", "Ruturaj Gaikwad"],
            "Nagle": ["Heinrich Klaasen", "Virat Kohli", "Suryakumar Yadav", "Mitchell Starc", "KL Rahul"]
        },
        "player_master": {
            "Virat Kohli": {"team": "RCB", "role": "BAT", "is_overseas": False},
            "Heinrich Klaasen": {"team": "SRH", "role": "WK", "is_overseas": True},
            "Jasprit Bumrah": {"team": "MI", "role": "BOWL", "is_overseas": False},
            "Pat Cummins": {"team": "SRH", "role": "BOWL", "is_overseas": True},
            "MS Dhoni": {"team": "CSK", "role": "WK", "is_overseas": False},
            "Jos Buttler": {"team": "RR", "role": "WK", "is_overseas": True},
            "Rohit Sharma": {"team": "MI", "role": "BAT", "is_overseas": False},
            "Travis Head": {"team": "SRH", "role": "BAT", "is_overseas": True}
            # (Admin can add more via the app UI)
        }
    }
    return initial_db

def save_db(data):
    with open(DB_FILE, 'w') as f: json.dump(data, f)

db = load_db()

# --- 3. MOBILE UI STYLING ---
st.set_page_config(page_title="Inner Circle IPL", layout="centered")
st.markdown("""
<style>
    .mobile-matrix { border: 1px solid #e2e8f0; padding: 6px; border-radius: 6px; background: #fff; display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px; height: 45px; }
    .jersey-dot { height: 8px; width: 8px; border-radius: 50%; margin-right: 5px; }
    .role-label { font-size: 10px; color: #64748b; font-weight: bold; }
    .lb-card { background: #f8fafc; padding: 10px; border-radius: 8px; border: 1px solid #cbd5e1; text-align: center; margin-bottom: 10px; }
    .total-pts { color: #e11d48; font-size: 1.5rem; font-weight: 800; display: block; }
</style>
""", unsafe_allow_html=True)

# --- 4. SIDEBAR SCHEDULE & COUNTS ---
st.sidebar.title("🗓️ Season Schedule")
active_week = st.sidebar.selectbox("Select Week", list(SEASON_WEEKS.keys()))
week_matches = SEASON_WEEKS[active_week]

team_counts = {}
for m_text in week_matches.values():
    teams = m_text.split(" vs ")
    for t in teams: team_counts[t] = team_counts.get(t, 0) + 1

st.sidebar.markdown("### Teams Playing This Week")
for t, count in sorted(team_counts.items()):
    st.sidebar.write(f"**{t}:** {count} {'Match' if count==1 else 'Matches'}")

st.sidebar.divider()
st.sidebar.markdown("### Week Fixtures")
for mid, fixture in week_matches.items():
    st.sidebar.info(f"**{mid}:** {fixture}")

# --- 5. MAIN TABS ---
t1, t2, t3 = st.tabs(["🏏 SQUAD", "📊 STANDINGS", "🛡️ ADMIN"])

# --- TAB 1: SQUAD SELECTION ---
with t1:
    user = st.selectbox("Select Manager", list(db["pools"].keys()))
    pool = db["pools"].get(user, [])
    saved = db["selections"].get(active_week, {}).get(user, {"squad": [], "cap": ""})
    
    selected, os_count = [], 0
    cols = st.columns(2)
    for idx, p in enumerate(pool):
        info = db["player_master"].get(p, {"team": "IPL", "role": "BAT", "is_overseas": False})
        with cols[idx % 2]:
            c_info, c_check = st.columns([4, 1])
            with c_info:
                st.markdown(f'''<div class="mobile-matrix">
                    <span class="jersey-dot" style="background:{TEAM_COLORS.get(info['team'], '#ccc')}"></span>
                    <div style="flex-grow:1; line-height:1.1;">
                        <span style="font-size:12px;">{p} {"✈️" if info['is_overseas'] else ""}</span><br>
                        <span class="role-label">{ROLE_EMOJI.get(info['role'], 'BAT')}</span>
                    </div>
                </div>''', unsafe_allow_html=True)
            with c_check:
                if st.checkbox("", key=f"sel_{user}_{p}", value=(p in saved["squad"]), label_visibility="collapsed"):
                    selected.append(p)
                    if info["is_overseas"]: os_count += 1

    st.divider()
    if len(selected) > 0:
        st.write(f"**Picked:** {len(selected)}/11 | **Overseas:** {os_count}/4")
        if len(selected) == 11 and os_count <= 4:
            cap = st.selectbox("🛡️ Captain (2x Pts)", selected, index=selected.index(saved["cap"]) if saved["cap"] in selected else 0)
            if st.button("🚀 SUBMIT SQUAD", type="primary", use_container_width=True):
                if active_week not in db["selections"]: db["selections"][active_week] = {}
                db["selections"][active_week][user] = {"squad": selected, "cap": cap}
                save_db(db)
                st.success("Squad Locked!")

# --- TAB 2: STANDINGS ---
with t2:
    st.subheader("📊 Leaderboard")
    managers = list(db["pools"].keys())
    if managers:
        lb_cols = st.columns(2)
        lb_data = []
        for i, m in enumerate(managers):
            t_pts, w_pts = 0, 0
            for wk, matches in SEASON_WEEKS.items():
                sel = db["selections"].get(wk, {}).get(m, {"squad": [], "cap": ""})
                week_total = 0
                for p in sel["squad"]:
                    p_sc = db["scores"].get(p, {})
                    pts = sum([v for k, v in p_sc.items() if k in matches])
                    week_total += (pts * 2) if p == sel["cap"] else pts
                t_pts += week_total
                if wk == active_week: w_pts = week_total
            lb_data.append({"Manager": m, "Weekly": w_pts, "Total": t_pts})
            with lb_cols[i % 2]:
                st.markdown(f'<div class="lb-card"><b>{m}</b><br><small>Week: {w_pts}</small><span class="total-pts">{t_pts}</span></div>', unsafe_allow_html=True)
        st.divider()
        st.dataframe(pd.DataFrame(lb_data).sort_values("Total", ascending=False), use_container_width=True, hide_index=True)

# --- TAB 3: ADMIN ---
with t3:
    adm_t1, adm_t2, adm_t3 = st.tabs(["📝 SCORING", "👥 POOLS", "🛠️ PLAYER MASTER"])

    with adm_t1:
        match_list = {f"{mid}: {txt}": mid for wk in SEASON_WEEKS.values() for mid, txt in wk.items()}
        sel_display = st.selectbox("Select Match to Score", list(match_list.keys()))
        sel_mid = match_list[sel_display]
        match_teams = sel_display.split(": ")[1].split(" vs ")
        eligible = [p for p, info in db["player_master"].items() if info['team'] in match_teams]
        for p in sorted(eligible):
            with st.expander(f"Score: {p}"):
                cur = db["scores"].get(p, {}).get(sel_mid, 0)
                score = st.number_input(f"Points", 0, value=int(cur), key=f"sc_{sel_mid}_{p}")
                if st.button(f"Save {p}"):
                    if p not in db["scores"]: db["scores"][p] = {}
                    db["scores"][p][sel_mid] = score
                    save_db(db)
                    st.toast(f"Saved {p}!")

    with adm_t2:
        st.write("### Edit Manager Pools")
        m_edit = st.selectbox("Select Manager", list(db["pools"].keys()))
        # DROPDOWN MULTISELECT for prefilled editing
        updated_pool = st.multiselect(f"Squad for {m_edit}", options=sorted(list(db["player_master"].keys())), default=db["pools"][m_edit])
        if st.button(f"Update {m_edit} Pool"):
            db["pools"][m_edit] = updated_pool
            save_db(db)
            st.success("Pool Updated!")

    with adm_t3:
        st.write("### Player Attributes")
        p_name = st.selectbox("Select Player", ["Add New"] + sorted(list(db["player_master"].keys())))
        if p_name == "Add New": p_name = st.text_input("Player Name")
        
        ca, cb, cc = st.columns(3)
        p_team = ca.selectbox("Team", list(TEAM_COLORS.keys()))
        p_role = cb.selectbox("Role", ["BAT", "BOWL", "WK"])
        p_os = cc.checkbox("Overseas?")
        
        if st.button("Save Player"):
            db["player_master"][p_name] = {"team": p_team, "role": p_role, "is_overseas": p_os}
            save_db(db)
            st.success(f"{p_name} saved!")
