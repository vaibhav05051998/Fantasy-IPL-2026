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

ROLE_EMOJI = {'BAT': '🏏', 'BOWL': '⚾', 'WK': '🧤'}

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

# --- 2. MOBILE-FIRST UI STYLING ---
st.set_page_config(page_title="Inner Circle IPL", layout="centered")
st.markdown("""
<style>
    .mobile-matrix { border: 1px solid #e2e8f0; padding: 6px; border-radius: 6px; background: #fff; display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px; height: 42px; }
    .jersey-dot { height: 8px; width: 8px; border-radius: 50%; margin-right: 5px; }
    .lb-card { background: #f8fafc; padding: 10px; border-radius: 8px; border: 1px solid #cbd5e1; text-align: center; margin-bottom: 10px; }
    .total-pts { color: #e11d48; font-size: 1.5rem; font-weight: 800; display: block; }
    .rule-box { background: #fffbeb; border: 1px solid #fcd34d; padding: 8px; border-radius: 6px; font-size: 12px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# --- 3. DATABASE ENGINE ---
DB_FILE = 'tournament_db.json'
def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f: return json.load(f)
        except: pass
    return {"selections": {}, "scores": {}, "pools": {}, "player_master": {}}

def save_db(data):
    with open(DB_FILE, 'w') as f: json.dump(data, f)

db = load_db()

# --- 4. NAVIGATION ---
st.title("🏆 Inner Circle IPL 2026")
active_week = st.sidebar.selectbox("Active Week", list(SEASON_WEEKS.keys()))
t1, t2, t3 = st.tabs(["🏏 SQUAD", "📊 STANDINGS", "🛡️ ADMIN"])

# --- TAB 1: SQUAD SELECTION (MOBILE MATRIX) ---
with t1:
    st.markdown('<div class="rule-box"><b>Rules:</b> 11 Players | Max 4 Overseas (✈️) | 1 Captain (2x Pts)</div>', unsafe_allow_html=True)
    
    managers = list(db["pools"].keys())
    if not managers:
        st.info("Setup pools in Admin first!")
    else:
        user = st.selectbox("Select Manager", managers)
        pool = db["pools"].get(user, [])
        saved = db["selections"].get(active_week, {}).get(user, {"squad": [], "cap": ""})
        
        selected, os_count = [], 0
        cols = st.columns(2) # Mobile Grid
        
        for idx, p in enumerate(pool):
            p_info = db["player_master"].get(p, {'team': 'IPL', 'role': 'BAT', 'is_overseas': False})
            color = TEAM_COLORS.get(p_info['team'], '#ccc')
            os_icon = "✈️" if p_info['is_overseas'] else ""
            
            with cols[idx % 2]:
                c_info, c_check = st.columns([4, 1])
                with c_info:
                    st.markdown(f'<div class="mobile-matrix"><span class="jersey-dot" style="background:{color}"></span><span style="font-size:12px;">{p} {os_icon}</span></div>', unsafe_allow_html=True)
                with c_check:
                    if st.checkbox("", key=f"m_{user}_{p}", value=(p in saved["squad"]), label_visibility="collapsed"):
                        selected.append(p)
                        if p_info['is_overseas']: os_count += 1

        st.divider()
        if len(selected) > 0:
            st.write(f"**Picked:** {len(selected)}/11 | **Overseas:** {os_count}/4")
            if len(selected) == 11 and os_count <= 4:
                cap = st.selectbox("🛡️ Select Captain", selected, index=selected.index(saved["cap"]) if saved["cap"] in selected else 0)
                if st.button("🚀 SUBMIT SQUAD", type="primary", use_container_width=True):
                    if active_week not in db["selections"]: db["selections"][active_week] = {}
                    db["selections"][active_week][user] = {"squad": selected, "cap": cap}
                    save_db(db)
                    st.success("Squad Locked!")
            elif os_count > 4: st.error("Too many Overseas (Max 4)!")

# --- TAB 2: STANDINGS (THE FIXED SECTION) ---
with t2:
    st.subheader("📊 Leaderboard")
    managers = list(db["pools"].keys())
    if not managers:
        st.info("No managers registered yet.")
    else:
        lb_data = []
        num_cols = min(len(managers), 2)
        lb_cols = st.columns(num_cols)
        
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
            with lb_cols[i % num_cols]:
                st.markdown(f'<div class="lb-card"><b>{m}</b><br><small>Week: {w_pts}</small><span class="total-pts">{t_pts}</span></div>', unsafe_allow_html=True)
        
        st.divider()
        st.dataframe(pd.DataFrame(lb_data).sort_values("Total", ascending=False), use_container_width=True, hide_index=True)

# --- TAB 3: ADMIN ---
with t3:
    st.subheader("🛡️ Admin Panel")
    
    st.write("### 🏏 Input Match Scores")
    match_list = {f"{mid}: {txt}": mid for wk in SEASON_WEEKS.values() for mid, txt in wk.items()}
    sel_display = st.selectbox("Select Match ID & Teams", list(match_list.keys()))
    sel_mid = match_list[sel_display]
    
    match_teams = sel_display.split(": ")[1].split(" vs ")
    eligible = [p for p, info in db["player_master"].items() if info['team'] in match_teams]
    
    if not eligible: st.info("No players found for these teams.")
    else:
        for p in sorted(eligible):
            with st.expander(f"Score: {p} ({db['player_master'][p]['team']})"):
                cur = db["scores"].get(p, {}).get(sel_mid, 0)
                score = st.number_input(f"Pts", 0, value=int(cur), key=f"sc_{sel_mid}_{p}")
                if st.button(f"Save {p}"):
                    if p not in db["scores"]: db["scores"][p] = {}
                    db["scores"][p][sel_mid] = score
                    save_db(db)
                    st.toast(f"Saved {p}!")

    st.divider()
    with st.expander("⚠️ Reset Tournament Data"):
        st.warning("Deletes scores and squad picks. Pools stay.")
        confirm_text = st.text_input("Type 'DELETE' to verify")
        safety_check = st.checkbox("Confirm wipe")
        
        if st.button("🔥 CLEAR ALL DATA"):
            if confirm_text == "DELETE" and safety_check:
                db["selections"], db["scores"] = {}, {}
                save_db(db)
                st.error("Data Wiped!")
                st.rerun()
        
