import streamlit as st
import pandas as pd
import json
import os

# --- 1. CONFIG & TEAM ASSIGNMENTS ---
# Assigning specific teams to players for smart filtering
TEAM_MAP = {
    'RCB': ['Virat Kohli', 'Rajat Patidar', 'Will Jacks', 'Yash Dayal', 'Mohammed Siraj', 'Cameron Green'],
    'MI': ['Rohit Sharma', 'Suryakumar Yadav', 'Hardik Pandya', 'Jasprit Bumrah', 'Ishan Kishan', 'Tim David', 'Nehal Wadhera'],
    'CSK': ['MS Dhoni', 'Ruturaj Gaikwad', 'Ravindra Jadeja', 'Shivam Dube', 'Deepak Chahar', 'Tushar Deshpande', 'Matheesha Pathirana'],
    'SRH': ['Travis Head', 'Abhishek Sharma', 'Heinrich Klaasen', 'Pat Cummins', 'Aiden Markram', 'Nitish Kumar Reddy', 'Bhuvneshwar Kumar'],
    'RR': ['Yashasvi Jaiswal', 'Sanju Samson', 'Jos Buttler', 'Riyan Parag', 'Dhruv Jurel', 'Yuzvendra Chahal', 'Trent Boult', 'Avesh Khan'],
    'KKR': ['Shreyas Iyer', 'Sunil Narine', 'Rinku Singh', 'Varun Chakaravarthy', 'Venkatesh Iyer', 'Phil Salt', 'Ramandeep Singh'],
    'GT': ['Shubman Gill', 'Rashid Khan', 'Sai Sudharsan', 'Rahul Tewatia', 'Mohammed Shami', 'Noor Ahmad'],
    'LSG': ['KL Rahul', 'Nicholas Pooran', 'Marcus Stoinis', 'Ravi Bishnoi', 'Quinton de Kock', 'Ayush Badoni'],
    'DC': ['Rishabh Pant', 'Axar Patel', 'Kuldeep Yadav', 'Jake Fraser-McGurk', 'Tristan Stubbs', 'Khaleel Ahmed'],
    'PBKS': ['Arshdeep Singh', 'Shashank Singh', 'Ashutosh Sharma', 'Liam Livingstone', 'Sam Curran', 'Jitesh Sharma']
}

# Mapping the "Sat-Fri" Week Logic
SEASON_WEEKS = {
    "Week 1 (Mar 28 - Apr 03)": {
        "Matches": ["RCB vs SRH", "MI vs KKR", "RR vs CSK", "PBKS vs GT", "LSG vs DC", "KKR vs SRH", "CSK vs PBKS"],
        "Schedule": {"RCB": 1, "SRH": 2, "MI": 1, "KKR": 2, "RR": 1, "CSK": 2, "PBKS": 2, "GT": 1, "LSG": 1, "DC": 1}
    },
    "Week 2 (Apr 04 - Apr 10)": {
        "Matches": ["DC vs MI", "GT vs RR", "SRH vs LSG", "RCB vs CSK", "KKR vs PBKS", "RR vs MI", "DC vs GT"],
        "Schedule": {"DC": 2, "MI": 2, "GT": 2, "RR": 2, "SRH": 1, "LSG": 1, "RCB": 1, "CSK": 1, "KKR": 1, "PBKS": 1}
    }
}

TEAM_COLORS = {'RCB': '#d11d26', 'MI': '#004ba0', 'CSK': '#fdb913', 'SRH': '#f26522', 'RR': '#ea1a85', 'KKR': '#3a225d', 'GT': '#1b2133', 'LSG': '#0057e2', 'DC': '#0078bc', 'PBKS': '#dd1f2d'}

# --- 2. DATABASE & HELPER FUNCTIONS ---
DB_FILE = 'tournament_db.json'

def get_player_team(name):
    for team, players in TEAM_MAP.items():
        if name in players: return team
    return 'IPL' # Default

def load_db():
    # Initial load logic (omitted for brevity, same as previous version)
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f: return json.load(f)
    return {"selections": {}, "scores": {}, "pools": {}, "player_master": {}}

db = load_db()

# --- 3. UI STYLING (Compact Grid) ---
st.set_page_config(page_title="Inner Circle IPL", layout="wide")
st.markdown("""
<style>
    .compact-card { padding: 8px; border: 1px solid #ddd; border-radius: 8px; margin-bottom: 5px; background: #fdfdfd; font-size: 13px; }
    .jersey-dot { height: 10px; width: 10px; border-radius: 50%; display: inline-block; margin-right: 5px; }
    .match-tag { background: #e2e8f0; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 4. APP LOGIC ---
st.sidebar.title("📅 Season Control")
sel_week_name = st.sidebar.selectbox("Select Week", list(SEASON_WEEKS.keys()))
week_data = SEASON_WEEKS[sel_week_name]

# Show Matches in Selected Week
st.sidebar.markdown("### Matches this Week")
for m in week_data["Matches"]:
    st.sidebar.markdown(f"• <span class='match-tag'>{m}</span>", unsafe_allow_html=True)

t1, t2, t3 = st.tabs(["🏏 SQUAD SELECTION", "📊 STANDINGS", "🛡️ ADMIN"])

with t1:
    user = st.selectbox("Select Manager", list(db["pools"].keys()))
    user_pool = db["pools"].get(user, [])
    
    # Compact Grid Layout
    cols = st.columns(4) # 4 columns to reduce scrolling
    selected = []
    
    for idx, p in enumerate(user_pool):
        p_team = get_player_team(p)
        p_info = db["player_master"].get(p, {})
        emoji = "🧤" if p_info.get('role') == 'WK' else ("🏏" if p_info.get('role') == 'BAT' else "⚾")
        os_tag = "✈️" if p_info.get('is_overseas') else ""
        
        with cols[idx % 4]:
            st.markdown(f'''<div class="compact-card"><span class="jersey-dot" style="background:{TEAM_COLORS.get(p_team, '#ccc')}"></span><b>{p}</b><br><small>{p_team} | {emoji} {os_tag}</small></div>''', unsafe_allow_html=True)
            if st.checkbox("Pick", key=f"sel_{p}", label_visibility="collapsed"):
                selected.append(p)

    # Locking logic (omitted for brevity)

with t3:
    st.subheader("🛡️ Scoring Dashboard")
    sel_match = st.selectbox("Select Match to Score", week_data["Matches"])
    
    # Smart Filtering: Show only players playing in the selected match
    playing_teams = sel_match.split(" vs ")
    eligible_players = [p for p in db["player_master"].keys() if get_player_team(p) in playing_teams]
    
    if not eligible_players:
        st.info("No players from this match are in any manager's pool.")
    else:
        for p in sorted(eligible_players):
            with st.expander(f"{p} ({get_player_team(p)})"):
                val = st.number_input(f"Points for {p}", 0, key=f"score_{p}")
                if st.button(f"Save {p}"):
                    # Save logic
                    st.toast(f"Saved {p}")

