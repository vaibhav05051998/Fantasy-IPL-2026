import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# --- 1. GLOBAL DATA (MUST BE AT THE TOP) ---
TEAM_STYLING = {
    'RCB': '#d11d26', 'MI': '#004ba0', 'CSK': '#fdb913', 'SRH': '#f26522',
    'RR': '#ea1a85', 'KKR': '#3a225d', 'GT': '#1b2133', 'LSG': '#0057e2',
    'DC': '#0078bc', 'PBKS': '#dd1f2d'
}

MEMBER_POOLS = {
    'Kazim': ['Rajat Patidar', 'Devdutt Padikkal', 'Shimron Hetmyer', 'Dhruv Jurel', 'Vaibhav Suryavanshi', 'Priyansh Arya', 'Ryan Rickelton', 'Aiden Markram', 'Angkrish Raghuvanshi', 'Shahrukh Khan', 'Nitish Rana', 'Prashant Veer', 'Anshul Kambhoj', 'Axar Patel', 'Gudakesh Motie', 'Will Jacks', 'Marcus Stoinis', 'Shashank Singh', 'Nitish Kumar Reddy', 'Pat Cummins', 'Jacob Duffy', 'Josh Hazlewood'],
    'Adi': ['Philip Salt', 'Yashasvi Jaiswal', 'Prabhsimran Singh', 'Nicholas Pooran', 'Tim Seifert', 'Shubman Gill', 'Ayush Mhatre', 'Ashutosh Sharma', 'Rahul Tewatia', 'Jasprit Bumrah', 'Ravindra Jadeja', 'Abhishek Sharma', 'Harshal Patel', 'Jofra Archer', 'Yuzvendra Chahal', 'Allah Ghazanfar', 'Digvesh Rathi', 'Prasidh Krishna', 'Umran Malik', 'Vipraj Nigam'],
    'Aatish': ['Tim David', 'Jitesh Sharma', 'Nehal Wadhera', 'Quinton de Kock', 'Sherfane Rutherford', 'Rohit Sharma', 'Rishabh Pant', 'Abdul Samad', 'Matthew Breetzke', 'Abishek Porel', 'Tristan Stubbs', 'Pathum Nissanka', 'MS Dhoni', 'Dewald Brevis', 'Shivam Dube', 'Rashid Khan', 'Sunil Narine', 'Shahbaz Ahmed', 'Hardik Pandya', 'Donovan Ferreira', 'Jacob Bethell'],
    'Shreejith': ['Travis Head', 'Ishan Kishan', 'Riyan Parag', 'Shreyas Iyer', 'Ayush Badoni', 'Himmat Singh', 'Manish Pandey', 'Ajinkya Rahane', 'Sai Sudharsan', 'Vishnu Vinod', 'Sarfaraz Khan', 'Ruturaj Gaikwad', 'Ramakrishna Ghosh', 'Mitchell Marsh', 'Krunal Pandya', 'Venkatesh Iyer', 'Jaydev Unadkat', 'Suyash Sharma', 'Sandeep Sharma', 'Arshdeep Singh', 'Trent Boult'],
    'Nagle': ['Heinrich Klaasen', 'Virat Kohli', 'Suryakumar Yadav', 'Rinku Singh', 'KL Rahul', 'Sanju Samson', 'Cameron Green', 'Tilak Varma', 'Marco Jansen', 'Varun Chakaravarthy', 'Lungi Ngidi', 'Jason Holder', 'Mitchell Starc', 'Josh Inglis', 'Ramandeep Singh']
}

# Full Schedule for Calendar Overview
SEASON_WEEKS = {
    "Week 1": ["Match 01: RCB vs SRH", "Match 02: MI vs KKR", "Match 03: RR vs CSK"],
    "Week 2": ["Match 04: PBKS vs GT", "Match 05: LSG vs DC", "Match 06: KKR vs SRH"],
    "Week 3": ["Match 07: CSK vs PBKS", "Match 08: DC vs MI", "Match 09: GT vs RR"],
    "Week 4": ["Match 10: SRH vs LSG", "Match 11: RCB vs CSK", "Match 12: KKR vs PBKS"]
}

# (Ensure your PLAYER_MASTER dict with 105 players is pasted here)
PLAYER_MASTER = {
    'Rajat Patidar': {'team': 'RCB', 'role': 'BAT'}, # ... and so on
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

# --- 2. THEME & SIDEBAR ---
st.set_page_config(page_title="Inner Circle IPL", layout="wide")
db = load_db()

st.sidebar.title("📅 Season Control")
current_week = st.sidebar.selectbox("Active Week", list(SEASON_WEEKS.keys()))

# Sidebar Match Counter
match_list = SEASON_WEEKS[current_week]
team_counts = {}
for m in match_list:
    teams = m.split(":")[1].split(" vs ")
    for t in teams:
        t = t.strip()
        team_counts[t] = team_counts.get(t, 0) + 1

st.sidebar.subheader("Weekly Matches")
for team, count in sorted(team_counts.items(), key=lambda x: x[1], reverse=True):
    st.sidebar.write(f"● {team}: **{count}**")

# --- 3. UI LAYOUT ---
st.markdown("""
<style>
    .player-card { padding: 5px 10px; margin: 2px 0; background: white; border-radius: 4px; border-left: 5px solid #ccc; font-size: 0.85rem; }
    .lb-card { background: white; padding: 10px; border-radius: 6px; border: 1px solid #eee; text-align: center; }
</style>
""", unsafe_allow_html=True)

st.title("🏆 Inner Circle IPL 2026")
tab1, tab2, tab4 = st.tabs(["🏏 SELECTION", "📊 STANDINGS", "🛡️ ADMIN"])

# --- TAB 1: SELECTION ---
with tab1:
    st.info(f"📅 Matches: {' | '.join(match_list)}")
    user = st.selectbox("Manager", list(MEMBER_POOLS.keys()))
    pool = MEMBER_POOLS[user]
    saved_squad = db["selections"].get(current_week, {}).get(user, {}).get("squad", [])
    
    col_l, col_r = st.columns([3, 1])
    with col_l:
        selected_names = []
        counts = {"BAT": 0, "BOWL": 0, "WK": 0}
        grid = st.columns(3)
        for i, p_name in enumerate(pool):
            p_info = PLAYER_MASTER.get(p_name, {'team': 'RCB', 'role': 'BAT'})
            color = TEAM_STYLING.get(p_info['team'], '#ccc')
            with grid[i % 3]:
                st.markdown(f'<div class="player-card" style="border-left-color: {color}">{p_name} ({p_info["team"]})</div>', unsafe_allow_html=True)
                if st.checkbox("Pick", key=f"p_{user}_{p_name}_{current_week}", value=(p_name in saved_squad)):
                    selected_names.append(p_name)
                    counts[p_info['role']] += 1
    
    with col_r:
        st.metric("Total", f"{len(selected_names)}/11")
        if len(selected_names) == 11:
            cap = st.selectbox("Captain", selected_names, key=f"cap_{user}")
            if st.button("🚀 LOCK TEAM"):
                if counts['WK'] >= 1 and counts['BOWL'] >= 5:
                    if current_week not in db["selections"]: db["selections"][current_week] = {}
                    db["selections"][current_week][user] = {"squad": selected_names, "cap": cap}
                    save_db(db)
                    st.success("Squad Saved!")

# --- TAB 2: STANDINGS ---
with tab2:
    cols = st.columns(len(MEMBER_POOLS))
    lb_data = []
    for i, m in enumerate(MEMBER_POOLS.keys()):
        # Weekly Score
        w_pts = 0
        m_data = db["selections"].get(current_week, {}).get(m, {"squad": [], "cap": ""})
        for p in m_data["squad"]:
            p_scores = db["scores"].get(p, {})
            p_pts = sum([v for k, v in p_scores.items() if k in SEASON_WEEKS[current_week]])
            w_pts += (p_pts * 2) if p == m_data["cap"] else p_pts
            
        # Total Season Score
        total_pts = 0
        for w_name, w_matches in SEASON_WEEKS.items():
            w_sel = db["selections"].get(w_name, {}).get(m, {"squad": [], "cap": ""})
            for p in w_sel["squad"]:
                p_scores = db["scores"].get(p, {})
                pts = sum([v for k, v in p_scores.items() if k in w_matches])
                total_pts += (pts * 2) if p == w_sel["cap"] else pts
        
        lb_data.append({"Member": m, "Weekly": w_pts, "Total": total_pts})
        with cols[i]:
            st.markdown(f'<div class="lb-card"><b>{m}</b><br><small>Wk: {w_pts}</small><br><span style="color:red; font-size:1.2rem;">{total_pts}</span></div>', unsafe_allow_html=True)

# --- TAB 4: ADMIN (SAFETY CLEAR) ---
with tab4:
    st.subheader("Admin Scoring")
    selected_match = st.selectbox("Match", SEASON_WEEKS[current_week])
    
    # Filter active players for scoring
    active = []
    for m in db["selections"].get(current_week, {}).values():
        active.extend(m["squad"])
    
    match_teams = selected_match.split(":")[1].split(" vs ")
    match_players = [p for p in set(active) if PLAYER_MASTER.get(p, {}).get('team') in match_teams]

    new_scores = {}
    for p in sorted(match_players):
        with st.expander(f"● {p}"):
            c1, c2, c3 = st.columns(3)
            r = c1.number_input("Runs", 0, key=f"r_{p}")
            w = c2.number_input("Wickets", 0, key=f"w_{p}")
            f = c3.number_input("Fielding", 0, key=f"f_{p}")
            new_scores[p] = r + (w * 20) + (f * 5)

    if st.button("🔥 PUSH SCORES", type="primary", use_container_width=True):
        for p, pts in new_scores.items():
            if p not in db["scores"]: db["scores"][p] = {}
            db["scores"][p][selected_match] = pts
        save_db(db)
        st.success("Synced!")

    st.divider()
    if st.button("🗑️ CLEAR DATA OPTIONS", use_container_width=True):
        st.session_state['confirm'] = True

    if st.session_state.get('confirm'):
        st.warning("Are you sure? This cannot be undone.")
        if st.button("CONFIRM: Clear This Match Only"):
            for p in db["scores"]:
                if selected_match in db["scores"][p]: del db["scores"][p][selected_match]
            save_db(db)
            st.session_state['confirm'] = False
            st.rerun()
        if st.button("CONFIRM: RESET ENTIRE SEASON"):
            db = {"selections": {}, "scores": {}, "last_updated": "Never"}
            save_db(db)
            st.session_state['confirm'] = False
            st.rerun()
        if st.button("Cancel"):
            st.session_state['confirm'] = False
            st.rerun()
    
