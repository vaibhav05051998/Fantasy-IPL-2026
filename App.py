import streamlit as st
import pandas as pd
import json
import datetime
import pytz
import os

# --- 1. CONFIG & ROLE-TAGGED PLAYER POOLS ---
IST = pytz.timezone('Asia/Kolkata')

# Players tagged as (BAT), (BOWL), or (WK)
MEMBER_POOLS = {
    'Kazim': [
        ('Rajat Patidar', 'BAT'), ('Devdutt Padikkal', 'BAT'), ('Shimron Hetmyer', 'BAT'), 
        ('Dhruv Jurel', 'WK'), ('Vaibhav Suryavanshi', 'BAT'), ('Priyansh Arya', 'BAT'), 
        ('Ryan Rickelton', 'WK'), ('Aiden Markram', 'BAT'), ('Angkrish Raghuvanshi', 'BAT'), 
        ('Shahrukh Khan', 'BAT'), ('Nitish Rana', 'BAT'), ('Prashant Veer', 'BOWL'), 
        ('Anshul Kambhoj', 'BOWL'), ('Axar Patel', 'BOWL'), ('Gudakesh Motie', 'BOWL'), 
        ('Will Jacks', 'BAT'), ('Marcus Stoinis', 'BAT'), ('Shashank Singh', 'BAT'), 
        ('Nitish Kumar Reddy', 'BOWL'), ('Pat Cummins', 'BOWL'), ('Jacob Duffy', 'BOWL'), 
        ('Josh Hazlewood', 'BOWL')
    ],
    'Adi': [
        ('Philip Salt', 'WK'), ('Yashasvi Jaiswal', 'BAT'), ('Prabhsimran Singh', 'WK'), 
        ('Nicholas Pooran', 'WK'), ('Tim Seifert', 'WK'), ('Shubman Gill', 'BAT'), 
        ('Ayush Mhatre', 'BAT'), ('Ashutosh Sharma', 'BAT'), ('Rahul Tewatia', 'BOWL'), 
        ('Jasprit Bumrah', 'BOWL'), ('Ravindra Jadeja', 'BOWL'), ('Abhishek Sharma', 'BAT'), 
        ('Harshal Patel', 'BOWL'), ('Jofra Archer', 'BOWL'), ('Yuzvendra Chahal', 'BOWL'), 
        ('Allah Ghazanfar', 'BOWL'), ('Digvesh Rathi', 'BOWL'), ('Prasidh Krishna', 'BOWL'), 
        ('Umran Malik', 'BOWL'), ('Vipraj Nigam', 'BOWL')
    ],
    'Aatish': [
        ('Tim David', 'BAT'), ('Jitesh Sharma', 'WK'), ('Nehal Wadhera', 'BAT'), 
        ('Quinton de Kock', 'WK'), ('Sherfane Rutherford', 'BAT'), ('Rohit Sharma', 'BAT'), 
        ('Rishabh Pant', 'WK'), ('Abdul Samad', 'BAT'), ('Matthew Breetzke', 'BAT'), 
        ('Abishek Porel', 'WK'), ('Tristan Stubbs', 'WK'), ('Pathum Nissanka', 'BAT'), 
        ('MS Dhoni', 'WK'), ('Dewald Brevis', 'BAT'), ('Shivam Dube', 'BAT'), 
        ('Rashid Khan', 'BOWL'), ('Sunil Narine', 'BOWL'), ('Shahbaz Ahmed', 'BOWL'), 
        ('Hardik Pandya', 'BAT'), ('Donovan Ferreira', 'WK'), ('Jacob Bethell', 'BOWL')
    ],
    'Shreejith': [
        ('Travis Head', 'BAT'), ('Ishan Kishan', 'WK'), ('Riyan Parag', 'BAT'), 
        ('Shreyas Iyer', 'BAT'), ('Ayush Badoni', 'BAT'), ('Himmat Singh', 'BAT'), 
        ('Manish Pandey', 'BAT'), ('Ajinkya Rahane', 'BAT'), ('Sai Sudharsan', 'BAT'), 
        ('Vishnu Vinod', 'WK'), ('Sarfaraz Khan', 'BAT'), ('Ruturaj Gaikwad', 'BAT'), 
        ('Ramakrishna Ghosh', 'BOWL'), ('Mitchell Marsh', 'BAT'), ('Krunal Pandya', 'BOWL'), 
        ('Venkatesh Iyer', 'BAT'), ('Jaydev Unadkat', 'BOWL'), ('Suyash Sharma', 'BOWL'), 
        ('Sandeep Sharma', 'BOWL'), ('Arshdeep Singh', 'BOWL'), ('Trent Boult', 'BOWL')
    ],
    'Nagle': [
        ('Heinrich Klaasen', 'WK'), ('Virat Kohli', 'BAT'), ('Suryakumar Yadav', 'BAT'), 
        ('Rinku Singh', 'BAT'), ('KL Rahul', 'WK'), ('Sanju Samson', 'WK'), 
        ('Cameron Green', 'BAT'), ('Tilak Varma', 'BAT'), ('Marco Jansen', 'BOWL'), 
        ('Varun Chakaravarthy', 'BOWL'), ('Lungi Ngidi', 'BOWL'), ('Jason Holder', 'BOWL'), 
        ('Mitchell Starc', 'BOWL'), ('Josh Inglis', 'WK'), ('Ramandeep Singh', 'BAT')
    ]
}

DB_FILE = 'tournament_db.json'

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f: return json.load(f)
        except: pass
    return {"selections": {}, "scores": {}, "totals": {m: 0 for m in MEMBER_POOLS.keys()}, "force_unlock": True}

def save_db(data):
    with open(DB_FILE, 'w') as f: json.dump(data, f)

# --- 2. APP UI ---
st.set_page_config(page_title="Inner Circle IPL 2026", layout="wide")
db = load_db()
week = "1" 

st.title("🏏 Inner Circle IPL 2026")
tab1, tab2, tab3, tab4 = st.tabs(["📋 Selection", "📊 Leaderboard", "📜 Match Logs", "⚙️ Admin"])

# --- TAB 1: SELECTION ---
with tab1:
    user = st.selectbox("Select User:", list(MEMBER_POOLS.keys()))
    pool = MEMBER_POOLS[user]
    
    db.get("force_unlock", False)
    # Selection is always open for this version unless manually toggled in Admin
    is_locked = not db.get("force_unlock", True)

    if is_locked:
        st.error(f"🔒 Roster Locked for Week {week}")
        user_team = db["selections"].get(week, {}).get(user, {"squad": [], "cap": ""})
        for p in user_team["squad"]: st.info(p)
    else:
        st.success(f"🔓 Selection Open. Rule: 1 WK, 5 BOWL, 5 BAT (Total 11)")
        saved_squad = db["selections"].get(week, {}).get(user, {}).get("squad", [])
        
        selected_names = []
        counts = {"BAT": 0, "BOWL": 0, "WK": 0}
        
        cols = st.columns(2)
        for i, (p_name, p_role) in enumerate(pool):
            with cols[i % 2]:
                if st.checkbox(f"{p_name} ({p_role})", key=f"sel_{user}_{p_name}", value=(p_name in saved_squad)):
                    selected_names.append(p_name)
                    counts[p_role] += 1
        
        st.divider()
        st.write(f"**Current Balance:** WK: {counts['WK']} | BOWL: {counts['BOWL']} | BAT: {counts['BAT']} (Total: {len(selected_names)})")
        
        if len(selected_names) > 0:
            cap = st.selectbox("Assign Captain (2x Pts):", selected_names)
            if st.button("Confirm & Save Squad"):
                # VALIDATION LOGIC
                if len(selected_names) != 11:
                    st.error("You must select exactly 11 players!")
                elif counts['WK'] < 1:
                    st.error("You need at least 1 Wicket Keeper!")
                elif counts['BOWL'] < 5:
                    st.error(f"You need 5 Bowlers! You only have {counts['BOWL']}.")
                else:
                    if week not in db["selections"]: db["selections"][week] = {}
                    db["selections"][week][user] = {"squad": selected_names, "cap": cap}
                    save_db(db)
                    st.success("Squad Validated and Saved!")
                    st.balloons()

# --- TAB 2: LEADERBOARD ---
with tab2:
    lb_data = []
    for m in MEMBER_POOLS.keys():
        w_pts = 0
        m_data = db["selections"].get(week, {}).get(m, {"squad": [], "cap": ""})
        for p in m_data["squad"]:
            p_pts = sum(db["scores"].get(p, {}).values())
            w_pts += (p_pts * 2) if p == m_data["cap"] else p_pts
        lb_data.append({"Member": m, "Weekly Pts": w_pts, "Tournament Total": db["totals"][m] + w_pts})
    st.table(pd.DataFrame(lb_data).sort_values("Tournament Total", ascending=False))

# --- TAB 3: MATCH LOGS ---
with tab3:
    all_scored = sorted(list(db["scores"].keys()))
    if all_scored:
        p_query = st.selectbox("Search Player:", all_scored)
        for m, s in db["scores"].get(p_query, {}).items():
            st.write(f"🔹 {m}: **{s} pts**")

# --- TAB 4: ADMIN ---
with tab4:
    st.subheader("Add Match Points")
    all_players = sorted([p[0] for pool in MEMBER_POOLS.values() for p in pool])
    target = st.selectbox("Player:", all_players)
    match_tag = st.text_input("Match Details:", value="Match 01")
    pts = st.number_input("Points Scored:", step=1)
    if st.button("Push Points"):
        if target not in db["scores"]: db["scores"][target] = {}
        db["scores"][target][match_tag] = pts
        save_db(db)
        st.success("Points Added!")
    
