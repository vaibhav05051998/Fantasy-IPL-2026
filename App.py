# VERSION: ver01_260326_ULTRA_V5
# STATUS: V3 UI + 7PM Sat Lock + Auto-Carryover Scoring + Fixed Datetime

import streamlit as st
import pandas as pd
import json
import os
from collections import Counter
from datetime import datetime

# --- 1. CONFIGURATION & DATA ---
DB_FILE = 'tournament_db.json'
TEAM_COLORS = {
    'RCB': '#d11d26', 'MI': '#004ba0', 'CSK': '#fdb913', 'SRH': '#f26522',
    'RR': '#ea1a85', 'KKR': '#3a225d', 'GT': '#1b2133', 'LSG': '#0057e2',
    'DC': '#0078bc', 'PBKS': '#dd1f2d', 'IPL': '#000080'
}
ROLE_EMOJI = {'BAT': '🏏', 'BOWL': '⚾', 'WK': '🧤'}

# CORRECTED SAT-FRI SCHEDULE WITH LOCK DATES
SEASON_WEEKS = {
    "Week 1 (Mar 28 - Apr 03)": {"lock": "2026-03-28 19:00:00", "matches": {"M01": "RCB vs SRH", "M02": "MI vs KKR", "M03": "RR vs CSK", "M04": "PBKS vs GT", "M05": "LSG vs DC", "M06": "KKR vs SRH", "M07": "CSK vs PBKS"}},
    "Week 2 (Apr 04 - Apr 10)": {"lock": "2026-04-04 19:00:00", "matches": {"M08": "DC vs MI", "M09": "GT vs RR", "M10": "SRH vs LSG", "M11": "RCB vs CSK", "M12": "KKR vs PBKS", "M13": "RR vs MI", "M14": "DC vs GT"}},
    "Week 3 (Apr 11 - Apr 17)": {"lock": "2026-04-11 19:00:00", "matches": {"M15": "SRH vs RCB", "M16": "KKR vs MI", "M17": "CSK vs RR", "M18": "GT vs PBKS", "M19": "DC vs LSG", "M20": "SRH vs KKR", "M21": "PBKS vs CSK"}},
    "Week 4 (Apr 18 - Apr 24)": {"lock": "2026-04-18 19:00:00", "matches": {"M22": "MI vs DC", "M23": "RR vs GT", "M24": "LSG vs SRH", "M25": "CSK vs RCB", "M26": "PBKS vs KKR", "M27": "MI vs RR", "M28": "GT vs DC"}},
    "Week 5 (Apr 25 - May 01)": {"lock": "2026-04-25 19:00:00", "matches": {"M29": "LSG vs KKR", "M30": "RCB vs GT", "M31": "SRH vs RR", "M32": "DC vs CSK", "M33": "MI vs PBKS", "M34": "KKR vs RCB", "M35": "RR vs LSG"}},
    "Week 6 (May 02 - May 08)": {"lock": "2026-05-02 19:00:00", "matches": {"M36": "GT vs SRH", "M37": "CSK vs MI", "M38": "PBKS vs DC", "M39": "RCB vs LSG", "M40": "RR vs KKR", "M41": "SRH vs PBKS", "M42": "GT vs CSK"}},
    "Week 7 (May 09 - May 15)": {"lock": "2026-05-09 19:00:00", "matches": {"M43": "DC vs RCB", "M44": "LSG vs MI", "M45": "KKR vs GT", "M46": "CSK vs SRH", "M47": "PBKS vs RR", "M48": "MI vs LSG", "M49": "RCB vs DC"}},
    "Week 8 (May 16 - May 22)": {"lock": "2026-05-16 19:00:00", "matches": {"M50": "GT vs KKR", "M51": "SRH vs CSK", "M52": "RR vs PBKS", "M53": "DC vs RR", "M54": "KKR vs PBKS", "M55": "LSG vs GT", "M56": "MI vs RCB"}},
}

def load_db():
    pm = {
        "Rajat Patidar": {"team": "RCB", "role": "BAT", "is_overseas": False}, "Devdutt Padikkal": {"team": "LSG", "role": "BAT", "is_overseas": False},
        "Shimron Hetmyer": {"team": "RR", "role": "BAT", "is_overseas": True}, "Dhruv Jurel": {"team": "RR", "role": "WK", "is_overseas": False},
        "Vaibhav Suryavanshi": {"team": "RR", "role": "BAT", "is_overseas": False}, "Priyansh Arya": {"team": "PBKS", "role": "BAT", "is_overseas": False},
        "Ryan Rickelton": {"team": "MI", "role": "WK", "is_overseas": True}, "Aiden Markram": {"team": "SRH", "role": "BAT", "is_overseas": True},
        "Angkrish Raghuvanshi": {"team": "KKR", "role": "BAT", "is_overseas": False}, "Jos Buttler": {"team": "SRH", "role": "WK", "is_overseas": True},
        "David Miller": {"team": "GT", "role": "BAT", "is_overseas": True}, "Ben Duckett": {"team": "LSG", "role": "WK", "is_overseas": True},
        "Nitish Rana": {"team": "KKR", "role": "BAT", "is_overseas": False}, "Prashant Veer": {"team": "SRH", "role": "BOWL", "is_overseas": False},
        "Anshul Kambhoj": {"team": "MI", "role": "BOWL", "is_overseas": False}, "Axar Patel": {"team": "DC", "role": "BOWL", "is_overseas": False},
        "Gudakesh Motie": {"team": "GT", "role": "BOWL", "is_overseas": True}, "Will Jacks": {"team": "RCB", "role": "BAT", "is_overseas": True},
        "Marcus Stoinis": {"team": "LSG", "role": "BAT", "is_overseas": True}, "Shashank Singh": {"team": "PBKS", "role": "BAT", "is_overseas": False},
        "Nitish Kumar Reddy": {"team": "SRH", "role": "BAT", "is_overseas": False}, "Pat Cummins": {"team": "SRH", "role": "BOWL", "is_overseas": True},
        "Jacob Duffy": {"team": "RCB", "role": "BOWL", "is_overseas": True}, "Josh Hazlewood": {"team": "RCB", "role": "BOWL", "is_overseas": True},
        "Ravi Bishnoi": {"team": "LSG", "role": "BOWL", "is_overseas": False}, "Avesh Khan": {"team": "RR", "role": "BOWL", "is_overseas": False},
        "Ravi Sai Kishore": {"team": "GT", "role": "BOWL", "is_overseas": False}, "Noor Ahmad": {"team": "GT", "role": "BOWL", "is_overseas": True},
        "Blessing Muzarabani": {"team": "PBKS", "role": "BOWL", "is_overseas": True}, "Lockie Ferguson": {"team": "RCB", "role": "BOWL", "is_overseas": True},
        "Phil Salt": {"team": "KKR", "role": "WK", "is_overseas": True}, "Yashasvi Jaiswal": {"team": "RR", "role": "BAT", "is_overseas": False},
        "Prabhsimran Singh": {"team": "PBKS", "role": "WK", "is_overseas": False}, "Nicholas Pooran": {"team": "LSG", "role": "WK", "is_overseas": True},
        "Tim Seifert": {"team": "DC", "role": "WK", "is_overseas": True}, "Shubman Gill": {"team": "GT", "role": "BAT", "is_overseas": False},
        "Ayush Mhatre": {"team": "MI", "role": "BAT", "is_overseas": False}, "Ashutosh Sharma": {"team": "PBKS", "role": "BAT", "is_overseas": False},
        "Rahul Tewatia": {"team": "GT", "role": "BAT", "is_overseas": False}, "Washington Sundar": {"team": "SRH", "role": "BOWL", "is_overseas": False},
        "Cooper Connolly": {"team": "MI", "role": "BAT", "is_overseas": True}, "Azmatullah Omarzai": {"team": "GT", "role": "BOWL", "is_overseas": True},
        "Ravindra Jadeja": {"team": "CSK", "role": "BOWL", "is_overseas": False}, "Abhishek Sharma": {"team": "SRH", "role": "BAT", "is_overseas": False},
        "Harshal Patel": {"team": "PBKS", "role": "BOWL", "is_overseas": False}, "Jofra Archer": {"team": "RR", "role": "BOWL", "is_overseas": True},
        "Yuzvendra Chahal": {"team": "PBKS", "role": "BOWL", "is_overseas": False}, "AM Ghazanfar": {"team": "MI", "role": "BOWL", "is_overseas": True},
        "Digvesh Singh": {"team": "MI", "role": "BOWL", "is_overseas": False}, "Prasidh Krishna": {"team": "GT", "role": "BOWL", "is_overseas": False},
        "Umran Malik": {"team": "SRH", "role": "BOWL", "is_overseas": False}, "Vipraj Nigam": {"team": "RR", "role": "BOWL", "is_overseas": False},
        "Tim David": {"team": "MI", "role": "BAT", "is_overseas": True}, "Jitesh Sharma": {"team": "PBKS", "role": "WK", "is_overseas": False},
        "Nehal Wadhera": {"team": "MI", "role": "BAT", "is_overseas": False}, "Quinton de Kock": {"team": "LSG", "role": "WK", "is_overseas": True},
        "Sherfane Rutherford": {"team": "KKR", "role": "BAT", "is_overseas": True}, "Rohit Sharma": {"team": "MI", "role": "BAT", "is_overseas": False},
        "Rishabh Pant": {"team": "LSG", "role": "WK", "is_overseas": False}, "Abdul Samad": {"team": "SRH", "role": "BAT", "is_overseas": False},
        "Matthew Breetzke": {"team": "LSG", "role": "BAT", "is_overseas": True}, "Rahul Tripathi": {"team": "SRH", "role": "BAT", "is_overseas": False},
        "Finn Allen": {"team": "RCB", "role": "WK", "is_overseas": True}, "Shahrukh Khan": {"team": "GT", "role": "BAT", "is_overseas": False},
        "Tristan Stubbs": {"team": "DC", "role": "WK", "is_overseas": True}, "Pathum Nissanka": {"team": "IPL", "role": "BAT", "is_overseas": True},
        "MS Dhoni": {"team": "CSK", "role": "WK", "is_overseas": False}, "Dewald Brevis": {"team": "MI", "role": "BAT", "is_overseas": True},
        "Shivam Dube": {"team": "CSK", "role": "BAT", "is_overseas": False}, "Rashid Khan": {"team": "GT", "role": "BOWL", "is_overseas": True},
        "Sunil Narine": {"team": "KKR", "role": "BOWL", "is_overseas": True}, "Shahbaz Ahmed": {"team": "SRH", "role": "BOWL", "is_overseas": False},
        "Hardik Pandya": {"team": "MI", "role": "BOWL", "is_overseas": False}, "Donovan Ferreira": {"team": "RR", "role": "WK", "is_overseas": True},
        "Jacob Bethell": {"team": "RCB", "role": "BAT", "is_overseas": True}, "Romario Shepherd": {"team": "MI", "role": "BOWL", "is_overseas": True},
        "Yash Dayal": {"team": "RCB", "role": "BOWL", "is_overseas": False}, "Deepak Chahar": {"team": "CSK", "role": "BOWL", "is_overseas": False},
        "Vaibhav Arora": {"team": "KKR", "role": "BOWL", "is_overseas": False}, "Mohammed Siraj": {"team": "GT", "role": "BOWL", "is_overseas": False},
        "Kuldeep Yadav": {"team": "DC", "role": "BOWL", "is_overseas": False}, "Khaleel Ahmed": {"team": "DC", "role": "BOWL", "is_overseas": False},
        "Mukesh Choudhary": {"team": "CSK", "role": "BOWL", "is_overseas": False}, "Rahul Chahar": {"team": "PBKS", "role": "BOWL", "is_overseas": False},
        "Mayank Yadav": {"team": "LSG", "role": "BOWL", "is_overseas": False}, "Harpreet Brar": {"team": "PBKS", "role": "BOWL", "is_overseas": False},
        "Tushar Deshpande": {"team": "RR", "role": "BOWL", "is_overseas": False}, "Travis Head": {"team": "SRH", "role": "BAT", "is_overseas": True},
        "Ishan Kishan": {"team": "SRH", "role": "WK", "is_overseas": False}, "Riyan Parag": {"team": "RR", "role": "BAT", "is_overseas": False},
        "Shreyas Iyer": {"team": "PBKS", "role": "BAT", "is_overseas": False}, "Ayush Badoni": {"team": "LSG", "role": "BAT", "is_overseas": False},
        "Himmat Singh": {"team": "IPL", "role": "BAT", "is_overseas": False}, "Manish Pandey": {"team": "KKR", "role": "BAT", "is_overseas": False},
        "Ajinkya Rahane": {"team": "CSK", "role": "BAT", "is_overseas": False}, "Sai Sudharsan": {"team": "GT", "role": "BAT", "is_overseas": False},
        "Prithvi Shaw": {"team": "DC", "role": "BAT", "is_overseas": False}, "Karun Nair": {"team": "IPL", "role": "BAT", "is_overseas": False},
        "Abishek Porel": {"team": "DC", "role": "WK", "is_overseas": False}, "Sarfaraz Khan": {"team": "DC", "role": "BAT", "is_overseas": False},
        "Ruturaj Gaikwad": {"team": "CSK", "role": "BAT", "is_overseas": False}, "Ramakrishna Ghosh": {"team": "IPL", "role": "BOWL", "is_overseas": False},
        "Mitchell Marsh": {"team": "DC", "role": "BAT", "is_overseas": True}, "Krunal Pandya": {"team": "RCB", "role": "BOWL", "is_overseas": False},
        "Venkatesh Iyer": {"team": "KKR", "role": "BAT", "is_overseas": False}, "Jaydev Unadkat": {"team": "SRH", "role": "BOWL", "is_overseas": False},
        "Suyash Sharma": {"team": "KKR", "role": "BOWL", "is_overseas": False}, "Sandeep Sharma": {"team": "RR", "role": "BOWL", "is_overseas": False},
        "Arshdeep Singh": {"team": "PBKS", "role": "BOWL", "is_overseas": False}, "Trent Boult": {"team": "MI", "role": "BOWL", "is_overseas": True},
        "Mohammed Shami": {"team": "SRH", "role": "BOWL", "is_overseas": False}, "Kagiso Rabada": {"team": "GT", "role": "BOWL", "is_overseas": True},
        "Mitchell Santner": {"team": "CSK", "role": "BOWL", "is_overseas": True}, "Kartik Sharma": {"team": "IPL", "role": "BAT", "is_overseas": False},
        "Heinrich Klaasen": {"team": "SRH", "role": "WK", "is_overseas": True}, "Virat Kohli": {"team": "RCB", "role": "BAT", "is_overseas": False},
        "Suryakumar Yadav": {"team": "MI", "role": "BAT", "is_overseas": False}, "Rinku Singh": {"team": "KKR", "role": "BAT", "is_overseas": False},
        "KL Rahul": {"team": "DC", "role": "WK", "is_overseas": False}, "Sanju Samson": {"team": "RR", "role": "WK", "is_overseas": False},
        "Cameron Green": {"team": "RCB", "role": "BOWL", "is_overseas": True}, "Tilak Varma": {"team": "MI", "role": "BAT", "is_overseas": False},
        "Marco Jansen": {"team": "PBKS", "role": "BOWL", "is_overseas": True}, "Liam Livingstone": {"team": "RCB", "role": "BAT", "is_overseas": True},
        "Bhuvneshwar Kumar": {"team": "RCB", "role": "BOWL", "is_overseas": False}, "Jasprit Bumrah": {"team": "MI", "role": "BOWL", "is_overseas": False},
        "Varun Chakaravarthy": {"team": "KKR", "role": "BOWL", "is_overseas": False}, "Lungi Ngidi": {"team": "DC", "role": "BOWL", "is_overseas": True},
        "Jason Holder": {"team": "IPL", "role": "BOWL", "is_overseas": True}, "Mitchell Starc": {"team": "DC", "role": "BOWL", "is_overseas": True}
    }
    initial_pools = {"Kazim": list(pm.keys())[:30], "Aman": list(pm.keys())[30:52], "Aatish": list(pm.keys())[52:87], "Shrijeet": list(pm.keys())[87:114], "Nagle": list(pm.keys())[114:]}
    if not os.path.exists(DB_FILE): return {"selections": {}, "scores": {}, "pools": initial_pools, "player_master": pm}
    with open(DB_FILE, 'r') as f: return json.load(f)

def save_db(data):
    with open(DB_FILE, 'w') as f: json.dump(data, f)

st.set_page_config(page_title="Inner Circle IPL", layout="wide")

# V3 STYLING RE-IMPLEMENTED
st.markdown("""<style>
    .mobile-matrix { border: 1px solid #e2e8f0; padding: 6px; border-radius: 6px; background: #fff; display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px; height: 52px; }
    .jersey-dot { height: 10px; width: 10px; border-radius: 50%; margin-right: 8px; }
    .role-label { font-size: 10px; color: #64748b; font-weight: 700; }
    .squad-view-box { background: #f1f5f9; border-radius: 10px; padding: 10px; border: 1px solid #cbd5e1; }
    .squad-player-row { font-size: 12px; padding: 4px 0; border-bottom: 1px solid #e2e8f0; display: flex; justify-content: space-between; }
    .cap-badge { background: #1e293b; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold; }
</style>""", unsafe_allow_html=True)

db = load_db()

# --- 2. SIDEBAR LOCK LOGIC ---
st.sidebar.title("🗓️ Season Schedule")
active_week_name = st.sidebar.selectbox("Select Week", list(SEASON_WEEKS.keys()))
week_config = SEASON_WEEKS[active_week_name]
lock_time = datetime.strptime(week_config["lock"], "%Y-%m-%d %H:%M:%S")
is_locked = datetime.now() > lock_time

if is_locked: st.sidebar.error(f"🔒 Locked at {lock_time.strftime('%I:%M %p, %b %d')}")
else: st.sidebar.success(f"🔓 Closes {lock_time.strftime('%I:%M %p, %b %d')}")

# Match counts sidebar
matches_this_week = week_config["matches"]
all_teams_week = []
for f in matches_this_week.values(): all_teams_week.extend(f.split(" vs "))
team_counts = Counter(all_teams_week)
for team, count in sorted(team_counts.items()): st.sidebar.markdown(f"**{team}**: {count}")

t1, t_view, t2, t_admin = st.tabs(["🏏 MY SQUAD", "👀 ALL SQUADS", "📊 STANDINGS", "🛡️ ADMIN"])

# TAB 1: SQUAD SELECTION (V3 UI)
with t1:
    user = st.selectbox("Manager Name", list(db["pools"].keys()))
    pool = db["pools"].get(user, [])
    saved = db["selections"].get(active_week_name, {}).get(user, {"squad": [], "cap": ""})
    state_key = f"sel_{user}_{active_week_name}"
    if state_key not in st.session_state: st.session_state[state_key] = list(saved["squad"])
    
    if is_locked: st.warning("Submission period has ended. No further changes can be saved.")
    
    f1, f2 = st.columns([2, 1])
    search = f1.text_input("🔍 Search Name", key="src_v5")
    role_f = f2.selectbox("Role", ["All", "BAT", "BOWL", "WK"], key="rol_v5")
    
    cols = st.columns(2)
    display_idx = 0
    for p in sorted(pool):
        info = db["player_master"].get(p, {"team": "IPL", "role": "BAT", "is_overseas": False})
        if (search.lower() in p.lower()) and (role_f == "All" or info["role"] == role_f):
            with cols[display_idx % 2]:
                c_cell, c_box = st.columns([4, 1])
                with c_cell: st.markdown(f'<div class="mobile-matrix"><span class="jersey-dot" style="background:{TEAM_COLORS.get(info["team"], "#ccc")}"></span><div style="flex-grow:1; line-height:1.1;"><span style="font-size:11px; font-weight:600;">{p} {"✈️" if info["is_overseas"] else ""}</span><br><span class="role-label">{ROLE_EMOJI.get(info["role"], "BAT")}</span></div></div>', unsafe_allow_html=True)
                with c_box:
                    checked = st.checkbox("", key=f"cb_{user}_{p}", value=(p in st.session_state[state_key]), disabled=is_locked)
                    if not is_locked:
                        if checked and p not in st.session_state[state_key]: st.session_state[state_key].append(p); st.rerun()
                        elif not checked and p in st.session_state[state_key]: st.session_state[state_key].remove(p); st.rerun()
            display_idx += 1
            
    st.divider()
    final_squad = st.session_state[state_key]
    os_count = sum(1 for p in final_squad if db["player_master"].get(p, {}).get("is_overseas"))
    wk_count = sum(1 for p in final_squad if db["player_master"].get(p, {}).get("role") == "WK")
    st.write(f"**Squad:** {len(final_squad)}/11 | **Overseas:** {os_count}/4 | **Keepers:** {wk_count}")
    
    if len(final_squad) == 11 and os_count <= 4 and wk_count >= 1:
        cap = st.selectbox("🛡️ Select Captain", final_squad, index=(final_squad.index(saved["cap"]) if saved["cap"] in final_squad else 0), disabled=is_locked)
        if not is_locked:
            if st.button("🚀 SAVE SQUAD", type="primary", use_container_width=True):
                if active_week_name not in db["selections"]: db["selections"][active_week_name] = {}
                db["selections"][active_week_name][user] = {"squad": final_squad, "cap": cap}
                save_db(db); st.success("Squad Locked!")
    else: st.warning("⚠️ Rules: Exactly 11 Players, Max 4 Overseas, Min 1 Keeper.")

# TAB 2: STANDINGS (METRICS + AUTO-CARRYOVER TABLE)
with t2:
    lb_data = []
    week_keys = list(SEASON_WEEKS.keys())
    
    for m in db["pools"].keys():
        total, week_pts, prev_total = 0, 0, 0
        for idx, wk_key in enumerate(week_keys):
            sel = db["selections"].get(wk_key, {}).get(m, None)
            
            # CARRYOVER LOGIC
            if not sel:
                for prev_wk in reversed(week_keys[:idx]):
                    lookback = db["selections"].get(prev_wk, {}).get(m, None)
                    if lookback: sel = lookback; break
            
            w_sum = 0
            if sel:
                for p in sel["squad"]:
                    p_pts = 0
                    for mid, fixture in SEASON_WEEKS[wk_key]["matches"].items():
                        s = db["scores"].get(p, {}).get(mid, {"r":0, "w":0, "c":0, "s":0})
                        p_pts += (s.get("r",0)*1) + (s.get("w",0)*20) + (s.get("c",0)*5) + (s.get("s",0)*5)
                    if p == sel["cap"]: p_pts *= 2
                    w_sum += p_pts
            
            total += w_sum
            if wk_key == active_week_name: week_pts = w_sum
            if idx < week_keys.index(active_week_name): prev_total += w_sum
            
        lb_data.append({"Manager": m, "Weekly": week_pts, "Total": total, "Prev": prev_total})

    curr_rank = sorted(lb_data, key=lambda x: x['Total'], reverse=True)
    st.subheader("📊 Leaderboard")
    cols = st.columns(2)
    for i, row in enumerate(curr_rank):
        with cols[i % 2]: st.metric(f"#{i+1} {row['Manager']}", f"{row['Total']} pts", f"{row['Weekly']} this week")
    
    st.divider()
    st.subheader("📝 Detailed Standings")
    df_lb = pd.DataFrame(curr_rank).drop(columns=['Prev'])
    st.table(df_lb)

# TAB 3: SQUAD VIEW (V3 BOX STYLE)
with t_view:
    manager_list = list(db["pools"].keys())
    cols = st.columns(len(manager_list))
    for i, mgr in enumerate(manager_list):
        with cols[i]:
            st.markdown(f"#### {mgr}")
            s_data = db["selections"].get(active_week_name, {}).get(mgr, None)
            if not s_data: st.error("No Selection")
            else:
                st.markdown('<div class="squad-view-box">', unsafe_allow_html=True)
                for player in sorted(s_data["squad"]):
                    p_info = db["player_master"].get(player, {"team": "IPL", "role": "BAT", "is_overseas": False})
                    cap_tag = '<span class="cap-badge">C</span>' if player == s_data["cap"] else ""
                    st.markdown(f'<div class="squad-player-row"><span>{ROLE_EMOJI.get(p_info["role"], "")} {player}</span>{cap_tag}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

# TAB 4: ADMIN (SCORING)
with t_admin:
    st.subheader("🛡️ Score Management")
    sel_mid = st.selectbox("Match to Score", list(matches_this_week.keys()))
    teams = matches_this_week[sel_mid].split(" vs ")
    all_p = set()
    for wk in db["selections"].values():
        for m_sel in wk.values(): all_p.update(m_sel["squad"])
    eligible = [p for p in all_p if db["player_master"].get(p, {}).get("team") in teams]
    for p in sorted(eligible):
        cur = db["scores"].get(p, {}).get(sel_mid, {"r":0, "w":0, "c":0, "s":0})
        cols = st.columns([2, 1, 1, 1, 1])
        cols[0].write(p)
        r = cols[1].number_input("R", 0, 200, cur["r"], key=f"r_{p}")
        w = cols[2].number_input("W", 0, 10, cur["w"], key=f"w_{p}")
        c = cols[3].number_input("C", 0, 10, cur["c"], key=f"c_{p}")
        s = cols[4].number_input("S", 0, 10, cur["s"], key=f"s_{p}")
        if {"r":r,"w":w,"c":c,"s":s} != cur:
            if p not in db["scores"]: db["scores"][p] = {}
            db["scores"][p][sel_mid] = {"r":r,"w":w,"c":c,"s":s}; save_db(db)
