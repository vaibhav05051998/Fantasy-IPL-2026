import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# --- 1. GLOBAL DATA & CONFIG ---
TEAM_STYLING = {
    'RCB': '#d11d26', 'MI': '#004ba0', 'CSK': '#fdb913', 'SRH': '#f26522',
    'RR': '#ea1a85', 'KKR': '#3a225d', 'GT': '#1b2133', 'LSG': '#0057e2',
    'DC': '#0078bc', 'PBKS': '#dd1f2d'
}

# Adjusted Week Setting: Saturday to Friday
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

# (Add your 105 player MASTER mapping here)
PLAYER_MASTER = {
    'Rajat Patidar': {'team': 'RCB', 'role': 'BAT'}, 'Devdutt Padikkal': {'team': 'RCB', 'role': 'BAT'},
    # ... fill the rest ...
}

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

# --- 2. LAYOUT & SIDEBAR ---
st.set_page_config(page_title="Inner Circle IPL", layout="wide")
db = load_db()

st.sidebar.title("📅 Weekly Cycle")
current_week = st.sidebar.selectbox("Select Week", list(SEASON_WEEKS.keys()))

# Calendar Stats for Sidebar
match_list = SEASON_WEEKS[current_week]
team_counts = {}
for m in match_list:
    if "vs" in m:
        teams = m.split(":")[1].split("(")[0].split(" vs ")
        for t in teams:
            t = t.strip()
            team_counts[t] = team_counts.get(t, 0) + 1

st.sidebar.subheader("Matches This Week")
for team, count in sorted(team_counts.items(), key=lambda x: x[1], reverse=True):
    st.sidebar.write(f"● {team}: **{count}**")

# --- 3. UI STYLE ---
st.markdown("""
<style>
    .player-card { padding: 4px 8px; margin: 2px 0; background: white; border-radius: 4px; border-left: 5px solid #ccc; font-size: 0.8rem; }
    .lb-card { background: #f9f9f9; padding: 10px; border-radius: 8px; border: 1px solid #ddd; text-align: center; }
    .weekly-pts { color: #555; font-size: 0.85rem; font-weight: bold; }
    .total-pts { color: #ff4b4b; font-size: 1.3rem; font-weight: 900; }
</style>
""", unsafe_allow_html=True)

st.title("🏆 Inner Circle IPL 2026")
tab1, tab2, tab4 = st.tabs(["🏏 TEAM SELECTION", "📊 STANDINGS", "🛡️ ADMIN"])

# --- TAB 1: SELECTION ---
with tab1:
    st.info(f"📅 **{current_week} Schedule:** {' | '.join(match_list)}")
    user = st.selectbox("Manager", list(MEMBER_POOLS.keys()))
    pool = MEMBER_POOLS[user]
    saved_squad = db["selections"].get(current_week, {}).get(user, {}).get("squad", [])
    
    col_l, col_r = st.columns([3, 1])
    with col_l:
        selected_names = []
        counts = {"BAT": 0, "BOWL": 0, "WK": 0}
        grid = st.columns(3)
        for i, p_name in enumerate(pool):
            p_info = PLAYER_MASTER.get(p_name, {'team': '?', 'role': 'BAT'})
            color = TEAM_STYLING.get(p_info['team'], '#ccc')
            with grid[i % 3]:
                st.markdown(f'<div class="player-card" style="border-left-color: {color}">{p_name} ({p_info["team"]})</div>', unsafe_allow_html=True)
                if st.checkbox("Pick", key=f"p_{user}_{p_name}_{current_week}", value=(p_name in saved_squad)):
                    selected_names.append(p_name)
                    counts[p_info['role']] += 1
    
    with col_r:
        st.metric("Total Players", f"{len(selected_names)}/11")
        if len(selected_names) == 11:
            cap = st.selectbox("Assign Captain", selected_names, key=f"cap_{user}_{current_week}")
            if st.button("🚀 SAVE TEAM"):
                if counts['WK'] >= 1 and counts['BOWL'] >= 5:
                    if current_week not in db["selections"]: db["selections"][current_week] = {}
                    db["selections"][current_week][user] = {"squad": selected_names, "cap": cap}
                    save_db(db)
                    st.success("Squad Locked!")

# --- TAB 2: STANDINGS (WEEKLY VS TOTAL) ---
with tab2:
    cols = st.columns(len(MEMBER_POOLS))
    lb_data = []
    for i, m in enumerate(MEMBER_POOLS.keys()):
        # Weekly Score Logic
        w_pts = 0
        m_curr_data = db["selections"].get(current_week, {}).get(m, {"squad": [], "cap": ""})
        for p in m_curr_data["squad"]:
            p_scores = db["scores"].get(p, {})
            pts = sum([v for k, v in p_scores.items() if k in SEASON_WEEKS[current_week]])
            w_pts += (pts * 2) if p == m_curr_data["cap"] else pts
            
        # Cumulative Total Logic
        total_pts = 0
        for week_key, week_matches in SEASON_WEEKS.items():
            m_wk_data = db["selections"].get(week_key,
