import streamlit as st
import pandas as pd
import json
import datetime
import pytz
import os

# --- 1. CONFIGURATION & TIMEZONE ---
IST = pytz.timezone('Asia/Kolkata')
LOCK_DAY = 5 # Saturday (0=Mon, 6=Sun)
LOCK_HOUR = 19 # 7:00 PM

# --- 2. AUCTION DATA (Extracted from your Excel) ---
MEMBER_POOLS = {
    'Kazim': ['Rajat Patidar', 'Padikkal', 'Hetmyer', 'Dhruv Jurel', 'Suryavanshi', 'Priyansh Arya', 'Ryan Rickelton', 'Markram', 'Raghuvanshi', 'Shahrukh Khan', 'Nitish Rana', 'Prashant Veer', 'Anshul Kambhoj', 'Axar Patel', 'Guldakesh Motie', 'Will Jacks', 'Stoinis', 'Shashank Singh', 'Nitish Kumar Reddy', 'Pat Cummins', 'Duffy', 'Hazlewood'],
    'Adi': ['Phil salt', 'Yashasvi Jaiswal', 'Prabhsimran', 'Pooran', 'Seifert', 'Gill', 'Ayush Mhatre', 'Ashutosh Sharma', 'Tewatia', 'Bumrah', 'Jadeja', 'Abhishek sharma', 'Harshal patel', 'Archer', 'Chahal', 'Ghazanfar', 'Digvesh', 'Prasidh', 'Umran Malik', 'Vipraj nigam'],
    'Aatish': ['Tim David', 'Jitesh Sharma', 'Wadhera', 'de Kock', 'Sherfane Rutherford', 'Rohit Sharma', 'Rishabh Pant', 'Samad', 'Breetzke', 'Porel', 'Stubbs', 'Nissanka', 'MS Dhoni', 'Brevis', 'Dube', 'Rashid Khan', 'Narine', 'Shahbaz Ahmed', 'Hardik Pandya', 'Donovan', 'Bethell'],
    'Shreejith': ['Travis head', 'Ishan Kishan', 'Riyan Parag', 'Shreyas Iyer', 'Badoni', 'Himmat singh', 'Manish Pandey', 'Rahane', 'Sai Sudarshan', 'Vishnu Vinod', 'Sarfaraz khan', 'Gaikwad', 'Ramakrishna Ghosh', 'Marsh', 'Krunal Pandya', 'Venkatesh Iyer', 'Unadkat', 'Suyash Sharma', 'Sandeep sharma', 'Arshdeep', 'Boult'],
    'Nagle': ['Klaasen', 'Kohli', 'SKY', 'Rinku Singh', 'KL Rahul', 'Samson', 'Green', 'Tilak verma', 'Marco Jansen', 'Nitish Rana', 'Varun', 'Ngidi', 'Holder', 'Starc', 'Josh Inglis', 'Ramandeep singh']
}

# Mapping for UI colors
TEAM_COLORS = {
    'RCB': '#EC1C24', 'MI': '#004BA0', 'CSK': '#FFFF00', 'KKR': '#3A225D',
    'SRH': '#FF822A', 'DC': '#00008B', 'PBKS': '#ED1B24', 'RR': '#EA1B85',
    'GT': '#1B2133', 'LSG': '#0057E2', 'Neutral': '#475569'
}

# --- 3. DATABASE HELPER FUNCTIONS ---
HISTORY_FILE = 'squad_history.json'

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return {m: {"week": 0, "squad": [], "captain": None} for m in MEMBER_POOLS.keys()}

def save_history(data):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(data, f)

def is_locked():
    now = datetime.datetime.now(IST)
    # Locked if it's Saturday after 7PM, or Sun, Mon, Tue, Wed, Thu, Fri
    if now.weekday() == 5 and now.hour >= 19: return True
    if now.weekday() in [6, 0, 1, 2, 3, 4]: return True
    return False

def get_current_week():
    # IPL 2026 starts March 28 (Week 1)
    start_date = datetime.datetime(2026, 3, 28, tzinfo=IST)
    now = datetime.datetime.now(IST)
    delta = now - start_date
    return max(1, (delta.days // 7) + 1)

# --- 4. STREAMLIT UI ---
st.set_page_config(page_title="IPL 2026 Fantasy", page_icon="🏏", layout="centered")

# Custom CSS for Dark Mode and Styling
st.markdown("""
    <style>
    .stApp { background-color: #0f172a; color: white; }
    .player-card { background: #1e293b; padding: 10px; border-radius: 8px; margin: 5px 0; border-left: 5px solid #3b82f6; }
    .locked-badge { background: #ef4444; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    .open-badge { background: #22c55e; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    </style>
    """, unsafe_allow_value=True)

st.title("🏏 The Inner Circle: IPL 2026")

# Sidebar Login & Status
member = st.sidebar.selectbox("Select Member", list(MEMBER_POOLS.keys()))
week = get_current_week()
locked = is_locked()

if locked:
    st.sidebar.markdown('<span class="locked-badge">🔒 ROSTER LOCKED</span>', unsafe_allow_value=True)
else:
    st.sidebar.markdown('<span class="open-badge">🔓 ROSTER OPEN</span>', unsafe_allow_value=True)

st.sidebar.write(f"**Current Period:** Week {week}")
st.sidebar.write("Deadline: Sat 7:00 PM IST")

# Load Data
history = load_history()
user_data = history.get(member, {"week": 0, "squad": [], "captain": None})

tab1, tab2, tab3 = st.tabs(["📋 My Squad", "📊 Leaderboard", "⚙️ Rules"])

# --- TAB 1: SQUAD SELECTION ---
with tab1:
    st.header(f"Squad Selection - Week {week}")
    
    if locked:
        st.info("The transfer window is closed. Displaying your active XI for this week.")
        active_squad = user_data["squad"]
        cap = user_data["captain"]
        
        if not active_squad:
            st.warning("No squad submitted. Auto-Pilot looking for previous data...")
        else:
            for p in active_squad:
                suffix = " ⭐ (Captain - 2x)" if p == cap else ""
                st.markdown(f'<div class="player-card">{p}{suffix}</div>', unsafe_allow_value=True)
    else:
        # User is picking their team
        pool = MEMBER_POOLS[member]
        st.write("Select exactly 11 players from your auction pool:")
        
        # Pre-select last week's squad if available
        default_val = user_data["squad"]
        selected = []
        
        cols = st.columns(2)
        for i, player in enumerate(pool):
            with cols[i % 2]:
                if st.checkbox(player, key=f"check_{player}", value=(player in default_val)):
                    selected.append(player)
        
        st.divider()
        if len(selected) > 0:
            captain = st.selectbox("Assign your Captain (2x Points)", selected, 
                                  index=selected.index(user_data["captain"]) if user_data["captain"] in selected else 0)
        
        if st.button("Submit Squad"):
            if len(selected) != 11:
                st.error(f"Selection Error: You have selected {len(selected)} players. Please select exactly 11.")
            else:
                history[member] = {"week": week, "squad": selected, "captain": captain}
                save_history(history)
                st.success("Squad locked in successfully! Good luck this week.")
                st.balloons()

# --- TAB 2: LEADERBOARD ---
with tab2:
    st.header("Global Standings")
    # Mock data for demonstration - in production, this would be calculated via API scores
    standings = pd.DataFrame({
        'Member': ['Kazim', 'Adi', 'Aatish', 'Shreejith', 'Nagle'],
        'Weekly Pts': [0, 0, 0, 0, 0],
        'Total Pts': [0, 0, 0, 0, 0],
        'Captain': [history[m]['captain'] if history[m]['captain'] else "Not Set" for m in MEMBER_POOLS.keys()]
    }).sort_values(by='Total Pts', ascending=False)
    
    st.table(standings)
    st.caption("Points update daily at 11:30 PM IST after match completion.")

# --- TAB 3: SCORING RULES ---
with tab3:
    st.header("League Rules")
    st.markdown("""
    - **1 Run:** 1 Point
    - **1 Wicket:** 20 Points
    - **Catch/Runout/Stumping:** 5 Points
    - **Man of the Match:** 100 Points
    - **Captain Multiplier:** 2x Points for designated player.
    ---
    - **Lock Time:** Every Saturday @ 7:00 PM IST.
    - **Duration:** Team is locked for 7 days (Saturday to Friday).
    - **Auto-Pilot:** If you don't submit a team, your team from the previous week is carried forward automatically.
    """)

