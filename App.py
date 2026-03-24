import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# --- 1. GLOBAL DATA ---
TEAM_STYLING = {
    'RCB': '#d11d26', 'MI': '#004ba0', 'CSK': '#fdb913', 'SRH': '#f26522',
    'RR': '#ea1a85', 'KKR': '#3a225d', 'GT': '#1b2133', 'LSG': '#0057e2',
    'DC': '#0078bc', 'PBKS': '#dd1f2d'
}

# Sat-Fri Cycle
SEASON_WEEKS = {
    "Week 1 (Mar 28 - Apr 03)": [
        "Match 01: RCB vs SRH (Sat)", "Match 02: MI vs KKR (Sun)", 
        "Match 03: RR vs CSK (Mon)", "Match 04: PBKS vs GT (Tue)",
        "Match 05: LSG vs DC (Wed)", "Match 06: KKR vs SRH (Thu)",
        "Match 07: CSK vs PBKS (Fri)"
    ],
    "Week 2 (Apr 04 - Apr 10)": [
        "Match 08: DC vs MI (Sat)", "Match 09: GT vs RR (Sat)", 
        "Match 10: SRH vs LSG (Sun)", "Match 11: RCB vs CSK (Mon)",
        "Match 12: KKR vs PBKS (Tue)", "Match 13: RR vs MI (Wed)",
        "Match 14: DC vs GT (Thu)", "Match 15: KKR vs LSG (Fri)"
    ]
}

MEMBER_POOLS = {
    'Kazim': ['Rajat Patidar', 'Devdutt Padikkal', 'Shimron Hetmyer', 'Dhruv Jurel', 'Vaibhav Suryavanshi', 'Priyansh Arya', 'Ryan Rickelton', 'Aiden Markram', 'Angkrish Raghuvanshi', 'Shahrukh Khan', 'Nitish Rana', 'Prashant Veer', 'Anshul Kambhoj', 'Axar Patel', 'Gudakesh Motie', 'Will Jacks', 'Marcus Stoinis', 'Shashank Singh', 'Nitish Kumar Reddy', 'Pat Cummins', 'Jacob Duffy', 'Josh Hazlewood'],
    'Adi': ['Philip Salt', 'Yashasvi Jaiswal', 'Prabhsimran Singh', 'Nicholas Pooran', 'Tim Seifert', 'Shubman Gill', 'Ayush Mhatre', 'Ashutosh Sharma', 'Rahul Tewatia', 'Jasprit Bumrah', 'Ravindra Jadeja', 'Abhishek Sharma', 'Harshal Patel', 'Jofra Archer', 'Yuzvendra Chahal', 'Allah Ghazanfar', 'Digvesh Rathi', 'Prasidh Krishna', 'Umran Malik', 'Vipraj Nigam'],
    'Aatish': ['Tim David', 'Jitesh Sharma', 'Nehal Wadhera', 'Quinton de Kock', 'Sherfane Rutherford', 'Rohit Sharma', 'Rishabh Pant', 'Abdul Samad', 'Matthew Breetzke', 'Abishek Porel', 'Tristan Stubbs', 'Pathum Nissanka', 'MS Dhoni', 'Dewald Brevis', 'Shivam Dube', 'Rashid Khan', 'Sunil Narine', 'Shahbaz Ahmed', 'Hardik Pandya', 'Donovan Ferreira', 'Jacob Bethell'],
    'Shreejith': ['Travis Head', 'Ishan Kishan', 'Riyan Parag', 'Shreyas Iyer', 'Ayush Badoni', 'Himmat Singh', 'Manish Pandey', 'Ajinkya Rahane', 'Sai Sudharsan', 'Vishnu Vinod', 'Sarfaraz Khan', 'Ruturaj Gaikwad', 'Ramakrishna Ghosh', 'Mitchell Marsh', 'Krunal Pandya', 'Venkatesh Iyer', 'Jaydev Unadkat', 'Suyash Sharma', 'Sandeep Sharma', 'Arshdeep Singh', 'Trent Boult'],
    'Nagle': ['Heinrich Klaasen', 'Virat Kohli', 'Suryakumar Yadav', 'Rinku Singh', 'KL Rahul', 'Sanju Samson', 'Cameron Green', 'Tilak Varma', 'Marco Jansen', 'Varun Chakaravarthy', 'Lungi Ngidi', 'Jason Holder', 'Mitchell Starc', 'Josh Inglis', 'Ramandeep Singh']
}

# Auto-generate player mapping with a default fallback to avoid crashes
PLAYER_MASTER = {name: {'team': 'RCB', 'role': 'BAT'} for p_list in MEMBER_POOLS.values() for name in p_list}

DB_FILE = 'tournament_db.json'
def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f: return json.load(f)
        except: pass
    return {"selections": {}, "scores": {}, "last_updated": "Never"}

def save_db(data):
    data["last_updated"] = datetime.now().strftime("%d %b, %H:%M")
    with open(DB_FILE, 'w') as f: json.dump(data, f)

# --- 2. SIDEBAR & LOGIC ---
st.set_page_config(page_title="Inner Circle IPL", layout="wide")
db = load_db()

st.sidebar.title("📅 Season Control")
current_week = st.sidebar.selectbox("Select Week", list(SEASON_WEEKS.keys()))

match_list = SEASON_WEEKS[current_week]
team_counts = {}
for m in match_list:
    teams = m.split(":")[1].split("(")[0].split(" vs ")
    for t in teams:
        t = t.strip()
        team_counts[t] = team_counts.get(t, 0) + 1

st.sidebar.subheader("Team Match Counts")
for team, count in sorted(team_counts.items(), key=lambda x: x[1], reverse=True):
    st.sidebar.write(f"● {team}: **{count}**")

# --- 3. UI STYLE ---
st.markdown("""
<style>
    .player-card { padding: 4px; background: white; border-radius: 4px; border-left: 5px solid #ccc; margin-bottom: 2px; font-size: 0.8rem; }
    .lb-card { background: #f8fafc; padding: 12px; border-radius: 8px; border: 1px solid #e2e8f0; text-align: center; }
    .weekly-pts { color: #64748b; font-size: 0.85rem; font-weight: bold; }
    .total-pts { color: #e11d48; font-size: 1.4rem; font-weight: 800; display: block; }
</style>
""", unsafe_allow_html=True)

st.title("🏆 Inner Circle IPL 2026")
t1, t2, t3 = st.tabs(["🏏 SELECTION", "📊 STANDINGS", "🛡️ ADMIN"])

# --- TAB 1: SELECTION ---
with t1:
    st.info(f"📅 Matches: {' | '.join(match_list)}")
    user = st.selectbox("Manager", list(MEMBER_POOLS.keys()))
    pool = MEMBER_POOLS[user]
    saved = db["selections"].get(current_week, {}).get(user, {"squad": [], "cap": ""})
    
    cl, cr = st.columns([3, 1])
    with cl:
        selected = []
        grid = st.columns(3)
        for i, p in enumerate(pool):
            team = PLAYER_MASTER.get(p, {}).get('team', '?')
            color = TEAM_STYLING.get(team, '#ccc')
            with grid[i % 3]:
                st.markdown(f'<div class="player-card" style="border-left-color: {color}">{p} ({team})</div>', unsafe_allow_html=True)
                if st.checkbox("Pick", key=f"p_{user}_{p}_{current_week}", value=(p in saved["squad"])):
                    selected.append(p)
    with cr:
        st.metric("Players", f"{len(selected)}/11")
        if len(selected) == 11:
            cap = st.selectbox("Captain", selected, key=f"cap_{user}_{current_week}")
            if st.button("🚀 LOCK TEAM"):
                if current_week not in db["selections"]: db["selections"][current_week] = {}
                db["selections"][current_week][user] = {"squad": selected, "cap": cap}
                save_db(db)
                st.success("Squad Saved!")

# --- TAB 2: STANDINGS ---
with t2:
    cols = st.columns(len(MEMBER_POOLS))
    lb_list = []
    for i, m in enumerate(MEMBER_POOLS.keys()):
        # Week Logic
        w_pts = 0
        m_curr = db["selections"].get(current_week, {}).get(m, {"squad": [], "cap": ""})
        for p in m_curr["squad"]:
            sc = db["scores"].get(p, {})
            pts = sum([v for k, v in sc.items() if k in match_list])
            w_pts += (pts * 2) if p == m_curr["cap"] else pts
        # Total Logic
        t_pts = 0
        for wk, matches in SEASON_WEEKS.items():
            m_wk = db["selections"].get(wk, {}).get(m, {"squad": [], "cap": ""})
            for p in m_wk["squad"]:
                sc = db["scores"].get(p, {})
                pts = sum([v for k, v in sc.items() if k in matches])
                t_pts += (pts * 2) if p == m_wk["cap"] else pts
        
        lb_list.append({"Manager": m, "Weekly": w_pts, "Total": t_pts})
        with cols[i]:
            st.markdown(f'<div class="lb-card"><b>{m}</b><br><span class="weekly-pts">Week: {w_pts}</span><span class="total-pts">{t_pts}</span><small>SEASON</small></div>', unsafe_allow_html=True)
    st.table(pd.DataFrame(lb_list).sort_values("Total", ascending=False))

# --- TAB 3: ADMIN ---
with t3:
    sel_match = st.selectbox("Select Match to Score", match_list)
    m_teams = [t.strip() for t in sel_match.split(":")[1].split("(")[0].split(" vs ")]
    
    picked = set()
    for m_data in db["selections"].get(current_week, {}).values():
        picked.update(m_data["squad"])
    
    # Filter only players in the selected match teams
    m_players = [p for p in picked if PLAYER_MASTER.get(p, {}).get('team') in m_teams]

    new_sc = {}
    for p in sorted(m_players):
        with st.expander(f"● {p} ({PLAYER_MASTER[p]['team']})"):
            c1, c2, c3 = st.columns(3)
            r = c1.number_input("Runs", 0, key=f"r_{p}_{sel_match}")
            w = c2.number_input("Wickets", 0, key=f"w_{p}_{sel_match}")
            f = c3.number_input("Fielding", 0, key=f"f_{p}_{sel_match}")
            new_sc[p] = r + (w * 20) + (f * 5)

    if st.button("🔥 PUSH MATCH SCORES", type="primary", use_container_width=True):
        for p, pts in new_sc.items():
            if p not in db["scores"]: db["scores"][p] = {}
            db["scores"][p][sel_match] = pts
        save_db(db)
        st.success("Synced!")
        st.rerun()

    st.divider()
    if st.button("🗑️ CLEAR DATA"):
        st.session_state['confirm_del'] = True
    if st.session_state.get('confirm_del'):
        st.warning("Confirm Deletion?")
        if st.button(f"Clear {sel_match}"):
            for p in db["scores"]:
                if sel_match in db["scores"][p]: del db["scores"][p][sel_match]
            save_db(db)
            st.session_state['confirm_del'] = False
            st.rerun()
        if st.button("Cancel"):
            st.session_state['confirm_del'] = False
            st.rerun()
        
