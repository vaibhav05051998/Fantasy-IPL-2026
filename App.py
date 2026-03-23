import streamlit as st
import pandas as pd
import json
import datetime
import pytz
import os

# --- 1. SETUP & TIME ---
IST = pytz.timezone('Asia/Kolkata')

MEMBER_POOLS = {
    'Kazim': ['Rajat Patidar', 'Padikkal', 'Hetmyer', 'Dhruv Jurel', 'Suryavanshi', 'Priyansh Arya', 'Ryan Rickelton', 'Markram', 'Raghuvanshi', 'Shahrukh Khan', 'Nitish Rana', 'Prashant Veer', 'Anshul Kambhoj', 'Axar Patel', 'Guldakesh Motie', 'Will Jacks', 'Stoinis', 'Shashank Singh', 'Nitish Kumar Reddy', 'Pat Cummins', 'Duffy', 'Hazlewood'],
    'Adi': ['Phil salt', 'Yashasvi Jaiswal', 'Prabhsimran', 'Pooran', 'Seifert', 'Gill', 'Ayush Mhatre', 'Ashutosh Sharma', 'Tewatia', 'Bumrah', 'Jadeja', 'Abhishek sharma', 'Harshal patel', 'Archer', 'Chahal', 'Ghazanfar', 'Digvesh', 'Prasidh', 'Umran Malik', 'Vipraj nigam'],
    'Aatish': ['Tim David', 'Jitesh Sharma', 'Wadhera', 'de Kock', 'Sherfane Rutherford', 'Rohit Sharma', 'Rishabh Pant', 'Samad', 'Breetzke', 'Porel', 'Stubbs', 'Nissanka', 'MS Dhoni', 'Brevis', 'Dube', 'Rashid Khan', 'Narine', 'Shahbaz Ahmed', 'Hardik Pandya', 'Donovan', 'Bethell'],
    'Shreejith': ['Travis head', 'Ishan Kishan', 'Riyan Parag', 'Shreyas Iyer', 'Badoni', 'Himmat singh', 'Manish Pandey', 'Rahane', 'Sai Sudarshan', 'Vishnu Vinod', 'Sarfaraz khan', 'Gaikwad', 'Ramakrishna Ghosh', 'Marsh', 'Krunal Pandya', 'Venkatesh Iyer', 'Unadkat', 'Suyash Sharma', 'Sandeep sharma', 'Arshdeep', 'Boult'],
    'Nagle': ['Klaasen', 'Kohli', 'SKY', 'Rinku Singh', 'KL Rahul', 'Samson', 'Green', 'Tilak verma', 'Marco Jansen', 'Nitish Rana', 'Varun', 'Ngidi', 'Holder', 'Starc', 'Josh Inglis', 'Ramandeep singh']
}

HISTORY_FILE = 'squad_history.json'

def load_data():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {m: {"squad": [], "captain": ""} for m in MEMBER_POOLS.keys()}

def save_data(data):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(data, f)

# --- 2. APP INTERFACE ---
st.title("🏆 Inner Circle IPL 2026")

user = st.sidebar.selectbox("Login as:", list(MEMBER_POOLS.keys()))
data = load_data()

# Lock logic (Sat 7PM)
now = datetime.datetime.now(IST)
# Saturday = 5. Lock if Sat >= 19:00 OR if Sun-Fri
# is_locked = (now.weekday() == 5 and now.hour >= 19) or (now.weekday() in [6,0,1,2,3,4])
is_locked = False
if is_locked:
    st.sidebar.error("🔒 SQUAD LOCKED")
    st.subheader(f"Active XI: {user}")
    current_squad = data.get(user, {}).get("squad", [])
    current_cap = data.get(user, {}).get("captain", "")
    
    if not current_squad:
        st.warning("No squad found. Please contact admin.")
    else:
        for p in current_squad:
            label = f"{p} ⭐ (C)" if p == current_cap else p
            st.info(label)
else:
    st.sidebar.success("🔓 SQUAD OPEN")
    st.subheader(f"Select your 11 - {user}")
    
    selected = []
    # Using a list of checkboxes
    pool = MEMBER_POOLS[user]
    for p in pool:
        # Pre-check if already in saved data
        if st.checkbox(p, key=p, value=(p in data[user]["squad"])):
            selected.append(p)
    
    st.divider()
    st.write(f"Selected: **{len(selected)} / 11**")
    
    if len(selected) > 0:
        cap = st.selectbox("Choose Captain (2x Pts)", selected)
        if st.button("Save My Team"):
            if len(selected) == 11:
                data[user] = {"squad": selected, "captain": cap}
                save_data(data)
                st.success("Success! Your team is saved.")
                st.balloons()
            else:
                st.error("You must pick exactly 11 players!")
    
# --- ADD THIS TO TAB 2 (Leaderboard) ---
with tab2:
    st.header("🏆 League Leaderboard")
    
    # Load the latest saved data
    all_teams = load_data()
    
    # Create a list to store the scores
    leaderboard_data = []
    
    for member_name, team_info in all_teams.items():
        squad = team_info.get("squad", [])
        captain = team_info.get("captain", "Not Set")
        
        # Placeholder: In a live match, we would pull real points here
        points = 0 
        
        leaderboard_data.append({
            "Member": member_name,
            "Total Points": points,
            "Captain": captain,
            "Squad Size": len(squad)
        })
    
    # Display the Table
    df = pd.DataFrame(leaderboard_data).sort_values(by="Total Points", ascending=False)
    st.table(df)

    # --- SQUAD VIEW SECTION ---
    st.divider()
    st.subheader("🔍 Member Squads")
    view_user = st.selectbox("View Squad For:", list(MEMBER_POOLS.keys()), key="view_squad")
    
    user_squad = all_teams.get(view_user, {}).get("squad", [])
    user_cap = all_teams.get(view_user, {}).get("captain", "")
    
    if user_squad:
        st.write(f"**{view_user}'s Active XI:**")
        cols = st.columns(2)
        for i, player in enumerate(user_squad):
            with cols[i % 2]:
                label = f"⭐ {player} (C)" if player == user_cap else player
                st.info(label)
    else:
        st.warning(f"{view_user} hasn't submitted a team yet!")
                       
