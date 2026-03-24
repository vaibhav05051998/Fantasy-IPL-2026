import streamlit as st
import pandas as pd
import json
import os

# --- 1. DATA & COLOR CONFIG ---
TEAM_STYLING = {
    'RCB': {'color': '#d11d26', 'icon': '🔴'}, 'MI': {'color': '#004ba0', 'icon': '🔵'},
    'CSK': {'color': '#fdb913', 'icon': '🟡'}, 'SRH': {'color': '#f26522', 'icon': '🟠'},
    'RR': {'color': '#ea1a85', 'icon': '💗'}, 'KKR': {'color': '#3a225d', 'icon': '🟣'},
    'GT': {'color': '#1b2133', 'icon': '🌑'}, 'LSG': {'color': '#0057e2', 'icon': '💧'},
    'DC': {'color': '#0078bc', 'icon': '🏙️'}, 'PBKS': {'color': '#dd1f2d', 'icon': '🦁'}
}

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

# (MEMBER_POOLS remains the same as previous)
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

# --- 2. HEADER & STYLE ---
st.set_page_config(page_title="IPL Manager 2026", layout="wide")
db = load_db()
week = "1"

st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .player-card { border-radius: 10px; padding: 10px; margin: 5px; border-left: 10px solid #ccc; background: white; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .metric-card { background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; }
</style>
""", unsafe_allow_html=True)

st.title("🏆 Inner Circle IPL 2026")
st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["🏏 TEAM SELECTION", "📊 GLOBAL STANDINGS", "📜 PLAYER RECORDS", "🛡️ ADMIN ROOM"])

# --- TAB 1: SELECTION (TEAM CARDS) ---
with tab1:
    user = st.selectbox("Choose Manager", list(MEMBER_POOLS.keys()))
    pool = MEMBER_POOLS[user]
    
    col_left, col_right = st.columns([3, 1])
    
    with col_left:
        selected_names = []
        counts = {"BAT": 0, "BOWL": 0, "WK": 0}
        saved_squad = db["selections"].get(week, {}).get(user, {}).get("squad", [])
        
        # 3-column Card View
        grid = st.columns(3)
        for i, p_name in enumerate(pool):
            p_info = PLAYER_MASTER.get(p_name, {'team': 'RCB', 'role': 'BAT'})
            team = p_info['team']
            style = TEAM_STYLING.get(team, {'color': '#ccc', 'icon': '👤'})
            
            with grid[i % 3]:
                st.markdown(f"""
                <div class="player-card" style="border-left-color: {style['color']}">
                    <span style="font-size: 1.2em;">{style['icon']} <b>{p_name}</b></span><br>
                    <small>{team} | {p_info['role']}</small>
                </div>
                """, unsafe_allow_html=True)
                if st.checkbox("Select Player", key=f"p_{user}_{p_name}", value=(p_name in saved_squad)):
                    selected_names.append(p_name)
                    counts[p_info['role']] += 1

    with col_right:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.subheader("📋 Squad Audit")
        st.metric("Total", f"{len(selected_names)}/11")
        st.progress(len(selected_names)/11)
        st.write(f"🧤 WK: {counts['WK']}")
        st.write(f"🏏 BAT: {counts['BAT']}")
        st.write(f"⚾ BOWL: {counts['BOWL']}")
        
        if len(selected_names) > 0:
            cap = st.selectbox("Assign Captain", selected_names)
            if st.button("🚀 LOCK SQUAD", use_container_width=True):
                if len(selected_names) == 11 and counts['WK'] >= 1 and counts['BOWL'] >= 5:
                    if week not in db["selections"]: db["selections"][week] = {}
                    db["selections"][week][user] = {"squad": selected_names, "cap": cap}
                    save_db(db)
                    st.success("Squad Registered!")
                else:
                    st.error("Squad requirements not met.")
        st.markdown("</div>", unsafe_allow_html=True)

# --- TAB 2: STANDINGS (COLORED CARDS) ---
with tab2:
    st.subheader("Championship Leaderboard")
    top_cols = st.columns(len(MEMBER_POOLS))
    lb_data = []
    
    for i, m in enumerate(MEMBER_POOLS.keys()):
        w_pts = 0
        m_data = db["selections"].get(week, {}).get(m, {"squad": [], "cap": ""})
        for p in m_data["squad"]:
            p_pts = sum(db["scores"].get(p, {}).values())
            w_pts += (p_pts * 2) if p == m_data["cap"] else p_pts
        total = db["totals"][m] + w_pts
        lb_data.append({"Member": m, "Weekly": w_pts, "Total": total})
        
        with top_cols[i]:
            st.markdown(f"""
            <div class="metric-card">
                <small>Rank #{i+1}</small>
                <h3>{m}</h3>
                <h1 style="color: #ff4b4b;">{total}</h1>
                <p>pts</p>
            </div>
            """, unsafe_allow_html=True)

# --- TAB 4: ADMIN (SCORING) ---
with tab4:
    selected_match = st.selectbox("Select Match to Score", IPL_SCHEDULE)
    match_part = selected_match.split(":")[1].split("(")[0].strip()
    teams = match_part.split(" vs ")
    
    # Filter only selected players in this match
    selected_by_anyone = set()
    for m in db["selections"].get(week, {}).values():
        selected_by_anyone.update(m["squad"])
    active = [p for p in selected_by_anyone if PLAYER_MASTER.get(p, {}).get('team') in teams]

    st.subheader(f"Update: {teams[0]} vs {teams[1]}")
    
    for p_name in sorted(active):
        p_info = PLAYER_MASTER[p_name]
        style = TEAM_STYLING.get(p_info['team'], {'color': '#ccc', 'icon': '👤'})
        
        with st.expander(f"{style['icon']} {p_name} ({p_info['team']})"):
            c1, c2, c3 = st.columns(3)
            r = c1.number_input("Runs", 0, key=f"r_{p_name}")
            w = c2.number_input("Wickets", 0, key=f"w_{p_name}") if p_info['role'] != 'BAT' else 0
            fld = c3.number_input("Fielding (Cat/RO/Stu)", 0, key=f"f_{p_name}")
            
            total = r + (w * 20) + (fld * 5)
            st.write(f"Points: **{total}**")
                    
