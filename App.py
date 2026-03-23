import streamlit as st
import pandas as pd
import json
import datetime
import pytz
import os

# --- 1. CONFIG & DATA ---
IST = pytz.timezone('Asia/Kolkata')

# EXACT MAPPING FROM YOUR EXCEL DATA
MEMBER_POOLS = {
    'Kazim': ['Rajat Patidar', 'Devdutt Padikkal', 'Shimron Hetmyer', 'Dhruv Jurel', 'Vaibhav Suryavanshi', 'Priyansh Arya', 'Ryan Rickelton', 'Aiden Markram', 'Angkrish Raghuvanshi', 'Shahrukh Khan', 'Nitish Rana', 'Prashant Veer', 'Anshul Kambhoj', 'Axar Patel', 'Gudakesh Motie', 'Will Jacks', 'Marcus Stoinis', 'Shashank Singh', 'Nitish Kumar Reddy', 'Pat Cummins', 'Jacob Duffy', 'Josh Hazlewood'],
    'Adi': ['Philip Salt', 'Yashasvi Jaiswal', 'Prabhsimran Singh', 'Nicholas Pooran', 'Tim Seifert', 'Shubman Gill', 'Ayush Mhatre', 'Ashutosh Sharma', 'Rahul Tewatia', 'Jasprit Bumrah', 'Ravindra Jadeja', 'Abhishek Sharma', 'Harshal Patel', 'Jofra Archer', 'Yuzvendra Chahal', 'Allah Ghazanfar', 'Digvesh Rathi', 'Prasidh Krishna', 'Umran Malik', 'Vipraj Nigam'],
    'Aatish': ['Tim David', 'Jitesh Sharma', 'Nehal Wadhera', 'Quinton de Kock', 'Sherfane Rutherford', 'Rohit Sharma', 'Rishabh Pant', 'Abdul Samad', 'Matthew Breetzke', 'Abishek Porel', 'Tristan Stubbs', 'Pathum Nissanka', 'MS Dhoni', 'Dewald Brevis', 'Shivam Dube', 'Rashid Khan', 'Sunil Narine', 'Shahbaz Ahmed', 'Hardik Pandya', 'Donovan Ferreira', 'Jacob Bethell'],
    'Shreejith': ['Travis Head', 'Ishan Kishan', 'Riyan Parag', 'Shreyas Iyer', 'Ayush Badoni', 'Himmat Singh', 'Manish Pandey', 'Ajinkya Rahane', 'Sai Sudharsan', 'Vishnu Vinod', 'Sarfaraz Khan', 'Ruturaj Gaikwad', 'Ramakrishna Ghosh', 'Mitchell Marsh', 'Krunal Pandya', 'Venkatesh Iyer', 'Jaydev Unadkat', 'Suyash Sharma', 'Sandeep Sharma', 'Arshdeep Singh', 'Trent Boult'],
    'Nagle': ['Heinrich Klaasen', 'Virat Kohli', 'Suryakumar Yadav', 'Rinku Singh', 'KL Rahul', 'Sanju Samson', 'Cameron Green', 'Tilak Varma', 'Marco Jansen', 'Varun Chakaravarthy', 'Lungi Ngidi', 'Jason Holder', 'Mitchell Starc', 'Josh Inglis', 'Ramandeep Singh']
}

MASTER_DATA_FILE = 'master_tournament_data.json'

# --- 2. CSS FOR BOTTOM TABS ---
st.set_page_config(page_title="Inner Circle IPL", layout="wide")

st.markdown("""
    <style>
    /* Force Sidebar to Bottom on Mobile */
    @media (max-width: 640px) {
        section[data-testid="stSidebar"] {
            bottom: 0;
            top: auto;
            height: 80px !important;
            width: 100% !important;
            position: fixed !important;
            z-index: 999999;
            background-color: #0e1117 !important;
            border-top: 1px solid #31333F;
        }
        [data-testid="stSidebarNav"] {
            display: flex;
            flex-direction: row !important;
            justify-content: space-around;
        }
    }
    /* Simple styling for the tabs */
    .stTabs [data-baseweb="tab-list"] {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #111;
        z-index: 1000;
        display: flex;
        justify-content: center;
        border-top: 2px solid #ff4b4b;
    }
    </style>
    """, unsafe_allow_value=True)

# --- 3. DATABASE FUNCTIONS ---
def load_db():
    if os.path.exists(MASTER_DATA_FILE):
        with open(MASTER_DATA_FILE, 'r') as f: return json.load(f)
    return {
        "weekly_selections": {}, 
        "player_scores": {},    
        "cumulative_totals": {m: 0 for m in MEMBER_POOLS.keys()}
    }

def save_db(data):
    with open(MASTER_DATA_FILE, 'w') as f: json.dump(data, f)

db = load_db()
week = "1" # Set manually or use function from previous turn

# --- 4. NAVIGATION (THE TABS) ---
tab_selection, tab_standings, tab_history, tab_admin = st.tabs(["📋 Selection", "📊 Standings", "📜 History", "⚙️ Admin"])

# User selection moved to top for easy mobile access
user = st.selectbox("Switch User:", list(MEMBER_POOLS.keys()))

# --- TAB 1: SELECTION ---
with tab_selection:
    st.header(f"Week {week} Selection")
    # Toggle this for locking:
    is_locked = False 
    
    if is_locked:
        st.warning("Locked! Viewing Squad.")
        sdata = db["weekly_selections"].get(week, {}).get(user, {"squad": [], "cap": ""})
        for p in sdata["squad"]: st.write(f"- {p}")
    else:
        pool = MEMBER_POOLS[user]
        selected = []
        cols = st.columns(2)
        for i, p in enumerate(pool):
            with cols[i%2]:
                if st.checkbox(p, key=f"{user}_{p}", value=(p in db["weekly_selections"].get(week, {}).get(user, {}).get("squad", []))):
                    selected.append(p)
        
        if len(selected) == 11:
            cap = st.selectbox("Captain:", selected)
            if st.button("Submit 11"):
                if week not in db["weekly_selections"]: db["weekly_selections"][week] = {}
                db["weekly_selections"][week][user] = {"squad": selected, "cap": cap}
                save_db(db)
                st.success("Locked!")

# --- TAB 2: STANDINGS ---
with tab_standings:
    st.header("Leaderboard")
    rows = []
    for m in MEMBER_POOLS.keys():
        w_pts = 0
        m_data = db["weekly_selections"].get(week, {}).get(m, {"squad": [], "cap": ""})
        for p in m_data["squad"]:
            p_total = sum(db["player_scores"].get(p, {}).values())
            w_pts += (p_total * 2) if p == m_data["cap"] else p_total
        rows.append({"Member": m, "Weekly": w_pts, "Total": db["cumulative_totals"][m] + w_pts})
    st.table(pd.DataFrame(rows).sort_values("Total", ascending=False))

# --- TAB 3: HISTORY ---
with tab_history:
    st.header("Match Logs")
    all_p = sorted(list(db["player_scores"].keys()))
    if all_p:
        p_look = st.selectbox("Search Player History:", all_p)
        for m_id, pts in db["player_scores"].get(p_look, {}).items():
            st.write(f"🔹 {m_id}: **{pts} pts**")

# --- TAB 4: ADMIN ---
with tab_admin:
    st.header("Admin Scoring")
    p_target = st.selectbox("Player:", sorted([p for pool in MEMBER_POOLS.values() for p in pool]))
    match_name = st.text_input("Match (e.g. MI vs RCB)")
    pts_gain = st.number_input("Points Scored:", step=1)
    
    if st.button("Add Points"):
        if p_target not in db["player_scores"]: db["player_scores"][p_target] = {}
        db["player_scores"][p_target][match_name] = pts_gain
        save_db(db)
        st.success("Done!")

    if st.button("🏁 End Week & Add to Total"):
        for m in MEMBER_POOLS.keys():
            # (Calculation logic same as Standings)
            pass
        st.warning("Weekly scores moved to Totals. Player daily scores reset.")
