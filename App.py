import streamlit as st
import pandas as pd
import json
import datetime
import pytz
import os

# --- 1. CONFIG & DATA ---
IST = pytz.timezone('Asia/Kolkata')

# SYNCED PLAYER POOLS (Verified against your Excel)
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

# --- 2. APP UI ---
st.set_page_config(page_title="Inner Circle IPL", layout="wide")
db = load_db()
week = "1" # Set manually for testing

st.title(f"🏆 Inner Circle IPL 2026")

# Navigation Tabs at the Top (Stable for Python 3.14)
tab1, tab2, tab3, tab4 = st.tabs(["📋 Selection", "📊 Leaderboard", "📜 History", "⚙️ Admin"])

# --- TAB 1: SELECTION ---
with tab1:
    user = st.selectbox("Select Your Name:", list(MEMBER_POOLS.keys()), key="user_sel")
    pool = MEMBER_POOLS[user]
    
    st.subheader(f"Week {week} Selection for {user}")
    
    # Pre-load saved team
    current_team = db["selections"].get(week, {}).get(user, {"squad": [], "cap": ""})
    
    selected = []
    cols = st.columns(2)
    for i, p in enumerate(pool):
        with cols[i % 2]:
            if st.checkbox(p, key=f"chk_{user}_{p}", value=(p in current_team["squad"])):
                selected.append(p)
    
    st.divider()
    st.write(f"Players Selected: **{len(selected)} / 11**")
    
    if len(selected) > 0:
        cap = st.selectbox("Choose Captain (2x):", selected)
        if st.button("Save Week " + week + " Squad"):
            if len(selected) == 11:
                if week not in db["selections"]: db["selections"][week] = {}
                db["selections"][week][user] = {"squad": selected, "cap": cap}
                save_db(db)
                st.success("Squad Locked!")
                st.balloons()
            else:
                st.error("Select exactly 11 players.")

# --- TAB 2: LEADERBOARD ---
with tab2:
    st.subheader(f"Week {week} Standings")
    lb = []
    for m in MEMBER_POOLS.keys():
        w_pts = 0
        m_data = db["selections"].get(week, {}).get(m, {"squad": [], "cap": ""})
        for p in m_data["squad"]:
            p_pts = sum(db["scores"].get(p, {}).values())
            w_pts += (p_pts * 2) if p == m_data["cap"] else p_pts
        
        lb.append({"Member": m, "Weekly Pts": w_pts, "Tournament Total": db["totals"][m] + w_pts})
    
    st.table(pd.DataFrame(lb).sort_values("Tournament Total", ascending=False))

# --- TAB 3: HISTORY ---
with tab3:
    st.subheader("Player Match Logs")
    all_scored_players = sorted(list(db["scores"].keys()))
    if all_scored_players:
        p_name = st.selectbox("View Player Points History:", all_scored_players)
        for match, pts in db["scores"].get(p_name, {}).items():
            st.write(f"🏏 {match}: **{pts} pts**")
    else:
        st.info("No match points recorded yet.")

# --- TAB 4: ADMIN ---
with tab4:
    st.subheader("Admin Scoring Panel")
    all_players = sorted([p for pool in MEMBER_POOLS.values() for p in pool])
    target = st.selectbox("Select Player:", all_players)
    match_id = st.text_input("Match Detail (e.g., Match 1 - RCB vs MI)")
    score = st.number_input("Points Scored:", step=1)
    
    if st.button("Add Match Score"):
        if target not in db["scores"]: db["scores"][target] = {}
        db["scores"][target][match_id] = score
        save_db(db)
        st.success(f"Added {score} pts to {target}")

    st.divider()
    if st.button("🏁 Finalize Week & Add to Totals"):
        for m in MEMBER_POOLS.keys():
            m_data = db["selections"].get(week, {}).get(m, {"squad": [], "cap": ""})
            w_pts = sum([(sum(db["scores"].get(p, {}).values()) * 2 if p == m_data["cap"] else sum(db["scores"].get(p, {}).values())) for p in m_data["squad"]])
            db["totals"][m] += w_pts
        
        db["scores"] = {} # Reset daily scores
        save_db(db)
        st.warning("Week finalized. Weekly scores added to totals and player scores reset.")
