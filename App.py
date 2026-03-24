import streamlit as st
import pandas as pd
import json
import os

# --- 1. DATA SETUP ---
IPL_SCHEDULE = ["Match 01: RCB vs SRH (Mar 28)", "Match 02: MI vs KKR (Mar 29)", "Match 03: RR vs CSK (Mar 30)"]

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

MEMBER_POOLS = {
    'Kazim': ['Rajat Patidar', 'Devdutt Padikkal', 'Shimron Hetmyer', 'Dhruv Jurel', 'Vaibhav Suryavanshi', 'Priyansh Arya', 'Ryan Rickelton', 'Aiden Markram', 'Angkrish Raghuvanshi', 'Shahrukh Khan', 'Nitish Rana', 'Prashant Veer', 'Anshul Kambhoj', 'Axar Patel', 'Gudakesh Motie', 'Will Jacks', 'Marcus Stoinis', 'Shashank Singh', 'Nitish Kumar Reddy', 'Pat Cummins', 'Jacob Duffy', 'Josh Hazlewood'],
    'Adi': ['Philip Salt', 'Yashasvi Jaiswal', 'Prabhsimran Singh', 'Nicholas Pooran', 'Tim Seifert', 'Shubman Gill', 'Ayush Mhatre', 'Ashutosh Sharma', 'Rahul Tewatia', 'Jasprit Bumrah', 'Ravindra Jadeja', 'Abhishek Sharma', 'Harshal Patel', 'Jofra Archer', 'Yuzvendra Chahal', 'Allah Ghazanfar', 'Digvesh Rathi', 'Prasidh Krishna', 'Umran Malik', 'Vipraj Nigam'],
    'Aatish': ['Tim David', 'Jitesh Sharma', 'Nehal Wadhera', 'Quinton de Kock', 'Sherfane Rutherford', 'Rohit Sharma', 'Rishabh Pant', 'Abdul Samad', 'Matthew Breetzke', 'Abishek Porel', 'Tristan Stubbs', 'Pathum Nissanka', 'MS Dhoni', 'Dewald Brevis', 'Shivam Dube', 'Rashid Khan', 'Sunil Narine', 'Shahbaz Ahmed', 'Hardik Pandya', 'Donovan Ferreira', 'Jacob Bethell'],
    'Shreejith': ['Travis Head', 'Ishan Kishan', 'Riyan Parag', 'Shreyas Iyer', 'Ayush Badoni', 'Himmat Singh', 'Manish Pandey', 'Ajinkya Rahane', 'Sai Sudharsan', 'Vishnu Vinod', 'Sarfaraz Khan', 'Ruturaj Gaikwad', 'Ramakrishna Ghosh', 'Mitchell Marsh', 'Krunal Pandya', 'Venkatesh Iyer', 'Jaydev Unadkat', 'Suyash Sharma', 'Sandeep Sharma', 'Arshdeep Singh', 'Trent Boult'],
    'Nagle': ['Heinrich Klaasen', 'Virat Kohli', 'Suryakumar Yadav', 'Rinku Singh', 'KL Rahul', 'Sanju Samson', 'Cameron Green', 'Tilak Varma', 'Marco Jansen', 'Varun Chakaravarthy', 'Lungi Ngidi', 'Jason Holder', 'Mitchell Starc', 'Josh Inglis', 'Ramandeep Singh']
}

DB_FILE = 'tournament_db.json'
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f: return json.load(f)
    return {"selections": {}, "scores": {}, "totals": {m: 0 for m in MEMBER_POOLS.keys()}}

def save_db(data):
    with open(DB_FILE, 'w') as f: json.dump(data, f)

# --- 2. THEME & HEADER ---
st.set_page_config(page_title="Inner Circle IPL 2026", layout="wide")
db = load_db()
week = "1"

# Custom CSS for modern feel
st.markdown("""
<style>
    .stMetric { background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #ff4b4b; }
    .player-card { border: 1px solid #e6e9ef; padding: 10px; border-radius: 8px; margin-bottom: 5px; }
    .status-open { color: #28a745; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("🏆 Inner Circle IPL 2026")
st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["🎯 SELECTION", "📊 STANDINGS", "📜 HISTORY", "⚙️ ADMIN"])

# --- TAB 1: SELECTION (Modern Cards) ---
with tab1:
    user = st.selectbox("Select Member", list(MEMBER_POOLS.keys()))
    pool = MEMBER_POOLS[user]
    saved_squad = db["selections"].get(week, {}).get(user, {}).get("squad", [])
    
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.subheader(f"Building Team: {user}")
        selected_names = []
        counts = {"BAT": 0, "BOWL": 0, "WK": 0}
        
        # Grid layout for player selection
        grid_cols = st.columns(3)
        for i, p_name in enumerate(pool):
            role = PLAYER_MASTER.get(p_name, {}).get('role', 'BAT')
            with grid_cols[i % 3]:
                st.markdown(f"**{p_name}** ({role})")
                if st.checkbox("Add to XI", key=f"sel_{user}_{p_name}", value=(p_name in saved_squad)):
                    selected_names.append(p_name)
                    counts[role] += 1
    
    with col_b:
        st.subheader("Team Balance")
        st.metric("Total Players", f"{len(selected_names)}/11")
        st.progress(len(selected_names)/11)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("WK", counts['WK'])
        c2.metric("BOWL", counts['BOWL'])
        c3.metric("BAT", counts['BAT'])

        if len(selected_names) > 0:
            cap = st.selectbox("Choose Captain (2x)", selected_names)
            if st.button("🚀 Confirm Squad", use_container_width=True):
                if len(selected_names) == 11 and counts['WK'] >= 1 and counts['BOWL'] >= 5:
                    if week not in db["selections"]: db["selections"][week] = {}
                    db["selections"][week][user] = {"squad": selected_names, "cap": cap}
                    save_db(db)
                    st.success("Squad Locked!")
                    st.balloons()
                else:
                    st.error("Invalid Balance (Need 11 Total, 1 WK, 5 B
                    
