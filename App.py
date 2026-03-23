import streamlit as st
import pandas as pd
import json
import os

# --- 1. DATA: IPL 2026 SCHEDULE ---
IPL_SCHEDULE = [
    "Match 01: RCB vs SRH (Mar 28)", "Match 02: MI vs KKR (Mar 29)", 
    "Match 03: RR vs CSK (Mar 30)", "Match 04: PBKS vs GT (Mar 31)",
    "Match 05: LSG vs DC (Apr 01)", "Match 06: KKR vs SRH (Apr 02)",
    "Match 07: CSK vs PBKS (Apr 03)", "Match 08: DC vs MI (Apr 04)",
    "Match 09: GT vs RR (Apr 04)", "Match 10: SRH vs LSG (Apr 05)",
    "Match 11: RCB vs CSK (Apr 05)", "Match 12: KKR vs PBKS (Apr 06)",
    "Match 13: RR vs MI (Apr 07)", "Match 14: DC vs GT (Apr 08)",
    "Match 15: KKR vs LSG (Apr 09)", "Match 16: RR vs RCB (Apr 10)",
    "Match 17: PBKS vs SRH (Apr 11)", "Match 18: CSK vs DC (Apr 11)",
    "Match 19: LSG vs GT (Apr 12)", "Match 20: MI vs RCB (Apr 12)"
]

# --- 2. PLAYER MASTER DATA (TEAM & ROLE SYNCED) ---
PLAYER_MASTER = {
    'Rajat Patidar': {'team': 'RCB', 'role': 'BAT'}, 'Devdutt Padikkal': {'team': 'RCB', 'role': 'BAT'},
    'Shimron Hetmyer': {'team': 'RR', 'role': 'BAT'}, 'Dhruv Jurel': {'team': 'RR', 'role': 'WK'},
    'Vaibhav Suryavanshi': {'team': 'RR', 'role': 'BAT'}, 'Priyansh Arya': {'team': 'DC', 'role': 'BAT'},
    'Ryan Rickelton': {'team': 'MI', 'role': 'WK'}, 'Aiden Markram': {'team': 'LSG', 'role': 'BAT'},
    'Angkrish Raghuvanshi': {'team': 'KKR', 'role': 'BAT'}, 'Shahrukh Khan': {'team': 'GT', 'role': 'BAT'},
    'Nitish Rana': {'team': 'DC', 'role': 'BAT'}, 'Prashant Veer': {'team': 'CSK', 'role': 'BOWL'},
    'Anshul Kambhoj': {'team': 'CSK', 'role': 'BOWL'}, 'Axar Patel': {'team': 'DC', 'role': 'BOWL'},
    'Gudakesh Motie': {'team': 'MI', 'role': 'BOWL'}, 'Will Jacks': {'team': 'MI', 'role': 'BAT'},
    'Marcus Stoinis': {'team': 'GT', 'role': 'BAT'}, 'Shashank Singh': {'team': 'PBKS', 'role': 'BAT'},
    'Nitish Kumar Reddy': {'team': 'SRH', 'role': 'BOWL'}, 'Pat Cummins': {'team': 'SRH', 'role': 'BOWL'},
    'Jacob Duffy': {'team': 'MI', 'role': 'BOWL'}, 'Josh Hazlewood': {'team': 'MI', 'role': 'BOWL'},
    'Philip Salt': {'team': 'RCB', 'role': 'WK'}, 'Yashasvi Jaiswal': {'team': 'RR', 'role': 'BAT'},
    'Prabhsimran Singh': {'team': 'PBKS', 'role': 'WK'}, 'Nicholas Pooran': {'team': 'LSG', 'role': 'WK'},
    'Tim Seifert': {'team': 'KKR', 'role': 'WK'}, 'Shubman Gill': {'team': 'GT', 'role': 'BAT'},
    'Ayush Mhatre': {'team': 'CSK', 'role': 'BAT'}, 'Ashutosh Sharma': {'team': 'DC', 'role': 'BAT'},
    'Rahul Tewatia': {'team': 'GT', 'role': 'BOWL'}, 'Jasprit Bumrah': {'team': 'MI', 'role': 'BOWL'},
    'Ravindra Jadeja': {'team': 'RR', 'role': 'BOWL'}, 'Abhishek Sharma': {'team': 'SRH', 'role': 'BAT'},
    'Harshal Patel': {'team': 'SRH', 'role': 'BOWL'}, 'Jofra Archer': {'team': 'RR', 'role': 'BOWL'},
    'Yuzvendra Chahal': {'team': 'RR', 'role': 'BOWL'}, 'Allah Ghazanfar': {'team': 'MI', 'role': 'BOWL'},
    'Digvesh Rathi': {'team': 'LSG', 'role': 'BOWL'}, 'Prasidh Krishna': {'team': 'GT', 'role': 'BOWL'},
    'Umran Malik': {'team': 'KKR', 'role': 'BOWL'}, 'Vipraj Nigam': {'team': 'DC', 'role': 'BOWL'},
    'Tim David': {'team': 'MI', 'role': 'BAT'}, 'Jitesh Sharma': {'team': 'PBKS', 'role': 'WK'},
    'Nehal Wadhera': {'team': 'MI', 'role': 'BAT'}, 'Quinton de Kock': {'team': 'MI', 'role': 'WK'},
    'Sherfane Rutherford': {'team': 'RCB', 'role': 'BAT'}, 'Rohit Sharma': {'team': 'MI', 'role': 'BAT'},
    'Rishabh Pant': {'team': 'LSG', 'role': 'WK'}, 'Abdul Samad': {'team': 'LSG', 'role': 'BAT'},
    'Matthew Breetzke': {'team': 'LSG', 'role': 'BAT'}, 'Abishek Porel': {'team': 'DC', 'role': 'WK'},
    'Tristan Stubbs': {'team': 'DC', 'role': 'WK'}, 'Pathum Nissanka': {'team': 'SRH', 'role': 'BAT'},
    'MS Dhoni': {'team': 'CSK', 'role': 'WK'}, 'Dewald Brevis': {'team': 'CSK', 'role': 'BAT'},
    'Shivam Dube': {'team': 'CSK', 'role': 'BAT'}, 'Rashid Khan': {'team': 'GT', 'role': 'BOWL'},
    'Sunil Narine': {'team': 'KKR', 'role': 'BOWL'}, 'Shahbaz Ahmed': {'team': 'LSG', 'role': 'BOWL'},
    'Hardik Pandya': {'team': 'MI', 'role': 'BAT'}, 'Donovan Ferreira': {'team': 'RR', 'role': 'WK'},
    'Jacob Bethell': {'team': 'MI', 'role': 'BOWL'}, 'Travis Head': {'team': 'SRH', 'role': 'BAT'},
    'Ishan Kishan': {'team': 'SRH', 'role': 'WK'}, 'Riyan Parag': {'team': 'RR', 'role': 'BAT'},
    'Shreyas Iyer': {'team': 'SRH', 'role': 'BAT'}, 'Ayush Badoni': {'team': 'LSG', 'role': 'BAT'},
    'Himmat Singh': {'team': 'LSG', 'role': 'BAT'}, 'Manish Pandey': {'team': 'KKR', 'role': 'BAT'},
    'Ajinkya Rahane': {'team': 'KKR', 'role': 'BAT'}, 'Sai Sudharsan': {'team': 'GT', 'role': 'BAT'},
    'Vishnu Vinod': {'team': 'RR', 'role': 'WK'}, 'Sarfaraz Khan': {'team': 'CSK', 'role': 'BAT'},
    'Ruturaj Gaikwad': {'team': 'CSK', 'role': 'BAT'}, 'Ramakrishna Ghosh': {'team': 'CSK', 'role': 'BOWL'},
    'Mitchell Marsh': {'team': 'LSG', 'role': 'BAT'}, 'Krunal Pandya': {'team': 'MI', 'role': 'BOWL'},
    'Venkatesh Iyer': {'team': 'MI', 'role': 'BAT'}, 'Jaydev Unadkat': {'team': 'SRH', 'role': 'BOWL'},
    'Suyash Sharma': {'team': 'MI', 'role': 'BOWL'}, 'Sandeep Sharma': {'team': 'RR', 'role': 'BOWL'},
    'Arshdeep Singh': {'team': 'PBKS', 'role': 'BOWL'}, 'Trent Boult': {'team': 'MI', 'role': 'BOWL'},
    'Heinrich Klaasen': {'team': 'SRH', 'role': 'WK'}, 'Virat Kohli': {'team': 'RCB', 'role': 'BAT'},
    'Suryakumar Yadav': {'team': 'MI', 'role': 'BAT'}, 'Rinku Singh': {'team': 'KKR', 'role': 'BAT'},
    'KL Rahul': {'team': 'DC', 'role': 'WK'}, 'Sanju Samson': {'team': 'CSK', 'role': 'WK'},
    'Cameron Green': {'team': 'KKR', 'role': 'BAT'}, 'Tilak Varma': {'team': 'MI', 'role': 'BAT'},
    'Marco Jansen': {'team': 'SRH', 'role': 'BOWL'}, 'Varun Chakaravarthy': {'team': 'KKR', 'role': 'BOWL'},
    'Lungi Ngidi': {'team': 'DC', 'role': 'BOWL'}, 'Jason Holder': {'team': 'GT', 'role': 'BOWL'},
    'Mitchell Starc': {'team': 'DC', 'role': 'BOWL'}, 'Josh Inglis': {'team': 'DC', 'role': 'WK'},
    'Ramandeep Singh': {'team': 'KKR', 'role': 'BAT'}
}

# Member Pools
MEMBER_POOLS = {
    'Kazim': ['Rajat Patidar', 'Devdutt Padikkal', 'Shimron Hetmyer', 'Dhruv Jurel', 'Vaibhav Suryavanshi', 'Priyansh Arya', 'Ryan Rickelton', 'Aiden Markram', 'Angkrish Raghuvanshi', 'Shahrukh Khan', 'Nitish Rana', 'Prashant Veer', 'Anshul Kambhoj', 'Axar Patel', 'Gudakesh Motie', 'Will Jacks', 'Marcus Stoinis', 'Shashank Singh', 'Nitish Kumar Reddy', 'Pat Cummins', 'Jacob Duffy', 'Josh Hazlewood'],
    'Adi': ['Philip Salt', 'Yashasvi Jaiswal', 'Prabhsimran Singh', 'Nicholas Pooran', 'Tim Seifert', 'Shubman Gill', 'Ayush Mhatre', 'Ashutosh Sharma', 'Rahul Tewatia', 'Jasprit Bumrah', 'Ravindra Jadeja', 'Abhishek Sharma', 'Harshal Patel', 'Jofra Archer', 'Yuzvendra Chahal', 'Allah Ghazanfar', 'Digvesh Rathi', 'Prasidh Krishna', 'Umran Malik', 'Vipraj Nigam'],
    'Aatish': ['Tim David', 'Jitesh Sharma', 'Nehal Wadhera', 'Quinton de Kock', 'Sherfane Rutherford', 'Rohit Sharma', 'Rishabh Pant', 'Abdul Samad', 'Matthew Breetzke', 'Abishek Porel', 'Tristan Stubbs', 'Pathum Nissanka', 'MS Dhoni', 'Dewald Brevis', 'Shivam Dube', 'Rashid Khan', 'Sunil Narine', 'Shahbaz Ahmed', 'Hardik Pandya', 'Donovan Ferreira', 'Jacob Bethell'],
    'Shreejith': ['Travis Head', 'Ishan Kishan', 'Riyan Parag', 'Shreyas Iyer', 'Ayush Badoni', 'Himmat Singh', 'Manish Pandey', 'Ajinkya Rahane', 'Sai Sudharsan', 'Vishnu Vinod', 'Sarfaraz Khan', 'Ruturaj Gaikwad', 'Ramakrishna Ghosh', 'Mitchell Marsh', 'Krunal Pandya', 'Venkatesh Iyer', 'Jaydev Unadkat', 'Suyash Sharma', 'Sandeep Sharma', 'Arshdeep Singh', 'Trent Boult'],
    'Nagle': ['Heinrich Klaasen', 'Virat Kohli', 'Suryakumar Yadav', 'Rinku Singh', 'KL Rahul', 'Sanju Samson', 'Cameron Green', 'Tilak Varma', 'Marco Jansen', 'Varun Chakaravarthy', 'Lungi Ngidi', 'Jason Holder', 'Mitchell Starc', 'Josh Inglis', 'Ramandeep Singh']
}

DB_FILE = 'tournament_db.json'

# --- 3. DATABASE FUNCTIONS ---
def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f: return json.load(f)
        except: pass
    return {"selections": {}, "scores": {}, "totals": {m: 0 for m in MEMBER_POOLS.keys()}, "force_unlock": True}

def save_db(data):
    with open(DB_FILE, 'w') as f: json.dump(data, f)

# --- 4. APP UI ---
st.set_page_config(page_title="Inner Circle IPL 2026", layout="wide")
db = load_db()
week = "1" 

tab1, tab2, tab3, tab4 = st.tabs(["📋 Selection", "📊 Leaderboard", "📜 Match Logs", "🛡️ Admin Console"])

# (Standard Selection and Leaderboard Logic here)
# ... [Selection Logic Omitted for brevity, but remains in the full final build] ...

# --- TAB 4: ERGONOMIC ADMIN CONSOLE ---
with tab4:
    st.title("🛡️ Super Admin Dashboard")
    selected_match = st.selectbox("🎯 Select Match:", IPL_SCHEDULE)
    
    # Parse Teams
    match_part = selected_match.split(":")[1].split("(")[0].strip()
    team_a, team_b = match_part.split(" vs ")
    
    # Filter Players
    match_players = [n for n, i in PLAYER_MASTER.items() if i['team'] in [team_a, team_b]]
    
    st.subheader(f"Input Stats for {team_a} vs {team_b}")
    st.write("Wicket = 20 pts | Catch = 10 pts | Run = 1 pt")

    new_scores = {}
    
    for p_name in sorted(match_players):
        with st.expander(f"📊 {p_name} ({PLAYER_MASTER[p_name]['team']})"):
            c1, c2, c3 = st.columns(3)
            runs = c1.number_input("Runs", min_value=0, key=f"r_{p_name}")
            wicks = c2.number_input("Wickets", min_value=0, key=f"w_{p_name}")
            catch = c3.number_input("Catches", min_value=0, key=f"c_{p_name}")
            
            # CALCULATION LOGIC
            total_p = (runs * 1) + (wicks * 20) + (catch * 10)
            st.write(f"**Total Points: {total_p}**")
            new_scores[p_name] = total_p

    if st.button("🔥 Push All Scores to Database", use_container_width=True):
        for p_name, p_pts in new_scores.items():
            if p_name not in db["scores"]: db["scores"][p_name] = {}
            db["scores"][p_name][selected_match] = p_pts
        save_db(db)
        st.success("All match scores successfully updated!")
        st.balloons()
