import streamlit as st
import pandas as pd
import json
import datetime
import pytz
import os

# --- 1. CONFIG & DATA ---
IST = pytz.timezone('Asia/Kolkata')
LOCK_DAY = 5 # Saturday
LOCK_HOUR = 19 # 7:00 PM

# Strict Auction Pools (Locked per member)
MEMBER_POOLS = {
    'Kazim': ['Rajat Patidar', 'Devdutt Padikkal', 'Shimron Hetmyer', 'Dhruv Jurel', 'Vaibhav Suryavanshi', 'Priyansh Arya', 'Ryan Rickelton', 'Aiden Markram', 'Angkrish Raghuvanshi', 'Shahrukh Khan', 'Nitish Rana', 'Prashant Veer', 'Anshul Kambhoj', 'Axar Patel', 'Gudakesh Motie', 'Will Jacks', 'Marcus Stoinis', 'Shashank Singh', 'Nitish Kumar Reddy', 'Pat Cummins', 'Jacob Duffy', 'Josh Hazlewood'],
    'Adi': ['Philip Salt', 'Yashasvi Jaiswal', 'Prabhsimran Singh', 'Nicholas Pooran', 'Tim Seifert', 'Shubman Gill', 'Ayush Mhatre', 'Ashutosh Sharma', 'Rahul Tewatia', 'Jasprit Bumrah', 'Ravindra Jadeja', 'Abhishek Sharma', 'Harshal Patel', 'Jofra Archer', 'Yuzvendra Chahal', 'Allah Ghazanfar', 'Digvesh Rathi', 'Prasidh Krishna', 'Umran Malik', 'Vipraj Nigam'],
    'Aatish': ['Tim David', 'Jitesh Sharma', 'Nehal Wadhera', 'Quinton de Kock', 'Sherfane Rutherford', 'Rohit Sharma', 'Rishabh Pant', 'Abdul Samad', 'Matthew Breetzke', 'Abishek Porel', 'Tristan Stubbs', 'Pathum Nissanka', 'MS Dhoni', 'Dewald Brevis', 'Shivam Dube', 'Rashid Khan', 'Sunil Narine', 'Shahbaz Ahmed', 'Hardik Pandya', 'Donovan Ferreira', 'Jacob Bethell'],
    'Shreejith': ['Travis Head', 'Ishan Kishan', 'Riyan Parag', 'Shreyas Iyer', 'Ayush Badoni', 'Himmat Singh', 'Manish Pandey', 'Ajinkya Rahane', 'Sai Sudharsan', 'Vishnu Vinod', 'Sarfaraz Khan', 'Ruturaj Gaikwad', 'Ramakrishna Ghosh', 'Mitchell Marsh', 'Krunal Pandya', 'Venkatesh Iyer', 'Jaydev Unadkat', 'Suyash Sharma', 'Sandeep Sharma', 'Arshdeep Singh', 'Trent Boult'],
    'Nagle': ['Heinrich Klaasen', 'Virat Kohli', 'Suryakumar Yadav', 'Rinku Singh', 'KL Rahul', 'Sanju Samson', 'Cameron Green', 'Tilak Varma', 'Marco Jansen', 'Nitish Rana', 'Varun Chakaravarthy', 'Lungi Ngidi', 'Jason Holder', 'Mitchell Starc', 'Josh Inglis', 'Ramandeep Singh']
}

# Database Files
MASTER_DATA_FILE = 'master_tournament_data.json'

def get_week():
    # IPL Week 1 starts March 28
    start = datetime.datetime(2026, 3, 28, tzinfo=IST)
    now = datetime.datetime.now(IST)
    delta = now - start
    return max(1, (delta.days // 7) + 1)

def load_db():
    if os.path.exists(MASTER_DATA_FILE):
        with open(MASTER_DATA_FILE, 'r') as f: return json.load(f)
    return {
        "current_week": 1,
        "weekly_selections": {}, # "1": {"Kazim": {"squad": [], "cap": ""}}
        "player_scores": {},    # "Virat Kohli": {"Match 1": 50, "Match 2": 20}
        "cumulative_totals": {m: 0 for m in MEMBER_POOLS.keys()}
    }

def save_db(data):
    with open(MASTER_DATA_FILE, 'w') as f: json.dump(data, f)

# --- 2. APP LOGIC ---
st.set_page_config(page_title="Inner Circle Pro", layout="wide")
db = load_db()
week = str(get_week())
now = datetime.datetime.now(IST)
#is_locked = (now.weekday() == 5 and now.hour >= 19) or (now.weekday() in [6,0,1,2,3,4])
is_locked = False
st.title(f"🏆 Inner Circle: Week {week}")
page = st.sidebar.radio("Menu", ["Selection", "Live Standings", "History & Match Logs", "Admin Panel"])
user = st.sidebar.selectbox("User:", list(MEMBER_POOLS.keys()))

# --- PAGE: SELECTION ---
if page == "Selection":
    if is_locked:
        st.error("🔒 Window Closed for Week " + week)
        active = db["weekly_selections"].get(week, {}).get(user, {"squad": [], "cap": ""})
        for p in active["squad"]:
            st.info(f"⭐ {p} (C)" if p == active["cap"] else p)
    else:
        st.success("🔓 Window Open")
        pool = MEMBER_POOLS[user]
        # Auto-carryover logic: load last week's squad if current is empty
        last_week = str(int(week)-1)
        prev_squad = db["weekly_selections"].get(last_week, {}).get(user, {}).get("squad", [])
        
        selected = [p for p in pool if st.checkbox(p, value=(p in prev_squad))]
        if len(selected) > 0:
            cap = st.selectbox("Assign Captain", selected)
            if st.button("Save Squad"):
                if len(selected) == 11:
                    if week not in db["weekly_selections"]: db["weekly_selections"][week] = {}
                    db["weekly_selections"][week][user] = {"squad": selected, "cap": cap}
                    save_db(db)
                    st.success("Week " + week + " Squad Locked!")
                else: st.error("Select exactly 11.")

# --- PAGE: STANDINGS ---
elif page == "Live Standings":
    st.header(f"Live Leaderboard (Week {week})")
    rows = []
    for m in MEMBER_POOLS.keys():
        # Calculate Weekly Points
        w_pts = 0
        m_data = db["weekly_selections"].get(week, {}).get(m, {"squad": [], "cap": ""})
        for p in m_data["squad"]:
            p_match_data = db["player_scores"].get(p, {})
            # Only count points for current week's logic if needed, 
            # or sum all scores if they reset weekly in the admin panel.
            p_total = sum(p_match_data.values())
            w_pts += (p_total * 2) if p == m_data["cap"] else p_total
        
        rows.append({
            "Member": m, 
            "Weekly Points": w_pts, 
            "Tournament Total": db["cumulative_totals"][m] + w_pts
        })
    st.table(pd.DataFrame(rows).sort_values("Tournament Total", ascending=False))

# --- PAGE: HISTORY ---
elif page == "History & Match Logs":
    hist_week = st.selectbox("Select Past Week:", [str(i) for i in range(1, int(week)+1)])
    st.subheader(f"Data for Week {hist_week}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Squads Picked:**")
        view_m = st.selectbox("Member:", list(MEMBER_POOLS.keys()))
        h_data = db["weekly_selections"].get(hist_week, {}).get(view_m, {"squad": [], "cap": ""})
        for p in h_data["squad"]:
            st.write(f"- {p} (C)" if p == h_data["cap"] else f"- {p}")
            
    with col2:
        st.write("**Player Performance (Match-wise):**")
        all_players = sorted(list(db["player_scores"].keys()))
        if all_players:
            p_view = st.selectbox("Player:", all_players)
            matches = db["player_scores"].get(p_view, {})
            for m_id, pts in matches.items():
                st.write(f"🏏 {m_id}: **{pts} pts**")

# --- PAGE: ADMIN ---
elif page == "Admin Panel":
    st.header("Admin Scoring Console")
    all_p = sorted([p for pool in MEMBER_POOLS.values() for p in pool])
    p_target = st.selectbox("Player:", all_p)
    m_id = st.text_input("Match ID (e.g., Match 01 - RCB vs MI)")
    pts = st.number_input("Points in this Match:", step=1)
    
    if st.button("Add Score"):
        if p_target not in db["player_scores"]: db["player_scores"][p_target] = {}
        db["player_scores"][p_target][m_id] = pts
        save_db(db)
        st.success("Score added!")
    
    st.divider()
    if st.button("End Week & Finalize Cumulative"):
        # This adds current weekly points to cumulative and clears weekly scores
        for m in MEMBER_POOLS.keys():
            w_pts = 0
            m_data = db["weekly_selections"].get(week, {}).get(m, {"squad": [], "cap": ""})
            for p in m_data["squad"]:
                p_total = sum(db["player_scores"].get(p, {}).values())
                w_pts += (p_total * 2) if p == m_data["cap"] else p_total
            db["cumulative_totals"][m] += w_pts
        
        db["player_scores"] = {} # RESET player scores for next week
        save_db(db)
        st.warning(f"Week {week} Finalized. Cumulative points updated. Player scores reset to 0.")
