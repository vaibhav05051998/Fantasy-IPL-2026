import streamlit as st
import pandas as pd
import json
import os

# --- 1. CONFIGURATION & TEAM COLORS ---
TEAM_COLORS = {
    'RCB': '#d11d26', 'MI': '#004ba0', 'CSK': '#fdb913', 'SRH': '#f26522',
    'RR': '#ea1a85', 'KKR': '#3a225d', 'GT': '#1b2133', 'LSG': '#0057e2',
    'DC': '#0078bc', 'PBKS': '#dd1f2d', 'IPL': '#000080'
}
ROLE_EMOJI = {'BAT': '🏏 BAT', 'BOWL': '⚾ BOWL', 'WK': '🧤 WK'}

# FULL SEASON CALENDAR (8 Weeks + Playoffs)
SEASON_WEEKS = {
    "Week 1 (Mar 28 - Apr 03)": {"M01": "RCB vs SRH", "M02": "MI vs KKR", "M03": "RR vs CSK", "M04": "PBKS vs GT", "M05": "LSG vs DC", "M06": "KKR vs SRH", "M07": "CSK vs PBKS"},
    "Week 2 (Apr 04 - Apr 10)": {"M08": "DC vs MI", "M09": "GT vs RR", "M10": "SRH vs LSG", "M11": "RCB vs CSK", "M12": "KKR vs PBKS", "M13": "RR vs MI", "M14": "DC vs GT"},
    "Week 3 (Apr 11 - Apr 17)": {"M15": "SRH vs RCB", "M16": "KKR vs MI", "M17": "CSK vs RR", "M18": "GT vs PBKS", "M19": "DC vs LSG", "M20": "SRH vs KKR", "M21": "PBKS vs CSK"},
    "Week 4 (Apr 18 - Apr 24)": {"M22": "MI vs DC", "M23": "RR vs GT", "M24": "LSG vs SRH", "M25": "CSK vs RCB", "M26": "PBKS vs KKR", "M27": "MI vs RR", "M28": "GT vs DC"},
    "Week 5 (Apr 25 - May 01)": {"M29": "LSG vs KKR", "M30": "RCB vs GT", "M31": "SRH vs RR", "M32": "DC vs CSK", "M33": "MI vs PBKS", "M34": "KKR vs RCB", "M35": "RR vs LSG"},
    "Week 6 (May 02 - May 08)": {"M36": "GT vs SRH", "M37": "CSK vs MI", "M38": "PBKS vs DC", "M39": "RCB vs LSG", "M40": "RR vs KKR", "M41": "SRH vs PBKS", "M42": "GT vs CSK"},
    "Week 7 (May 09 - May 15)": {"M43": "DC vs RCB", "M44": "LSG vs MI", "M45": "KKR vs GT", "M46": "CSK vs SRH", "M47": "PBKS vs RR", "M48": "MI vs LSG", "M49": "RCB vs DC"},
    "Week 8 (May 16 - May 22)": {"M50": "GT vs KKR", "M51": "SRH vs CSK", "M52": "RR vs PBKS", "M53": "DC vs RR", "M54": "KKR vs PBKS", "M55": "LSG vs GT", "M56": "MI vs RCB"},
    "Playoffs (May 23 - May 30)": {"SF1": "Qualifier 1", "SF2": "Eliminator", "SF3": "Qualifier 2", "FIN": "Grand Final"}
}

# --- 2. DATABASE ENGINE WITH FULL PLAYER POOLS ---
DB_FILE = 'tournament_db.json'

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r') as f: return json.load(f)
    
    # Pre-filled Master Data based on your provided list
    pm = {
        # KAZIM
        "Rajat Patidar": {"team": "RCB", "role": "BAT", "is_overseas": False}, "Devdutt Padikkal": {"team": "LSG", "role": "BAT", "is_overseas": False},
        "Shimron Hetmyer": {"team": "RR", "role": "BAT", "is_overseas": True}, "Dhruv Jurel": {"team": "RR", "role": "WK", "is_overseas": False},
        "Vaibhav Suryavanshi": {"team": "RR", "role": "BAT", "is_overseas": False}, "Priyansh Arya": {"team": "PBKS", "role": "BAT", "is_overseas": False},
        "Ryan Rickelton": {"team": "MI", "role": "WK", "is_overseas": True}, "Aiden Markram": {"team": "SRH", "role": "BAT", "is_overseas": True},
        "Angkrish Raghuvanshi": {"team": "KKR", "role": "BAT", "is_overseas": False}, "Jos Buttler": {"team": "SRH", "role": "WK", "is_overseas": True},
        "David Miller": {"team": "GT", "role": "BAT", "is_overseas": True}, "Ben Duckett": {"team": "LSG", "role": "WK", "is_overseas": True},
        "Nitish Rana": {"team": "KKR", "role": "BAT", "is_overseas": False}, "Prashant Veer": {"team": "SRH", "role": "BOWL", "is_overseas": False},
        "Anshul Kambhoj": {"team": "MI", "role": "BOWL", "is_overseas": False}, "Axar Patel": {"team": "DC", "role": "BOWL", "is_overseas": False},
        "Gudakesh Motie": {"team": "GT", "role": "BOWL", "is_overseas": True}, "Will Jacks": {"team": "RCB", "role": "BAT", "is_overseas": True},
        "Marcus Stoinis": {"team": "LSG", "role": "BAT", "is_overseas": True}, "Shashank Singh": {"team": "PBKS", "role": "BAT", "is_overseas": False},
        "Nitish Kumar Reddy": {"team": "SRH", "role": "BAT", "is_overseas": False}, "Pat Cummins": {"team": "SRH", "role": "BOWL", "is_overseas": True},
        "Jacob Duffy": {"team": "RCB", "role": "BOWL", "is_overseas": True}, "Josh Hazlewood": {"team": "RCB", "role": "BOWL", "is_overseas": True},
        "Ravi Bishnoi": {"team": "LSG", "role": "BOWL", "is_overseas": False}, "Avesh Khan": {"team": "RR", "role": "BOWL", "is_overseas": False},
        "Ravi Sai Kishore": {"team": "GT", "role": "BOWL", "is_overseas": False}, "Noor Ahmad": {"team": "GT", "role": "BOWL", "is_overseas": True},
        "Blessing Muzarabani": {"team": "PBKS", "role": "BOWL", "is_overseas": True}, "Lockie Ferguson": {"team": "RCB", "role": "BOWL", "is_overseas": True},
        
        # AMAN
        "Phil Salt": {"team": "KKR", "role": "WK", "is_overseas": True}, "Yashasvi Jaiswal": {"team": "RR", "role": "BAT", "is_overseas": False},
        "Prabhsimran Singh": {"team": "PBKS", "role": "WK", "is_overseas": False}, "Nicholas Pooran": {"team": "LSG", "role": "WK", "is_overseas": True},
        "Tim Seifert": {"team": "DC", "role": "WK", "is_overseas": True}, "Shubman Gill": {"team": "GT", "role": "BAT", "is_overseas": False},
        "Ayush Mhatre": {"team": "MI", "role": "BAT", "is_overseas": False}, "Ashutosh Sharma": {"team": "PBKS", "role": "BAT", "is_overseas": False},
        "Rahul Tewatia": {"team": "GT", "role": "BAT", "is_overseas": False}, "Washington Sundar": {"team": "SRH", "role": "BOWL", "is_overseas": False},
        "Cooper Connolly": {"team": "MI", "role": "BAT", "is_overseas": True}, "Azmatullah Omarzai": {"team": "GT", "role": "BOWL", "is_overseas": True},
        "Ravindra Jadeja": {"team": "CSK", "role": "BOWL", "is_overseas": False}, "Abhishek Sharma": {"team": "SRH", "role": "BAT", "is_overseas": False},
        "Harshal Patel": {"team": "PBKS", "role": "BOWL", "is_overseas": False}, "Jofra Archer": {"team": "RR", "role": "BOWL", "is_overseas": True},
        "Yuzvendra Chahal": {"team": "PBKS", "role": "BOWL", "is_overseas": False}, "AM Ghazanfar": {"team": "MI", "role": "BOWL", "is_overseas": True},
        "Digvesh Singh": {"team": "MI", "role": "BOWL", "is_overseas": False}, "Prasidh Krishna": {"team": "GT", "role": "BOWL", "is_overseas": False},
        "Umran Malik": {"team": "SRH", "role": "BOWL", "is_overseas": False}, "Vipraj Nigam": {"team": "RR", "role": "BOWL", "is_overseas": False},

        # AATISH
        "Tim David": {"team": "MI", "role": "BAT", "is_overseas": True}, "Jitesh Sharma": {"team": "PBKS", "role": "WK", "is_overseas": False},
        "Nehal Wadhera": {"team": "MI", "role": "BAT", "is_overseas": False}, "Quinton de Kock": {"team": "LSG", "role": "WK", "is_overseas": True},
        "Sherfane Rutherford": {"team": "KKR", "role": "BAT", "is_overseas": True}, "Rohit Sharma": {"team": "MI", "role": "BAT", "is_overseas": False},
        "Rishabh Pant": {"team": "LSG", "role": "WK", "is_overseas": False}, "Abdul Samad": {"team": "SRH", "role": "BAT", "is_overseas": False},
        "Matthew Breetzke": {"team": "LSG", "role": "BAT", "is_overseas": True}, "Rahul Tripathi": {"team": "SRH", "role": "BAT", "is_overseas": False},
        "Finn Allen": {"team": "RCB", "role": "WK", "is_overseas": True}, "Shahrukh Khan": {"team": "GT", "role": "BAT", "is_overseas": False},
        "Tristan Stubbs": {"team": "DC", "role": "WK", "is_overseas": True}, "Pathum Nissanka": {"team": "IPL", "role": "BAT", "is_overseas": True},
        "MS Dhoni": {"team": "CSK", "role": "WK", "is_overseas": False}, "Dewald Brevis": {"team": "MI", "role": "BAT", "is_overseas": True},
        "Shivam Dube": {"team": "CSK", "role": "BAT", "is_overseas": False}, "Rashid Khan": {"team": "GT", "role": "BOWL", "is_overseas": True},
        "Sunil Narine": {"team": "KKR", "role": "BOWL", "is_overseas": True}, "Shahbaz Ahmed": {"team": "SRH", "role": "BOWL", "is_overseas": False},
        "Hardik Pandya": {"team": "MI", "role": "BOWL", "is_overseas": False}, "Donovan Ferreira": {"team": "RR", "role": "WK", "is_overseas": True},
        "Jacob Bethell": {"team": "RCB", "role": "BAT", "is_overseas": True}, "Romario Shepherd": {"team": "MI", "role": "BOWL", "is_overseas": True},
        "Yash Dayal": {"team": "RCB", "role": "BOWL", "is_overseas": False}, "Deepak Chahar": {"team": "CSK", "role": "BOWL", "is_overseas": False},
        "Vaibhav Arora": {"team": "KKR", "role": "BOWL", "is_overseas": False}, "Mohammed Siraj": {"team": "GT", "role": "BOWL", "is_overseas": False},
        "Kuldeep Yadav": {"team": "DC", "role": "BOWL", "is_overseas": False}, "Khaleel Ahmed": {"team": "DC", "role": "BOWL", "is_overseas": False},
        "Mukesh Choudhary": {"team": "CSK", "role": "BOWL", "is_overseas": False}, "Rahul Chahar": {"team": "PBKS", "role": "BOWL", "is_overseas": False},
        "Mayank Yadav": {"team": "LSG", "role": "BOWL", "is_overseas": False}, "Harpreet Brar": {"team": "PBKS", "role": "BOWL", "is_overseas": False},
        "Tushar Deshpande": {"team": "RR", "role": "BOWL", "is_overseas": False},

        # SHRIJEET
        "Travis Head": {"team": "SRH", "role": "BAT", "is_overseas": True}, "Ishan Kishan": {"team": "SRH", "role": "WK", "is_overseas": False},
        "Riyan Parag": {"team": "RR", "role": "BAT", "is_overseas": False}, "Shreyas Iyer": {"team": "PBKS", "role": "BAT", "is_overseas": False},
        "Ayush Badoni": {"team": "LSG", "role": "BAT", "is_overseas": False}, "Himmat Singh": {"team": "IPL", "role": "BAT", "is_overseas": False},
        "Manish Pandey": {"team": "KKR", "role": "BAT", "is_overseas": False}, "Ajinkya Rahane": {"team": "CSK", "role": "BAT", "is_overseas": False},
        "Sai Sudharsan": {"team": "GT", "role": "BAT", "is_overseas": False}, "Prithvi Shaw": {"team": "DC", "role": "BAT", "is_overseas": False},
        "Karun Nair": {"team": "IPL", "role": "BAT", "is_overseas": False}, "Abishek Porel": {"team": "DC", "role": "WK", "is_overseas": False},
        "Sarfaraz Khan": {"team": "DC", "role": "BAT", "is_overseas": False}, "Ruturaj Gaikwad": {"team": "CSK", "role": "BAT", "is_overseas": False},
        "Ramakrishna Ghosh": {"team": "IPL", "role": "BOWL", "is_overseas": False}, "Mitchell Marsh": {"team": "DC", "role": "BAT", "is_overseas": True},
        "Krunal Pandya": {"team": "RCB", "role": "BOWL", "is_overseas": False}, "Venkatesh Iyer": {"team": "KKR", "role": "BAT", "is_overseas": False},
        "Jaydev Unadkat": {"team": "SRH", "role": "BOWL", "is_overseas": False}, "Suyash Sharma": {"team": "KKR", "role": "BOWL", "is_overseas": False},
        "Sandeep Sharma": {"team": "RR", "role": "BOWL", "is_overseas": False}, "Arshdeep Singh": {"team": "PBKS", "role": "BOWL", "is_overseas": False},
        "Trent Boult": {"team": "MI", "role": "BOWL", "is_overseas": True}, "Mohammed Shami": {"team": "SRH", "role": "BOWL", "is_overseas": False},
        "Kagiso Rabada": {"team": "GT", "role": "BOWL", "is_overseas": True}, "Mitchell Santner": {"team": "CSK", "role": "BOWL", "is_overseas": True},
        "Kartik Sharma": {"team": "IPL", "role": "BAT", "is_overseas": False},

        # NAGLE
        "Heinrich Klaasen": {"team": "SRH", "role": "WK", "is_overseas": True}, "Virat Kohli": {"team": "RCB", "role": "BAT", "is_overseas": False},
        "Suryakumar Yadav": {"team": "MI", "role": "BAT", "is_overseas": False}, "Rinku Singh": {"team": "KKR", "role": "BAT", "is_overseas": False},
        "KL Rahul": {"team": "DC", "role": "WK", "is_overseas": False}, "Sanju Samson": {"team": "RR", "role": "WK", "is_overseas": False},
        "Cameron Green": {"team": "RCB", "role": "BOWL", "is_overseas": True}, "Tilak Varma": {"team": "MI", "role": "BAT", "is_overseas": False},
        "Marco Jansen": {"team": "PBKS", "role": "BOWL", "is_overseas": True}, "Liam Livingstone": {"team": "RCB", "role": "BAT", "is_overseas": True},
        "Bhuvneshwar Kumar": {"team": "RCB", "role": "BOWL", "is_overseas": False}, "Jasprit Bumrah": {"team": "MI", "role": "BOWL", "is_overseas": False},
        "Varun Chakaravarthy": {"team": "KKR", "role": "BOWL", "is_overseas": False}, "Lungi Ngidi": {"team": "DC", "role": "BOWL", "is_overseas": True},
        "Jason Holder": {"team": "IPL", "role": "BOWL", "is_overseas": True}, "Mitchell Starc": {"team": "DC", "role": "BOWL", "is_overseas": True}
    }

    initial_pools = {
        "Kazim": ["Rajat Patidar", "Devdutt Padikkal", "Shimron Hetmyer", "Dhruv Jurel", "Vaibhav Suryavanshi", "Priyansh Arya", "Ryan Rickelton", "Aiden Markram", "Angkrish Raghuvanshi", "Jos Buttler", "David Miller", "Ben Duckett", "Nitish Rana", "Prashant Veer", "Anshul Kambhoj", "Axar Patel", "Gudakesh Motie", "Will Jacks", "Marcus Stoinis", "Shashank Singh", "Nitish Kumar Reddy", "Pat Cummins", "Jacob Duffy", "Josh Hazlewood", "Ravi Bishnoi", "Avesh Khan", "Ravi Sai Kishore", "Noor Ahmad", "Blessing Muzarabani", "Lockie Ferguson"],
        "Aman": ["Phil Salt", "Yashasvi Jaiswal", "Prabhsimran Singh", "Nicholas Pooran", "Tim Seifert", "Shubman Gill", "Ayush Mhatre", "Ashutosh Sharma", "Rahul Tewatia", "Washington Sundar", "Cooper Connolly", "Azmatullah Omarzai", "Ravindra Jadeja", "Abhishek Sharma", "Harshal Patel", "Jofra Archer", "Yuzvendra Chahal", "AM Ghazanfar", "Digvesh Singh", "Prasidh Krishna", "Umran Malik", "Vipraj Nigam"],
        "Aatish": ["Tim David", "Jitesh Sharma", "Nehal Wadhera", "Quinton de Kock", "Sherfane Rutherford", "Rohit Sharma", "Rishabh Pant", "Abdul Samad", "Matthew Breetzke", "Rahul Tripathi", "Finn Allen", "Shahrukh Khan", "Tristan Stubbs", "Pathum Nissanka", "MS Dhoni", "Dewald Brevis", "Shivam Dube", "Rashid Khan", "Sunil Narine", "Shahbaz Ahmed", "Hardik Pandya", "Donovan Ferreira", "Jacob Bethell", "Romario Shepherd", "Yash Dayal", "Deepak Chahar", "Vaibhav Arora", "Mohammed Siraj", "Kuldeep Yadav", "Khaleel Ahmed", "Mukesh Choudhary", "Rahul Chahar", "Mayank Yadav", "Harpreet Brar", "Tushar Deshpande"],
        "Shrijeet": ["Travis Head", "Ishan Kishan", "Riyan Parag", "Shreyas Iyer", "Ayush Badoni", "Himmat Singh", "Manish Pandey", "Ajinkya Rahane", "Sai Sudharsan", "Prithvi Shaw", "Karun Nair", "Abishek Porel", "Sarfaraz Khan", "Ruturaj Gaikwad", "Ramakrishna Ghosh", "Mitchell Marsh", "Krunal Pandya", "Venkatesh Iyer", "Jaydev Unadkat", "Suyash Sharma", "Sandeep Sharma", "Arshdeep Singh", "Trent Boult", "Mohammed Shami", "Kagiso Rabada", "Mitchell Santner", "Kartik Sharma"],
        "Nagle": ["Heinrich Klaasen", "Virat Kohli", "Suryakumar Yadav", "Rinku Singh", "KL Rahul", "Sanju Samson", "Cameron Green", "Tilak Varma", "Marco Jansen", "Liam Livingstone", "Bhuvneshwar Kumar", "Jasprit Bumrah", "Varun Chakaravarthy", "Lungi Ngidi", "Jason Holder", "Mitchell Starc"]
    }
    return {"selections": {}, "scores": {}, "pools": initial_pools, "player_master": pm}

def save_db(data):
    with open(DB_FILE, 'w') as f: json.dump(data, f)

db = load_db()

# --- 3. MOBILE UI STYLING ---
st.set_page_config(page_title="Inner Circle IPL", layout="centered")
st.markdown("""
<style>
    .mobile-matrix { border: 1px solid #e2e8f0; padding: 6px; border-radius: 6px; background: #fff; display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px; height: 52px; }
    .jersey-dot { height: 8px; width: 8px; border-radius: 50%; margin-right: 5px; }
    .role-label { font-size: 10px; color: #64748b; font-weight: 700; }
    .lb-card { background: #f8fafc; padding: 10px; border-radius: 8px; border: 1px solid #cbd5e1; text-align: center; margin-bottom: 10px; }
    .total-pts { color: #e11d48; font-size: 1.5rem; font-weight: 800; display: block; }
    .validation-badge { padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 4. SIDEBAR SCHEDULE ---
st.sidebar.title("🗓️ Season Schedule")
active_week = st.sidebar.selectbox("Select Week", list(SEASON_WEEKS.keys()))
week_matches = SEASON_WEEKS[active_week]
team_counts = {}
for m_text in week_matches.values():
    for t in m_text.split(" vs "): team_counts[t] = team_counts.get(t, 0) + 1
st.sidebar.markdown("### Team Activity")
for t, count in sorted(team_counts.items()):
    st.sidebar.write(f"**{t}:** {count} Matches")

# --- 5. MAIN NAVIGATION ---
t1, t2, t3 = st.tabs(["🏏 SQUAD", "📊 STANDINGS", "🛡️ ADMIN"])

# --- TAB 1: SQUAD (WITH SEARCH, FILTERS & VALIDATION) ---
with t1:
    user = st.selectbox("Manager Name", list(db["pools"].keys()), key="s_mgr")
    pool = db["pools"].get(user, [])
    saved = db["selections"].get(active_week, {}).get(user, {"squad": [], "cap": ""})
    
    # Search and Filter
    st.markdown("### Selection Filters")
    f1, f2 = st.columns([2, 1])
    search = f1.text_input("🔍 Search Name", placeholder="Type name...", label_visibility="collapsed")
    role = f2.selectbox("Role", ["All", "BAT", "BOWL", "WK"], label_visibility="collapsed")

    # Tracking Selection across filters
    if 'selected_dict' not in st.session_state: st.session_state.selected_dict = {}
    if user not in st.session_state.selected_dict: 
        st.session_state.selected_dict[user] = set(saved["squad"])

    selected_list = st.session_state.selected_dict[user]
    
    # Display Grid
    cols = st.columns(2)
    display_count = 0
    for p in sorted(pool):
        info = db["player_master"].get(p, {"team": "IPL", "role": "BAT", "is_overseas": False})
        match_search = search.lower() in p.lower()
        match_role = (role == "All") or (info["role"] == role)
        
        if match_search and match_role:
            with cols[display_count % 2]:
                c_cell, c_box = st.columns([4, 1])
                with c_cell:
                    st.markdown(f'''<div class="mobile-matrix">
                        <span class="jersey-dot" style="background:{TEAM_COLORS.get(info['team'], '#ccc')}"></span>
                        <div style="flex-grow:1; line-height:1.1;">
                            <span style="font-size:11px; font-weight:600;">{p} {"✈️" if info['is_overseas'] else ""}</span><br>
                            <span class="role-label">{ROLE_EMOJI.get(info['role'], 'BAT')}</span>
                        </div>
                    </div>''', unsafe_allow_html=True)
                with c_box:
                    val = st.checkbox("", key=f"cb_{user}_{p}", value=(p in selected_list), label_visibility="collapsed")
                    if val: selected_list.add(p)
                    elif not val and p in selected_list: selected_list.discard(p)
            display_count += 1

    # VALIDATION LOGIC
    st.divider()
    os_count = sum(1 for p in selected_list if db["player_master"].get(p, {}).get("is_overseas", False))
    wk_count = sum(1 for p in selected_list if db["player_master"].get(p, {}).get("role") == "WK")
    
    v_col1, v_col2, v_col3 = st.columns(3)
    v_col1.metric("Squad", f"{len(selected_list)}/11")
    v_col2.metric("Overseas", f"{os_count}/4", delta=None if os_count <= 4 else "Limit Exceeded", delta_color="inverse")
    v_col3.metric("Keepers", f"{wk_count}/Min 1")

    if len(selected_list) == 11 and os_count <= 4 and wk_count >= 1:
        cap = st.selectbox("🛡️ Select Captain", list(selected_list), index=list(selected_list).index(saved["cap"]) if saved["cap"] in selected_list else 0)
        if st.button("🚀 LOCK SQUAD", type="primary", use_container_width=True):
            if active_week not in db["selections"]: db["selections"][active_week] = {}
            db["selections"][active_week][user] = {"squad": list(selected_list), "cap": cap}
            save_db(db)
            st.success("Squad locked successfully!")
    else:
        st.warning("Ensure 11 Players, Max 4 Overseas, and Min 1 Keeper.")

# --- TAB 2: STANDINGS ---
with t2:
    st.subheader("📊 Leaderboard")
    managers = list(db["pools"].keys())
    lb_cols = st.columns(2)
    lb_data = []
    for i, m in enumerate(managers):
        t_pts, w_pts = 0, 0
        for wk, matches in SEASON_WEEKS.items():
            sel = db["selections"].get(wk, {}).get(m, {"squad": [], "cap": ""})
            week_total = 0
            for p in sel["squad"]:
                p_sc = db["scores"].get(p, {})
                pts = sum([v for k, v in p_sc.items() if k in matches])
                week_total += (pts * 2) if p == sel["cap"] else pts
            t_pts += week_total
            if wk == active_week: w_pts = week_total
        lb_data.append({"Manager": m, "Weekly": w_pts, "Total": t_pts})
        with lb_cols[i % 2]:
            st.markdown(f'<div class="lb-card"><b>{m}</b><br><small>Week: {w_pts}</small><span class="total-pts">{t_pts}</span></div>', unsafe_allow_html=True)
    st.divider()
    st.dataframe(pd.DataFrame(lb_data).sort_values("Total", ascending=False), use_container_width=True, hide_index=True)

# --- TAB 3: ADMIN ---
with t3:
    at1, at2, at3 = st.tabs(["📝 SCORING", "👥 POOLS", "🛠️ PLAYER MASTER"])
    with at1:
        match_list = {f"{mid}: {txt}": mid for wk in SEASON_WEEKS.values() for mid, txt in wk.items()}
        sel_display = st.selectbox("Select Match", list(match_list.keys()))
        sel_mid = match_list[sel_display]
        match_teams = sel_display.split(": ")[1].split(" vs ")
        eligible = [p for p, info in db["player_master"].items() if info['team'] in match_teams]
        for p in sorted(eligible):
            with st.expander(f"Score: {p}"):
                cur = db["scores"].get(p, {}).get(sel_mid, 0)
                score = st.number_input(f"Points", 0, value=int(cur), key=f"sc_{sel_mid}_{p}")
                if st.button(f"Save {p}"):
                    if p not in db["scores"]: db["scores"][p] = {}
                    db["scores"][p][sel_mid] = score
                    save_db(db)
                    st.toast(f"Saved {p}")

    with at2:
        m_edit = st.selectbox("Manager Pool", list(db["pools"].keys()), key="adm_m")
        updated_pool = st.multiselect("Edit Squad", options=sorted(list(db["player_master"].keys())), default=db["pools"][m_edit])
        if st.button("Update Pool"):
            db["pools"][m_edit] = updated_pool
            save_db(db)
            st.success("Pool Updated!")

    with at3:
        p_name = st.selectbox("Player", ["Add New"] + sorted(list(db["player_master"].keys())))
        if p_name == "Add New": p_name = st.text_input("Full Name")
        c_a, c_b, c_c = st.columns(3)
        p_team = c_a.selectbox("Team", list(TEAM_COLORS.keys()), key="ed_t")
        p_role = c_b.selectbox("Role", ["BAT", "BOWL", "WK"], key="ed_r")
        p_os = c_c.checkbox("Overseas?", key="ed_o")
        if st.button("Save to Master"):
            db["player_master"][p_name] = {"team": p_team, "role": p_role, "is_overseas": p_os}
            save_db(db)
            st.success("Saved!")
