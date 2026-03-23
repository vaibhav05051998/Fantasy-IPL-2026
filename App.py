import streamlit as st
import pandas as pd
import json
import datetime
import pytz
import os

# --- 1. CONFIG & SYNCED PLAYER POOLS ---
IST = pytz.timezone('Asia/Kolkata')

# VERIFIED MAPPING: EXACTLY AS PER YOUR AUCTION DATA
MEMBER_POOLS = {
    'Kazim': ['Rajat Patidar', 'Devdutt Padikkal', 'Shimron Hetmyer', 'Dhruv Jurel', 'Vaibhav Suryavanshi', 'Priyansh Arya', 'Ryan Rickelton', 'Aiden Markram', 'Angkrish Raghuvanshi', 'Shahrukh Khan', 'Nitish Rana', 'Prashant Veer', 'Anshul Kambhoj', 'Axar Patel', 'Gudakesh Motie', 'Will Jacks', 'Marcus Stoinis', 'Shashank Singh', 'Nitish Kumar Reddy', 'Pat Cummins', 'Jacob Duffy', 'Josh Hazlewood'],
    'Adi': ['Philip Salt', 'Yashasvi Jaiswal', 'Prabhsimran Singh', 'Nicholas Pooran', 'Tim Seifert', 'Shubman Gill', 'Ayush Mhatre', 'Ashutosh Sharma', 'Rahul Tewatia', 'Jasprit Bumrah', 'Ravindra Jadeja', 'Abhishek Sharma', 'Harshal Patel', 'Jofra Archer', 'Yuzvendra Chahal', 'Allah Ghazanfar', 'Digvesh Rathi', 'Prasidh Krishna', 'Umran Malik', 'Vipraj Nigam'],
    'Aatish': ['Tim David', 'Jitesh Sharma', 'Nehal Wadhera', 'Quinton de Kock', 'Sherfane Rutherford', 'Rohit Sharma', 'Rishabh Pant', 'Abdul Samad', 'Matthew Breetzke', 'Abishek Porel', 'Tristan Stubbs', 'Pathum Nissanka', 'MS Dhoni', 'Dewald Brevis', 'Shivam Dube', 'Rashid Khan', 'Sunil Narine', 'Shahbaz Ahmed', 'Hardik Pandya', 'Donovan Ferreira', 'Jacob Bethell'],
    'Shreejith': ['Travis Head', 'Ishan Kishan', 'Riyan Parag', 'Shreyas Iyer', 'Ayush Badoni', 'Himmat Singh', 'Manish Pandey', 'Ajinkya Rahane', 'Sai Sudarsan', 'Vishnu Vinod', 'Sarfaraz Khan', 'Ruturaj Gaikwad', 'Ramakrishna Ghosh', 'Mitchell Marsh', 'Krunal Pandya', 'Venkatesh Iyer', 'Jaydev Unadkat', 'Suyash Sharma', 'Sandeep Sharma', 'Arshdeep Singh', 'Trent Boult'],
    'Nagle': ['Heinrich Klaasen', 'Virat Kohli', 'Suryakumar Yadav', 'Rinku Singh', 'KL Rahul', 'Sanju Samson', 'Cameron Green', 'Tilak Varma', 'Marco Jansen', 'Varun Chakaravarthy', 'Lungi Ngidi', 'Jason Holder', 'Mitchell Starc', 'Josh Inglis', 'Ramandeep Singh']
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

st.title("🏆 Inner Circle IPL 2026")

# Navigation
tab1, tab2, tab3, tab4 = st.tabs(["📋 Selection", "📊 Leaderboard", "📜 Match Logs", "⚙️ Admin"])

# --- TAB 1: SELECTION ---
with tab1:
    user = st.selectbox("Who is picking?", list(MEMBER_POOLS.keys()))
    pool = MEMBER_POOLS[user]
    
    # Lock Logic
    now = datetime.datetime.now(IST)
    is_locked = (now.weekday() == 5 and now.hour >= 19) or (now.weekday() in [6,0,1,2,3,4])
    if db.get("force_unlock", False): is_locked = False

    if is_locked:
        st.error(f"🔒 Roster Locked for Week {week}")
        user_team = db["selections"].get(week, {}).get(user, {"squad": [], "cap": ""})
        for p in user_team["squad"]:
            st.info(f"⭐ {p} (C)" if p == user_team["cap"] else p)
    else:
        st.success(f"🔓 Window Open for {user}")
        saved_squad = db["selections"].get(week, {}).get(user, {}).get("squad", [])
        selected = []
        cols = st.columns(2)
        for i, p in enumerate(pool):
            with cols[i % 2]:
                if st.checkbox(p, key=f"sel_{user}_{p}", value=(p in saved_squad)):
                    selected.append(p)
        
        st.write(f"Count: **{len(selected)} / 11**")
        if len(selected) > 0:
            cap = st.selectbox("Captain (2x):", selected, index=0)
            if st.button("Submit Squad"):
                if len(selected) == 11:
                    if week not in db["selections"]: db["selections"][week] = {}
                    db["selections"][week][user] = {"squad": selected, "cap": cap}
                    save_db(db)
                    st.success("Squad Saved Successfully!")
                    st.balloons()
                else:
                    st.error("Select exactly 11 players.")

# --- TAB 2: LEADERBOARD ---
with tab2:
    st.subheader(f"Week {week} Standings")
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
    st.subheader("Player Performance History")
    all_scored = sorted(list(db["scores"].keys()))
    if all_scored:
        p_query = st.selectbox("Search Player:", all_scored)
        for m, s in db["scores"].get(p_query, {}).items():
            st.write(f"🔹 {m}: **{s} pts**")
    else:
        st.info("No match points recorded yet.")

# --- TAB 4: ADMIN ---
with tab4:
    st.header("Admin Control Center")
    
    # 1. Scoring
    st.subheader("Add Match Scores")
    all_players = sorted([p for pool in MEMBER_POOLS.values() for p in pool])
    target = st.selectbox("Player:", all_players)
    match_tag = st.text_input("Match Details:", value="IPL 2026 - Match")
    pts = st.number_input("Points Scored:", step=1)
    if st.button("Push Points"):
        if target not in db["scores"]: db["scores"][target] = {}
        db["scores"][target][match_tag] = pts
        save_db(db)
        st.success("Points Added!")

    st.divider()
    
    # 2. End Week Logic
    st.subheader("Week Management")
    if st.button("Finalize Week & Reset Daily Scores"):
        for m in MEMBER_POOLS.keys():
            m_data = db["selections"].get(week, {}).get(m, {"squad": [], "cap": ""})
            w_pts = sum([(sum(db["scores"].get(p, {}).values()) * 2 if p == m_data["cap"] else sum(db["scores"].get(p, {}).values())) for p in m_data["squad"]])
            db["totals"][m] += w_pts
        db["scores"] = {} 
        save_db(db)
        st.warning("All points moved to Total. Daily reset done.")

    # 3. Force Unlock
    unlock_status = db.get("force_unlock", False)
    if st.button("Toggle Force Unlock (Current: " + str(unlock_status) + ")"):
        db["force_unlock"] = not unlock_status
        save_db(db)
        st.rerun()
        
