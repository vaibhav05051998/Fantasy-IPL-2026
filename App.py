import streamlit as st
import pandas as pd
import json
import os

# --- 1. GLOBAL CONFIGURATION & STYLING ---
TEAM_STYLING = {
    'RCB': '#d11d26', 'MI': '#004ba0', 'CSK': '#fdb913', 'SRH': '#f26522',
    'RR': '#ea1a85', 'KKR': '#3a225d', 'GT': '#1b2133', 'LSG': '#0057e2',
    'DC': '#0078bc', 'PBKS': '#dd1f2d', 'IPL': '#000080'
}

ROLE_EMOJI = {'BAT': '🏏', 'BOWL': '🎳', 'WK': '🧤'}

SEASON_WEEKS = {
    "Week 1 (Mar 28 - Apr 03)": ["Match 01: RCB vs SRH", "Match 02: MI vs KKR", "Match 03: RR vs CSK", "Match 04: PBKS vs GT", "Match 05: LSG vs DC", "Match 06: KKR vs SRH", "Match 07: CSK vs PBKS"],
    "Week 2 (Apr 04 - Apr 10)": ["Match 08: DC vs MI", "Match 09: GT vs RR", "Match 10: SRH vs LSG", "Match 11: RCB vs CSK", "Match 12: KKR vs PBKS", "Match 13: RR vs MI", "Match 14: DC vs GT", "Match 15: KKR vs LSG"]
}

# --- 2. PLAYER DATA LOGIC ---
OVERSEAS_LIST = [
    'Shimron Hetmyer', 'Ryan Rickelton', 'Aiden Markram', 'Jos Buttler', 'David Miller', 
    'Ben Duckett', 'Gudakesh Motie', 'Will Jacks', 'Marcus Stoinis', 'Pat Cummins', 
    'Jacob Duffy', 'Josh Hazlewood', 'Noor Ahmad', 'Blessing Muzarabani', 'Lockie Ferguson',
    'Philip Salt', 'Nicholas Pooran', 'Tim Seifert', 'Cooper Connolly', 'Azmatullah Omarzai', 
    'Jofra Archer', 'Allah Ghazanfar', 'Tim David', 'Quinton de Kock', 'Sherfane Rutherford', 
    'Matthew Breetzke', 'Finn Allen', 'Tristan Stubbs', 'Pathum Nissanka', 'Dewald Brevis', 
    'Rashid Khan', 'Sunil Narine', 'Donovan Ferreira', 'Jacob Bethell', 'Romario Shepherd',
    'Travis Head', 'Mitchell Marsh', 'Trent Boult', 'Kagiso Rabada', 'Mitchell Santner',
    'Heinrich Klaasen', 'Cameron Green', 'Marco Jansen', 'Liam Livingstone', 'Lungi Ngidi', 
    'Jason Holder', 'Mitchell Starc'
]

WK_LIST = [
    'Dhruv Jurel', 'Ryan Rickelton', 'Jos Buttler', 'Ben Duckett', 'Philip Salt', 
    'Nicholas Pooran', 'Tim Seifert', 'Jitesh Sharma', 'Quinton de Kock', 'Rishabh Pant', 
    'Abishek Porel', 'Sanju Samson', 'KL Rahul', 'Heinrich Klaasen'
]

BOWLERS_LIST = [
    'Anshul Kambhoj', 'Gudakesh Motie', 'Pat Cummins', 'Jacob Duffy', 'Josh Hazlewood', 
    'Ravi Bishnoi', 'Avesh Khan', 'Ravi Sai Kishore', 'Noor Ahmad', 'Blessing Muzarabani', 
    'Lockie Ferguson', 'Harshal Patel', 'Jofra Archer', 'Yuzvendra Chahal', 'Allah Ghazanfar', 
    'Prasidh Krishna', 'Umran Malik', 'Yash Dayal', 'Deepak Chahar', 'Vaibhav Arora', 
    'Mohammed Siraj', 'Kuldeep Yadav', 'Khaleel Ahmed', 'Mukesh Choudhary', 'Rahul Chahar', 
    'Mayank Yadav', 'Harpreet Brar', 'Tushar Deshpande', 'Jaydev Unadkat', 'Suyash Sharma', 
    'Sandeep Sharma', 'Arshdeep Singh', 'Trent Boult', 'Mohammed Shami', 'Kagiso Rabada', 
    'Varun Chakaravarthy', 'Lungi Ngidi', 'Mitchell Starc', 'Bhuvi'
]

# --- 3. DATABASE ENGINE ---
DB_FILE = 'tournament_db.json'

def load_db():
    default_pools = {
        'Kazim': ['Rajat Patidar', 'Devdutt Padikkal', 'Shimron Hetmyer', 'Dhruv Jurel', 'Vaibhav Suryavanshi', 'Priyansh Arya', 'Ryan Rickelton', 'Aiden Markram', 'Angkrish Raghuvanshi', 'Jos Buttler', 'David Miller', 'Ben Duckett', 'Nitish Rana', 'Prashant Veer', 'Anshul Kambhoj', 'Axar Patel', 'Gudakesh Motie', 'Will Jacks', 'Marcus Stoinis', 'Shashank Singh', 'Nitish Kumar Reddy', 'Pat Cummins', 'Jacob Duffy', 'Josh Hazlewood', 'Ravi Bishnoi', 'Avesh Khan', 'Ravi Sai Kishore', 'Noor Ahmad', 'Blessing Muzarabani', 'Lockie Ferguson'],
        'Adi': ['Philip Salt', 'Yashasvi Jaiswal', 'Prabhsimran Singh', 'Nicholas Pooran', 'Tim Seifert', 'Shubman Gill', 'Ayush Mhatre', 'Ashutosh Sharma', 'Rahul Tewatia', 'Washington Sundar', 'Cooper Connolly', 'Azmatullah Omarzai', 'Ravindra Jadeja', 'Abhishek Sharma', 'Harshal Patel', 'Jofra Archer', 'Yuzvendra Chahal', 'Allah Ghazanfar', 'Digvesh Rathi', 'Prasidh Krishna', 'Umran Malik', 'Vipraj Nigam'],
        'Aatish': ['Tim David', 'Jitesh Sharma', 'Nehal Wadhera', 'Quinton de Kock', 'Sherfane Rutherford', 'Rohit Sharma', 'Rishabh Pant', 'Abdul Samad', 'Matthew Breetzke', 'Rahul Tripathi', 'Finn Allen', 'Shahrukh Khan', 'Tristan Stubbs', 'Pathum Nissanka', 'MS Dhoni', 'Dewald Brevis', 'Shivam Dube', 'Rashid Khan', 'Sunil Narine', 'Shahbaz Ahmed', 'Hardik Pandya', 'Donovan Ferreira', 'Jacob Bethell', 'Romario Shepherd', 'Yash Dayal', 'Deepak Chahar', 'Vaibhav Arora', 'Mohammed Siraj', 'Kuldeep Yadav', 'Khaleel Ahmed', 'Mukesh Choudhary', 'Rahul Chahar', 'Mayank Yadav', 'Harpreet Brar', 'Tushar Deshpande'],
        'Shreejith': ['Travis Head', 'Ishan Kishan', 'Riyan Parag', 'Shreyas Iyer', 'Ayush Badoni', 'Himmat Singh', 'Manish Pandey', 'Ajinkya Rahane', 'Sai Sudharsan', 'Prithvi Shaw', 'Karun Nair', 'Abishek Porel', 'Sarfaraz Khan', 'Ruturaj Gaikwad', 'Ramakrishna Ghosh', 'Mitchell Marsh', 'Krunal Pandya', 'Venkatesh Iyer', 'Jaydev Unadkat', 'Suyash Sharma', 'Sandeep Sharma', 'Arshdeep Singh', 'Trent Boult', 'Mohammed Shami', 'Kagiso Rabada', 'Mitchell Santner', 'Kartik Sharma'],
        'Nagle': ['Heinrich Klaasen', 'Virat Kohli', 'Suryakumar Yadav', 'Rinku Singh', 'KL Rahul', 'Sanju Samson', 'Cameron Green', 'Tilak Varma', 'Marco Jansen', 'Liam Livingstone', 'Bhuvneshwar Kumar', 'Jasprit Bumrah', 'Varun Chakaravarthy', 'Lungi Ngidi', 'Jason Holder', 'Mitchell Starc']
    }
    
    # Generate Player Master Metadata
    pm = {}
    for pool_list in default_pools.values():
        for name in pool_list:
            role = 'WK' if name in WK_LIST else ('BOWL' if name in BOWLERS_LIST else 'BAT')
            pm[name] = {'team': 'IPL', 'role': role, 'is_overseas': name in OVERSEAS_LIST}

    default = {"selections": {}, "scores": {}, "pools": default_pools, "player_master": pm}
    
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f:
                data = json.load(f)
                for k in default: 
                    if k not in data: data[k] = default[k]
                return data
        except: return default
    return default

def save_db(data):
    with open(DB_FILE, 'w') as f: json.dump(data, f)

# --- 4. APP UI ---
st.set_page_config(page_title="Inner Circle IPL 2026", layout="wide")
db = load_db()

st.sidebar.title("📅 Season Control")
current_week = st.sidebar.selectbox("Select Week", list(SEASON_WEEKS.keys()))

st.markdown("""
<style>
    .player-row { display: flex; align-items: center; padding: 5px; background: white; border-radius: 5px; margin-bottom: 3px; border: 1px solid #eee; }
    .jersey-circle { height: 12px; width: 12px; border-radius: 50%; margin-right: 10px; display: inline-block; }
    .lb-card { background: #f8fafc; padding: 12px; border-radius: 8px; border: 1px solid #e2e8f0; text-align: center; }
    .total-pts { color: #e11d48; font-size: 1.5rem; font-weight: 800; display: block; }
</style>
""", unsafe_allow_html=True)

st.title("🏆 Inner Circle IPL 2026")
t1, t2, t3 = st.tabs(["🏏 SQUAD SELECTION", "📊 STANDINGS", "🛡️ ADMIN"])

# --- TAB 1: SELECTION ---
with t1:
    user = st.selectbox("Select Manager", list(db["pools"].keys()))
    pool = db["pools"].get(user, [])
    saved = db["selections"].get(current_week, {}).get(user, {"squad": [], "cap": ""})
    
    cl, cr = st.columns([3, 1])
    selected, os_count = [], 0
    
    with cl:
        grid = st.columns(3)
        for i, p in enumerate(pool):
            p_info = db["player_master"].get(p, {'team': 'IPL', 'role': 'BAT', 'is_overseas': False})
            color = TEAM_STYLING.get(p_info.get('team', 'IPL'), '#ccc')
            os_tag = "✈️ " if p_info.get('is_overseas') else ""
            with grid[i % 3]:
                st.markdown(f'<div class="player-row"><span class="jersey-circle" style="background-color: {color}"></span><span>{os_tag}{ROLE_EMOJI.get(p_info["role"])} <b>{p}</b></span></div>', unsafe_allow_html=True)
                if st.checkbox(f"Pick {p}", key=f"sel_{user}_{p}", value=(p in saved["squad"]), label_visibility="collapsed"):
                    selected.append(p)
                    if p_info.get('is_overseas'): os_count += 1
    with cr:
        st.metric("Squad Size", f"{len(selected)}/11")
        st.metric("Overseas ✈️", f"{os_count}/4")
        if len(selected) == 11 and os_count <= 4:
            cap = st.selectbox("Choose Captain", selected, index=selected.index(saved["cap"]) if saved["cap"] in selected else 0)
            if st.button("🚀 LOCK SQUAD", use_container_width=True):
                if current_week not in db["selections"]: db["selections"][current_week] = {}
                db["selections"][current_week][user] = {"squad": selected, "cap": cap}
                save_db(db)
                st.success("Squad Locked!")
        elif os_count > 4: st.error("Max 4 Overseas Allowed!")

# --- TAB 2: STANDINGS ---
with t2:
    lb_list = []
    cols = st.columns(len(db["pools"]))
    for i, (m, m_pool) in enumerate(db["pools"].items()):
        w_pts, t_pts = 0, 0
        
        # Calculate scores for all weeks to prevent dropping total rank
        for wk, matches in SEASON_WEEKS.items():
            m_wk = db["selections"].get(wk, {}).get(m, {"squad": [], "cap": ""})
            week_pts = 0
            for p in m_wk["squad"]:
                p_sc = db["scores"].get(p, {})
                match_pts = sum([v for k, v in p_sc.items() if k in matches])
                week_pts += (match_pts * 2) if p == m_wk["cap"] else match_pts
            
            t_pts += week_pts
            if wk == current_week: w_pts = week_pts
            
        lb_list.append({"Manager": m, "Weekly": w_pts, "Total": t_pts})
        with cols[i]:
            st.markdown(f'<div class="lb-card"><b>{m}</b><br><small>Week: {w_pts}</small><span class="total-pts">{t_pts}</span></div>', unsafe_allow_html=True)
    
    st.divider()
    st.subheader("Leaderboard")
    st.dataframe(pd.DataFrame(lb_list).sort_values("Total", ascending=False), use_container_width=True)

# --- TAB 3: ADMIN ---
with t3:
    st.subheader("🏏 Match Scoring (Top Priority)")
    all_m = [m for sub in SEASON_WEEKS.values() for m in sub]
    sel_m = st.selectbox("Select Match to Score", all_m)
    
    # Score input for all players in current week squads
    active_players = set()
    for wk_d in db["selections"].get(current_week, {}).values():
        active_players.update(wk_d["squad"])
    
    if not active_players:
        st.info("No managers have locked squads for this week yet.")
    else:
        for p in sorted(active_players):
            with st.expander(f"Score {p}"):
                cur_sc = db["scores"].get(p, {}).get(sel_m, 0)
                val = st.number_input(f"Points in {sel_m}", 0, value=cur_sc, key=f"sc_{p}_{sel_m}")
                if st.button(f"Save {p}", key=f"btn_{p}"):
                    if p not in db["scores"]: db["scores"][p] = {}
                    db["scores"][p][sel_m] = val
                    save_db(db)
                    st.toast(f"Saved {p}!")

    st.divider()
    st.subheader("⚙️ Pool Management (Secondary)")
    with st.expander("Add or Remove Players from Pools"):
        target = st.selectbox("Manager to Edit", list(db["pools"].keys()))
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        new_p = col1.text_input("New Player Name")
        new_t = col2.selectbox("Team", list(TEAM_STYLING.keys()))
        new_r = col3.selectbox("Role", ["BAT", "BOWL", "WK"])
        new_o = col4.checkbox("Overseas? ✈️")
        
        if st.button("➕ Add Player"):
            if new_p:
                db["pools"][target].append(new_p)
                db["player_master"][new_p] = {"team": new_t, "role": new_r, "is_overseas": new_o}
                save_db(db)
                st.success(f"Added {new_p}")
                st.rerun()
        
        st.write("---")
        p_rem = st.selectbox("Select Player to Remove", [""] + db["pools"][target])
        if st.button("🗑️ Remove Player"):
            if p_rem in db["pools"][target]:
                db["pools"][target].remove(p_rem)
                save_db(db)
                st.warning(f"Removed {p_rem}")
                st.rerun()
