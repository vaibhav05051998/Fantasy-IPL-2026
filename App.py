import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# --- 1. GLOBAL DATA (MUST BE AT TOP) ---
TEAM_STYLING = {
    'RCB': '#d11d26', 'MI': '#004ba0', 'CSK': '#fdb913', 'SRH': '#f26522',
    'RR': '#ea1a85', 'KKR': '#3a225d', 'GT': '#1b2133', 'LSG': '#0057e2',
    'DC': '#0078bc', 'PBKS': '#dd1f2d'
}

IPL_SCHEDULE = [
    "Match 01: RCB vs SRH (Mar 28)", "Match 02: MI vs KKR (Mar 29)", 
    "Match 03: RR vs CSK (Mar 30)", "Match 04: PBKS vs GT (Mar 31)",
    "Match 05: LSG vs DC (Apr 01)"
]

MEMBER_POOLS = {
    'Kazim': ['Rajat Patidar', 'Devdutt Padikkal', 'Shimron Hetmyer', 'Dhruv Jurel', 'Vaibhav Suryavanshi', 'Priyansh Arya', 'Ryan Rickelton', 'Aiden Markram', 'Angkrish Raghuvanshi', 'Shahrukh Khan', 'Nitish Rana', 'Prashant Veer', 'Anshul Kambhoj', 'Axar Patel', 'Gudakesh Motie', 'Will Jacks', 'Marcus Stoinis', 'Shashank Singh', 'Nitish Kumar Reddy', 'Pat Cummins', 'Jacob Duffy', 'Josh Hazlewood'],
    'Adi': ['Philip Salt', 'Yashasvi Jaiswal', 'Prabhsimran Singh', 'Nicholas Pooran', 'Tim Seifert', 'Shubman Gill', 'Ayush Mhatre', 'Ashutosh Sharma', 'Rahul Tewatia', 'Jasprit Bumrah', 'Ravindra Jadeja', 'Abhishek Sharma', 'Harshal Patel', 'Jofra Archer', 'Yuzvendra Chahal', 'Allah Ghazanfar', 'Digvesh Rathi', 'Prasidh Krishna', 'Umran Malik', 'Vipraj Nigam'],
    'Aatish': ['Tim David', 'Jitesh Sharma', 'Nehal Wadhera', 'Quinton de Kock', 'Sherfane Rutherford', 'Rohit Sharma', 'Rishabh Pant', 'Abdul Samad', 'Matthew Breetzke', 'Abishek Porel', 'Tristan Stubbs', 'Pathum Nissanka', 'MS Dhoni', 'Dewald Brevis', 'Shivam Dube', 'Rashid Khan', 'Sunil Narine', 'Shahbaz Ahmed', 'Hardik Pandya', 'Donovan Ferreira', 'Jacob Bethell'],
    'Shreejith': ['Travis Head', 'Ishan Kishan', 'Riyan Parag', 'Shreyas Iyer', 'Ayush Badoni', 'Himmat Singh', 'Manish Pandey', 'Ajinkya Rahane', 'Sai Sudharsan', 'Vishnu Vinod', 'Sarfaraz Khan', 'Ruturaj Gaikwad', 'Ramakrishna Ghosh', 'Mitchell Marsh', 'Krunal Pandya', 'Venkatesh Iyer', 'Jaydev Unadkat', 'Suyash Sharma', 'Sandeep Sharma', 'Arshdeep Singh', 'Trent Boult'],
    'Nagle': ['Heinrich Klaasen', 'Virat Kohli', 'Suryakumar Yadav', 'Rinku Singh', 'KL Rahul', 'Sanju Samson', 'Cameron Green', 'Tilak Varma', 'Marco Jansen', 'Varun Chakaravarthy', 'Lungi Ngidi', 'Jason Holder', 'Mitchell Starc', 'Josh Inglis', 'Ramandeep Singh']
}

PLAYER_MASTER = {
    # ... (Keep your full list of 105 players here as mapped previously)
}

DB_FILE = 'tournament_db.json'

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f: return json.load(f)
        except: pass
    return {"selections": {}, "scores": {}, "totals": {m: 0 for m in MEMBER_POOLS.keys()}, "last_updated": "Never"}

def save_db(data):
    data["last_updated"] = datetime.now().strftime("%d %b, %H:%M")
    with open(DB_FILE, 'w') as f: json.dump(data, f)

# --- 2. UI CONFIG ---
st.set_page_config(page_title="IPL Manager 2026", layout="wide")
db = load_db()
week = "1"

st.markdown("""
<style>
    .player-row { border-radius: 5px; padding: 4px 8px; margin: 2px 0; background: white; border-left: 4px solid #ccc; display: flex; align-items: center; font-size: 0.85rem; }
    .dot { height: 10px; width: 10px; border-radius: 50%; display: inline-block; margin-right: 8px; }
    .lb-card { background: white; padding: 8px; border-radius: 6px; border: 1px solid #ddd; text-align: center; line-height: 1.2; }
    .lb-name { font-size: 0.9rem; font-weight: bold; margin-bottom: 2px; }
    .lb-weekly { font-size: 0.75rem; color: #666; }
    .lb-total { font-size: 1.1rem; color: #ff4b4b; font-weight: 800; }
</style>
""", unsafe_allow_html=True)

st.title("🏆 Inner Circle IPL")
st.caption(f"Last Points Sync: {db.get('last_updated', 'N/A')}")

tab1, tab2, tab4 = st.tabs(["🏏 TEAM", "📊 STANDINGS", "🛡️ ADMIN"])

# --- TAB 1: SELECTION ---
with tab1:
    user = st.selectbox("Manager", list(MEMBER_POOLS.keys()))
    pool = MEMBER_POOLS[user]
    saved_squad = db["selections"].get(week, {}).get(user, {}).get("squad", [])
    
    col_l, col_r = st.columns([3, 1])
    with col_l:
        selected_names = []
        counts = {"BAT": 0, "BOWL": 0, "WK": 0}
        grid = st.columns(3)
        for i, p_name in enumerate(pool):
            p_info = PLAYER_MASTER.get(p_name, {'team': 'RCB', 'role': 'BAT'})
            color = TEAM_STYLING.get(p_info['team'], '#ccc')
            with grid[i % 3]:
                st.markdown(f'<div class="player-row" style="border-left-color: {color}"><span class="dot" style="background-color: {color}"></span>{p_name}</div>', unsafe_allow_html=True)
                if st.checkbox("Pick", key=f"p_{user}_{p_name}", value=(p_name in saved_squad)):
                    selected_names.append(p_name)
                    counts[p_info['role']] += 1
    with col_r:
        st.metric("Total", f"{len(selected_names)}/11")
        if len(selected_names) == 11:
            cap = st.selectbox("Captain", selected_names)
            if st.button("🚀 SAVE TEAM", use_container_width=True):
                if counts['WK'] >= 1 and counts['BOWL'] >= 5:
                    if week not in db["selections"]: db["selections"][week] = {}
                    db["selections"][week][user] = {"squad": selected_names, "cap": cap}
                    save_db(db)
                    st.success("Locked!")

# --- TAB 2: STANDINGS (REDUCED FONT SIZE) ---
with tab2:
    cols = st.columns(len(MEMBER_POOLS))
    lb_list = []
    for i, m in enumerate(MEMBER_POOLS.keys()):
        w_pts = 0
        m_data = db["selections"].get(week, {}).get(m, {"squad": [], "cap": ""})
        for p in m_data["squad"]:
            p_pts = sum(db["scores"].get(p, {}).values())
            w_pts += (p_pts * 2) if p == m_data["cap"] else p_pts
        total = db["totals"][m] + w_pts
        lb_list.append({"Member": m, "Weekly": w_pts, "Total": total})
        
        with cols[i]:
            st.markdown(f"""
            <div class="lb-card">
                <div class="lb-name">{m}</div>
                <div class="lb-weekly">Wk: {w_pts}</div>
                <div class="lb-total">{total}</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("---")
    st.table(pd.DataFrame(lb_list).sort_values("Total", ascending=False))

# --- TAB 4: ADMIN ---
with tab4:
    st.subheader("Admin Scoring")
    selected_match = st.selectbox("Match", IPL_SCHEDULE)
    
    # Filter only selected players
    selected_by_anyone = set()
    for m in db["selections"].get(week, {}).values():
        selected_by_anyone.update(m["squad"])
    
    match_teams = selected_match.split(":")[1].split("(")[0].strip().split(" vs ")
    active = [p for p in selected_by_anyone if PLAYER_MASTER.get(p, {}).get('team') in match_teams]

    new_match_scores = {}
    for p_name in sorted(active):
        role = PLAYER_MASTER[p_name]['role']
        with st.expander(f"● {p_name} ({role})"):
            c1, c2, c3 = st.columns(3)
            r = c1.number_input("Runs", 0, key=f"r_{p_name}")
            w = c2.number_input("Wickets", 0, key=f"w_{p_name}") if role != 'BAT' else 0
            f = c3.number_input("Cat/RO/Stu", 0, key=f"f_{p_name}")
            new_match_scores[p_name] = r + (w * 20) + (f * 5)

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🔥 PUSH POINTS", use_container_width=True, type="primary"):
            for p, pts in new_match_scores.items():
                if p not in db["scores"]: db["scores"][p] = {}
                db["scores"][p][selected_match] = pts
            save_db(db)
            st.rerun()
    with col_btn2:
        if st.button("🗑️ CLEAR ALL", use_container_width=True):
            db["scores"] = {}
            save_db(db)
            st.rerun()
                    
