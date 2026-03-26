# VERSION: ver02_260326_PREMIUM_UI
# STATUS: Premium Dark Cricket UI - Multi-View Standings + Full Feature Set

import streamlit as st
import pandas as pd
import json
import os
from collections import Counter

# --- 1. CONFIGURATION & DATA ---
DB_FILE = 'tournament_db.json'
TEAM_COLORS = {
    'RCB': '#d11d26', 'MI': '#004ba0', 'CSK': '#fdb913', 'SRH': '#f26522',
    'RR': '#ea1a85', 'KKR': '#3a225d', 'GT': '#1b2133', 'LSG': '#0057e2',
    'DC': '#0078bc', 'PBKS': '#dd1f2d', 'IPL': '#000080'
}
TEAM_SECONDARY = {
    'RCB': '#1a0a0a', 'MI': '#001f4d', 'CSK': '#7a5c00', 'SRH': '#7a2d00',
    'RR': '#7a0040', 'KKR': '#1a0d2e', 'GT': '#0d1019', 'LSG': '#002878',
    'DC': '#003d5e', 'PBKS': '#7a0010', 'IPL': '#000040'
}
ROLE_EMOJI = {'BAT': '🏏', 'BOWL': '⚾', 'WK': '🧤'}
MANAGER_COLORS = {
    'Kazim': '#f59e0b', 'Aman': '#10b981', 
    'Aatish': '#6366f1', 'Shrijeet': '#ec4899', 'Nagle': '#14b8a6'
}

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

def load_db():
    pm = {
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
        "Tushar Deshpande": {"team": "RR", "role": "BOWL", "is_overseas": False}, "Travis Head": {"team": "SRH", "role": "BAT", "is_overseas": True},
        "Ishan Kishan": {"team": "SRH", "role": "WK", "is_overseas": False}, "Riyan Parag": {"team": "RR", "role": "BAT", "is_overseas": False},
        "Shreyas Iyer": {"team": "PBKS", "role": "BAT", "is_overseas": False}, "Ayush Badoni": {"team": "LSG", "role": "BAT", "is_overseas": False},
        "Himmat Singh": {"team": "IPL", "role": "BAT", "is_overseas": False}, "Manish Pandey": {"team": "KKR", "role": "BAT", "is_overseas": False},
        "Ajinkya Rahane": {"team": "CSK", "role": "BAT", "is_overseas": False}, "Sai Sudharsan": {"team": "GT", "role": "BAT", "is_overseas": False},
        "Prithvi Shaw": {"team": "DC", "role": "BAT", "is_overseas": False}, "Karun Nair": {"team": "IPL", "role": "BAT", "is_overseas": False},
        "Abishek Porel": {"team": "DC", "role": "WK", "is_overseas": False}, "Sarfaraz Khan": {"team": "DC", "role": "BAT", "is_overseas": False},
        "Ruturaj Gaikwad": {"team": "CSK", "role": "BAT", "is_overseas": False}, "Ramakrishna Ghosh": {"team": "IPL", "role": "BOWL", "is_overseas": False},
        "Mitchell Marsh": {"team": "DC", "role": "BAT", "is_overseas": True}, "Krunal Pandya": {"team": "RCB", "role": "BOWL", "is_overseas": False},
        "Venkatesh Iyer": {"team": "KKR", "role": "BAT", "is_overseas": False}, "Jaydev Unadkat": {"team": "SRH", "role": "BOWL", "is_overseas": False},
        "Suyash Sharma": {"team": "KKR", "role": "BOWL", "is_overseas": False}, "Sandeep Sharma": {"team": "RR", "role": "BOWL", "is_overseas": False},
        "Arshdeep Singh": {"team": "PBKS", "role": "BOWL", "is_overseas": False}, "Trent Boult": {"team": "MI", "role": "BOWL", "is_overseas": True},
        "Mohammed Shami": {"team": "SRH", "role": "BOWL", "is_overseas": False}, "Kagiso Rabada": {"team": "GT", "role": "BOWL", "is_overseas": True},
        "Mitchell Santner": {"team": "CSK", "role": "BOWL", "is_overseas": True}, "Kartik Sharma": {"team": "IPL", "role": "BAT", "is_overseas": False},
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
        "Kazim": list(pm.keys())[:30], "Aman": list(pm.keys())[30:52],
        "Aatish": list(pm.keys())[52:87], "Shrijeet": list(pm.keys())[87:114],
        "Nagle": list(pm.keys())[114:]
    }
    if not os.path.exists(DB_FILE):
        return {"selections": {}, "scores": {}, "pools": initial_pools, "player_master": pm}
    with open(DB_FILE, 'r') as f: data = json.load(f)
    return data

def save_db(data):
    with open(DB_FILE, 'w') as f: json.dump(data, f)

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────
st.set_page_config(page_title="Inner Circle IPL 2025", layout="wide", initial_sidebar_state="expanded")

# ─── GLOBAL CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
    --bg-base: #0a0c12;
    --bg-card: #111520;
    --bg-elevated: #181d2a;
    --border: #252b3b;
    --border-glow: #334155;
    --text-primary: #f1f5f9;
    --text-secondary: #94a3b8;
    --text-muted: #475569;
    --accent-gold: #f59e0b;
    --accent-green: #10b981;
    --accent-red: #ef4444;
    --accent-blue: #3b82f6;
    --glow-gold: rgba(245,158,11,0.15);
    --glow-green: rgba(16,185,129,0.15);
}

html, body, [data-testid="stApp"] {
    background-color: var(--bg-base) !important;
    color: var(--text-primary) !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── HEADER ── */
.app-header {
    background: linear-gradient(135deg, #0a0c12 0%, #111520 50%, #0a0c12 100%);
    border-bottom: 1px solid var(--border);
    padding: 20px 0 16px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}
.app-header::before {
    content: '';
    position: absolute;
    top: -40px; left: 50%; transform: translateX(-50%);
    width: 600px; height: 150px;
    background: radial-gradient(ellipse, rgba(245,158,11,0.08) 0%, transparent 70%);
    pointer-events: none;
}
.app-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 3rem;
    letter-spacing: 4px;
    background: linear-gradient(135deg, #f59e0b 0%, #fde68a 50%, #f59e0b 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin: 0; line-height: 1;
}
.app-subtitle {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: var(--text-muted);
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-top: 4px;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: var(--bg-card) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text-primary) !important; }
[data-testid="stSidebar"] .stSelectbox > label,
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: var(--text-primary) !important; }

.sidebar-week-badge {
    background: var(--bg-elevated);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent-gold);
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 8px;
    font-size: 12px;
}
.sidebar-match-id {
    font-family: 'JetBrains Mono', monospace;
    color: var(--accent-gold);
    font-size: 11px;
    font-weight: 600;
}
.sidebar-fixture {
    color: var(--text-primary);
    font-weight: 600;
    font-size: 13px;
}
.team-count-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 5px 0; border-bottom: 1px solid var(--border);
    font-size: 12px;
}
.team-dot { display:inline-block; width:8px; height:8px; border-radius:50%; margin-right:6px; }

/* ── TABS ── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: var(--bg-card) !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0 !important;
    padding: 0 !important;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-secondary) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    padding: 14px 20px !important;
    border-bottom: 2px solid transparent !important;
    transition: all 0.2s ease;
}
[data-testid="stTabs"] [data-baseweb="tab"]:hover {
    color: var(--text-primary) !important;
    background: var(--bg-elevated) !important;
}
[data-testid="stTabs"] [aria-selected="true"] {
    color: var(--accent-gold) !important;
    border-bottom: 2px solid var(--accent-gold) !important;
    background: var(--bg-elevated) !important;
}
[data-testid="stTabs"] [data-baseweb="tab-panel"] {
    background: var(--bg-base) !important;
    padding: 20px 0 !important;
}

/* ── PLAYER CARD ── */
.player-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 10px 14px;
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 6px;
    transition: border-color 0.2s, background 0.2s;
    position: relative; overflow: hidden;
}
.player-card:hover { border-color: var(--border-glow); }
.player-card.selected {
    border-color: var(--accent-gold) !important;
    background: linear-gradient(135deg, var(--bg-elevated) 0%, rgba(245,158,11,0.05) 100%);
}
.player-card::before {
    content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 3px;
}
.team-stripe-RCB::before { background: #d11d26; }
.team-stripe-MI::before { background: #004ba0; }
.team-stripe-CSK::before { background: #fdb913; }
.team-stripe-SRH::before { background: #f26522; }
.team-stripe-RR::before { background: #ea1a85; }
.team-stripe-KKR::before { background: #3a225d; }
.team-stripe-GT::before { background: #6b7280; }
.team-stripe-LSG::before { background: #0057e2; }
.team-stripe-DC::before { background: #0078bc; }
.team-stripe-PBKS::before { background: #dd1f2d; }
.player-name { font-weight: 600; font-size: 13px; color: var(--text-primary); flex: 1; }
.player-meta { font-size: 11px; color: var(--text-muted); }
.role-chip {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px; font-weight: 700;
    padding: 2px 7px; border-radius: 4px;
    background: var(--bg-elevated); color: var(--text-secondary);
    border: 1px solid var(--border);
}
.overseas-flag { font-size: 14px; }

/* ── SQUAD COUNTER BAR ── */
.squad-bar {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px 20px;
    margin: 16px 0;
    display: flex; align-items: center; gap: 20px;
}
.squad-stat { text-align: center; }
.squad-stat-val {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2rem; line-height: 1;
    color: var(--accent-gold);
}
.squad-stat-label { font-size: 10px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px; }

/* ── STANDINGS CARDS ── */
.standings-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 18px 20px;
    margin-bottom: 12px;
    display: flex; align-items: center; gap: 16px;
    transition: border-color 0.2s;
    position: relative; overflow: hidden;
}
.standings-card:hover { border-color: var(--border-glow); }
.standings-card.rank-1 { border-color: var(--accent-gold); background: linear-gradient(135deg, var(--bg-card) 0%, rgba(245,158,11,0.06) 100%); }
.standings-card.rank-2 { border-color: #94a3b8; background: linear-gradient(135deg, var(--bg-card) 0%, rgba(148,163,184,0.04) 100%); }
.standings-card.rank-3 { border-color: #cd7c2f; background: linear-gradient(135deg, var(--bg-card) 0%, rgba(205,124,47,0.04) 100%); }
.rank-number {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2.5rem; line-height: 1;
    color: var(--text-muted); width: 48px; text-align: center;
}
.rank-1 .rank-number { color: var(--accent-gold); }
.rank-2 .rank-number { color: #94a3b8; }
.rank-3 .rank-number { color: #cd7c2f; }
.manager-info { flex: 1; }
.manager-name-lg {
    font-family: 'DM Sans', sans-serif;
    font-weight: 700; font-size: 1.1rem; color: var(--text-primary);
}
.manager-tag {
    display: inline-block;
    width: 10px; height: 10px; border-radius: 50%;
    margin-right: 6px; vertical-align: middle;
}
.pts-block { text-align: right; }
.pts-total {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2.2rem; line-height: 1;
    color: var(--text-primary);
}
.pts-label { font-size: 10px; color: var(--text-muted); letter-spacing: 1px; text-transform: uppercase; }
.pts-weekly { font-size: 12px; color: var(--text-secondary); margin-top: 2px; }
.delta-up { color: var(--accent-green); font-weight: 700; }
.delta-dn { color: var(--accent-red); font-weight: 700; }
.delta-nc { color: var(--text-muted); }

/* ── SQUAD VIEW ── */
.squad-view-header {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.3rem; letter-spacing: 3px;
    color: var(--text-primary); margin-bottom: 12px;
    display: flex; align-items: center; gap: 10px;
}
.mgr-color-bar { height: 3px; border-radius: 2px; margin-bottom: 12px; }
.squad-player-item {
    display: flex; align-items: center; justify-content: space-between;
    padding: 8px 12px;
    border-bottom: 1px solid var(--border);
    font-size: 12px;
}
.squad-player-item:last-child { border-bottom: none; }
.squad-player-name { font-weight: 600; color: var(--text-primary); }
.cap-badge {
    background: var(--accent-gold); color: #000;
    padding: 1px 7px; border-radius: 4px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px; font-weight: 700;
}

/* ── PERFORMER CARD ── */
.performer-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px;
    text-align: center;
    position: relative; overflow: hidden;
}
.performer-card::after {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent-gold), transparent);
}
.performer-rank {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.5rem; color: var(--text-muted);
}
.performer-name { font-weight: 700; font-size: 13px; color: var(--text-primary); margin: 4px 0; }
.performer-pts {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2rem; color: var(--accent-gold);
}
.performer-pts-label { font-size: 10px; color: var(--text-muted); text-transform: uppercase; }

/* ── ADMIN ── */
.admin-player-row {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 8px;
}
.admin-player-name { font-weight: 700; font-size: 14px; color: var(--text-primary); margin-bottom: 8px; }
.admin-team-badge {
    display: inline-block;
    padding: 2px 8px; border-radius: 4px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px; font-weight: 700;
    margin-left: 8px;
}

/* ── BUTTONS ── */
[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #f59e0b, #d97706) !important;
    color: #000 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 700 !important;
    font-size: 14px !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 12px 24px !important;
    letter-spacing: 1px !important;
    transition: all 0.2s !important;
}
[data-testid="stButton"] > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(245,158,11,0.4) !important;
}

/* ── INPUTS ── */
[data-testid="stSelectbox"] > div > div,
[data-testid="stTextInput"] > div > div > input,
[data-testid="stNumberInput"] > div > div > input {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-primary) !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stSelectbox"] > label,
[data-testid="stTextInput"] > label,
[data-testid="stNumberInput"] > label {
    color: var(--text-secondary) !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px !important;
    text-transform: uppercase !important;
}

/* ── CHECKBOXES ── */
[data-testid="stCheckbox"] > label { color: var(--text-primary) !important; }

/* ── DIVIDER ── */
hr { border-color: var(--border) !important; }

/* ── WARNINGS / SUCCESS ── */
[data-testid="stAlert"] {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
}

/* ── METRIC ── */
[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 14px !important;
}
[data-testid="stMetricLabel"] { color: var(--text-secondary) !important; }
[data-testid="stMetricValue"] { color: var(--text-primary) !important; font-family: 'Bebas Neue', sans-serif !important; font-size: 1.8rem !important; }

/* TABLE */
[data-testid="stTable"] table {
    background: var(--bg-card) !important;
    border-radius: 10px !important;
    overflow: hidden;
}
[data-testid="stTable"] th {
    background: var(--bg-elevated) !important;
    color: var(--text-secondary) !important;
    font-size: 11px !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    border-bottom: 1px solid var(--border) !important;
}
[data-testid="stTable"] td {
    color: var(--text-primary) !important;
    border-bottom: 1px solid var(--border) !important;
    font-size: 13px !important;
}

/* SCROLLBAR */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-base); }
::-webkit-scrollbar-thumb { background: var(--border-glow); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

db = load_db()

# ─── HEADER ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
  <div style="text-align:center;">
    <div class="app-title">⚡ INNER CIRCLE IPL</div>
    <div class="app-subtitle">Fantasy Cricket League · 2025 Season</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── SIDEBAR ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""<div style="font-family:'Bebas Neue',sans-serif; font-size:1.4rem; letter-spacing:3px; color:#f59e0b; margin-bottom:16px;">🗓 SCHEDULE</div>""", unsafe_allow_html=True)
    active_week = st.selectbox("Select Week", list(SEASON_WEEKS.keys()), label_visibility="collapsed")
    matches_this_week = SEASON_WEEKS[active_week]

    all_teams_this_week = []
    for fixture in matches_this_week.values():
        if " vs " in fixture:
            teams = fixture.split(" vs ")
            all_teams_this_week.extend(teams)
    team_counts = Counter(all_teams_this_week)

    st.markdown(f"""<div style="font-family:'JetBrains Mono',monospace; font-size:10px; color:#475569; letter-spacing:2px; text-transform:uppercase; margin: 12px 0 8px;">{active_week}</div>""", unsafe_allow_html=True)

    for mid, fixture in matches_this_week.items():
        st.markdown(f"""
        <div class="sidebar-week-badge">
            <span class="sidebar-match-id">{mid}</span>
            <div class="sidebar-fixture">{fixture}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<hr style="margin: 16px 0;">', unsafe_allow_html=True)
    st.markdown("""<div style="font-family:'JetBrains Mono',monospace; font-size:10px; color:#475569; letter-spacing:2px; text-transform:uppercase; margin-bottom:8px;">TEAMS THIS WEEK</div>""", unsafe_allow_html=True)
    for team, count in sorted(team_counts.items()):
        color = TEAM_COLORS.get(team, '#475569')
        st.markdown(f"""
        <div class="team-count-row">
            <span><span class="team-dot" style="background:{color};"></span><b>{team}</b></span>
            <span style="font-family:'JetBrains Mono',monospace; color:#94a3b8; font-size:11px;">{count}M</span>
        </div>""", unsafe_allow_html=True)

# ─── TABS ───────────────────────────────────────────────────────────────────
t1, t_view, t2, t_admin = st.tabs(["🏏  MY SQUAD", "👀  ALL SQUADS", "📊  STANDINGS", "🛡️  ADMIN"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — MY SQUAD
# ══════════════════════════════════════════════════════════════════════════════
with t1:
    user = st.selectbox("Select Manager", list(db["pools"].keys()))
    pool = db["pools"].get(user, [])
    saved = db["selections"].get(active_week, {}).get(user, {"squad": [], "cap": ""})
    state_key = f"sel_{user}_{active_week}"
    if state_key not in st.session_state:
        st.session_state[state_key] = list(saved["squad"])

    mgr_color = MANAGER_COLORS.get(user, '#f59e0b')

    # Search + Filter
    f1, f2 = st.columns([3, 1])
    with f1:
        search = st.text_input("", placeholder="🔍  Search player name...", key="src_1", label_visibility="collapsed")
    with f2:
        role_f = st.selectbox("", ["All", "BAT 🏏", "BOWL ⚾", "WK 🧤"], key="rol_1", label_visibility="collapsed")
    role_map = {"All": "All", "BAT 🏏": "BAT", "BOWL ⚾": "BOWL", "WK 🧤": "WK"}
    role_filter = role_map[role_f]

    # Player Grid
    cols = st.columns(2)
    display_idx = 0
    for p in sorted(pool):
        info = db["player_master"].get(p, {"team": "IPL", "role": "BAT", "is_overseas": False})
        if (search.lower() in p.lower()) and (role_filter == "All" or info["role"] == role_filter):
            is_sel = p in st.session_state[state_key]
            team_color = TEAM_COLORS.get(info["team"], "#475569")
            sel_class = "selected" if is_sel else ""
            with cols[display_idx % 2]:
                col_card, col_check = st.columns([5, 1])
                with col_card:
                    st.markdown(f"""
                    <div class="player-card {sel_class} team-stripe-{info['team']}">
                        <div style="width:32px; height:32px; border-radius:8px; background:{team_color}22; border:1px solid {team_color}44; display:flex; align-items:center; justify-content:center; font-size:16px; flex-shrink:0;">
                            {ROLE_EMOJI.get(info['role'], '🏏')}
                        </div>
                        <div style="flex:1; min-width:0;">
                            <div class="player-name" style="white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                                {p} {'✈️' if info['is_overseas'] else ''}
                            </div>
                            <div style="display:flex; align-items:center; gap:6px; margin-top:2px;">
                                <span style="font-family:'JetBrains Mono',monospace; font-size:10px; color:{team_color}; font-weight:700;">{info['team']}</span>
                                <span class="role-chip">{info['role']}</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_check:
                    st.markdown('<div style="padding-top:10px;">', unsafe_allow_html=True)
                    if st.checkbox("", key=f"cb_{user}_{active_week}_{p}", value=is_sel):
                        if p not in st.session_state[state_key]:
                            st.session_state[state_key].append(p); st.rerun()
                    elif p in st.session_state[state_key]:
                        st.session_state[state_key].remove(p); st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
            display_idx += 1

    st.markdown('<hr style="margin: 20px 0;">', unsafe_allow_html=True)

    # Squad Counter
    final_squad = st.session_state[state_key]
    os_count = sum(1 for p in final_squad if db["player_master"].get(p, {}).get("is_overseas"))
    wk_count = sum(1 for p in final_squad if db["player_master"].get(p, {}).get("role") == "WK")

    pl_color = '#10b981' if len(final_squad) == 11 else '#f59e0b' if len(final_squad) < 11 else '#ef4444'
    os_color = '#10b981' if os_count <= 4 else '#ef4444'
    wk_color = '#10b981' if wk_count >= 1 else '#ef4444'

    st.markdown(f"""
    <div style="background:#111520; border:1px solid #252b3b; border-radius:12px; padding:16px 20px; margin:16px 0; display:flex; gap:32px; flex-wrap:wrap;">
        <div style="text-align:center;">
            <div style="font-family:'Bebas Neue',sans-serif; font-size:2.2rem; color:{pl_color}; line-height:1;">{len(final_squad)}<span style="font-size:1.2rem; color:#475569;">/11</span></div>
            <div style="font-size:10px; color:#475569; text-transform:uppercase; letter-spacing:1px;">Players</div>
        </div>
        <div style="text-align:center;">
            <div style="font-family:'Bebas Neue',sans-serif; font-size:2.2rem; color:{os_color}; line-height:1;">{os_count}<span style="font-size:1.2rem; color:#475569;">/4</span></div>
            <div style="font-size:10px; color:#475569; text-transform:uppercase; letter-spacing:1px;">Overseas</div>
        </div>
        <div style="text-align:center;">
            <div style="font-family:'Bebas Neue',sans-serif; font-size:2.2rem; color:{wk_color}; line-height:1;">{wk_count}<span style="font-size:1.2rem; color:#475569;">+</span></div>
            <div style="font-size:10px; color:#475569; text-transform:uppercase; letter-spacing:1px;">Keepers</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if len(final_squad) == 11 and os_count <= 4 and wk_count >= 1:
        default_cap = final_squad.index(saved["cap"]) if saved["cap"] in final_squad else 0
        cap = st.selectbox("🛡️ Captain", final_squad, index=default_cap)
        if st.button("🚀  LOCK SQUAD", type="primary", use_container_width=True):
            if active_week not in db["selections"]: db["selections"][active_week] = {}
            db["selections"][active_week][user] = {"squad": final_squad, "cap": cap}
            save_db(db)
            st.success(f"✅ Squad locked for {active_week}! Captain: **{cap}**")
    else:
        st.markdown("""
        <div style="background:rgba(245,158,11,0.08); border:1px solid rgba(245,158,11,0.3); border-radius:8px; padding:12px 16px; font-size:13px; color:#fbbf24;">
            ⚠️ Rules: Exactly 11 players · Max 4 Overseas · Min 1 Keeper
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — ALL SQUADS VIEW
# ══════════════════════════════════════════════════════════════════════════════
with t_view:
    manager_list = list(db["pools"].keys())
    cols = st.columns(len(manager_list))
    for i, mgr in enumerate(manager_list):
        with cols[i]:
            mgr_color = MANAGER_COLORS.get(mgr, '#f59e0b')
            s_data = db["selections"].get(active_week, {}).get(mgr, None)

            st.markdown(f"""
            <div style="margin-bottom:8px;">
                <div style="font-family:'Bebas Neue',sans-serif; font-size:1.1rem; letter-spacing:2px; color:{mgr_color};">{mgr}</div>
                <div style="height:2px; background:{mgr_color}; border-radius:2px; margin-bottom:10px; opacity:0.6;"></div>
            </div>
            """, unsafe_allow_html=True)

            if not s_data:
                st.markdown("""
                <div style="background:#111520; border:1px solid #252b3b; border-radius:10px; padding:20px; text-align:center; color:#475569; font-size:12px;">
                    No squad submitted
                </div>
                """, unsafe_allow_html=True)
            else:
                players_html = ""
                for player in sorted(s_data["squad"]):
                    p_info = db["player_master"].get(player, {"team": "IPL", "role": "BAT", "is_overseas": False})
                    team_color = TEAM_COLORS.get(p_info["team"], "#475569")
                    cap_html = '<span class="cap-badge">C</span>' if player == s_data["cap"] else ""
                    role_icon = ROLE_EMOJI.get(p_info["role"], "")
                    players_html += f"""
                    <div class="squad-player-item">
                        <span>
                            <span style="font-size:11px;">{role_icon}</span>
                            <span class="squad-player-name"> {player}</span>
                        </span>
                        <span style="display:flex; align-items:center; gap:6px;">
                            <span style="font-family:'JetBrains Mono',monospace; font-size:9px; color:{team_color}; font-weight:700;">{p_info['team']}</span>
                            {cap_html}
                        </span>
                    </div>"""

                st.markdown(f"""
                <div style="background:#111520; border:1px solid #252b3b; border-radius:10px; overflow:hidden;">
                    {players_html}
                </div>
                """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — STANDINGS
# ══════════════════════════════════════════════════════════════════════════════
with t2:
    lb_data = []
    player_weekly_pts = Counter()
    week_keys = list(SEASON_WEEKS.keys())
    cur_idx = week_keys.index(active_week)

    for m in db["pools"].keys():
        total, week, prev = 0, 0, 0
        for idx, (wk, matches) in enumerate(SEASON_WEEKS.items()):
            sel = db["selections"].get(wk, {}).get(m, {"squad": [], "cap": ""})
            w_pts = 0
            for p in sel["squad"]:
                p_pts = 0
                for mid in matches:
                    s = db["scores"].get(p, {}).get(mid, {"r":0, "w":0, "c":0, "s":0})
                    m_pts = (s.get("r",0)*1) + (s.get("w",0)*20) + (s.get("c",0)*5) + (s.get("s",0)*5)
                    p_pts += m_pts
                    if wk == active_week: player_weekly_pts[p] += m_pts
                if p == sel["cap"]: p_pts *= 2
                w_pts += p_pts
            total += w_pts
            if wk == active_week: week = w_pts
            if idx < cur_idx: prev += w_pts
        lb_data.append({"Manager": m, "Weekly": week, "Total": total, "PrevTotal": prev})

    curr_rank = sorted(lb_data, key=lambda x: x['Total'], reverse=True)
    prev_rank = sorted(lb_data, key=lambda x: x['PrevTotal'], reverse=True)

    st.markdown("""<div style="font-family:'Bebas Neue',sans-serif; font-size:1.6rem; letter-spacing:3px; color:#f1f5f9; margin-bottom:20px;">📊 CURRENT STANDINGS</div>""", unsafe_allow_html=True)

    rank_labels = {1: "🥇", 2: "🥈", 3: "🥉"}
    rank_classes = {1: "rank-1", 2: "rank-2", 3: "rank-3"}

    for i, row in enumerate(curr_rank):
        c_pos = i + 1
        p_pos = next(idx for idx, d in enumerate(prev_rank) if d['Manager'] == row['Manager']) + 1

        if c_pos < p_pos:
            delta_html = f'<span class="delta-up">▲ +{p_pos-c_pos}</span>'
        elif c_pos > p_pos:
            delta_html = f'<span class="delta-dn">▼ -{c_pos-p_pos}</span>'
        else:
            delta_html = '<span class="delta-nc">— same</span>'

        mgr_color = MANAGER_COLORS.get(row["Manager"], "#f59e0b")
        rank_class = rank_classes.get(c_pos, "")
        rank_icon = rank_labels.get(c_pos, f"#{c_pos}")

        st.markdown(f"""
        <div class="standings-card {rank_class}">
            <div class="rank-number">{rank_icon}</div>
            <div class="manager-info">
                <div class="manager-name-lg">
                    <span class="manager-tag" style="background:{mgr_color};"></span>
                    {row["Manager"]}
                </div>
                <div style="font-size:12px; color:#94a3b8; margin-top:4px;">
                    This week: <b style="color:#f1f5f9;">{row['Weekly']} pts</b>
                    &nbsp;&nbsp;{delta_html}
                </div>
            </div>
            <div class="pts-block">
                <div class="pts-total">{row['Total']}</div>
                <div class="pts-label">TOTAL PTS</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr style="margin: 28px 0 20px;">', unsafe_allow_html=True)
    st.markdown("""<div style="font-family:'Bebas Neue',sans-serif; font-size:1.4rem; letter-spacing:3px; color:#f1f5f9; margin-bottom:16px;">🔥 TOP PERFORMERS THIS WEEK</div>""", unsafe_allow_html=True)

    if player_weekly_pts:
        top_players = player_weekly_pts.most_common(5)
        p_cols = st.columns(len(top_players))
        for i, (p_name, p_val) in enumerate(top_players):
            p_info = db["player_master"].get(p_name, {"team": "IPL", "role": "BAT"})
            team_color = TEAM_COLORS.get(p_info["team"], "#475569")
            with p_cols[i]:
                st.markdown(f"""
                <div class="performer-card">
                    <div class="performer-rank">#{i+1}</div>
                    <div style="font-family:'JetBrains Mono',monospace; font-size:9px; color:{team_color}; font-weight:700; margin:4px 0;">{p_info['team']}</div>
                    <div class="performer-name">{p_name}</div>
                    <div class="performer-pts">{p_val}</div>
                    <div class="performer-pts-label">pts</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:#475569; font-size:13px; text-align:center; padding:20px;">No matches scored yet for this week.</div>', unsafe_allow_html=True)

    st.markdown('<hr style="margin: 28px 0 20px;">', unsafe_allow_html=True)
    st.markdown("""<div style="font-family:'Bebas Neue',sans-serif; font-size:1.4rem; letter-spacing:3px; color:#f1f5f9; margin-bottom:12px;">📋 SUMMARY TABLE</div>""", unsafe_allow_html=True)
    df_lb = pd.DataFrame(curr_rank).drop(columns=['PrevTotal'])
    df_lb.index = range(1, len(df_lb) + 1)
    df_lb.columns = ['Manager', 'This Week', 'Total']
    st.table(df_lb)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — ADMIN
# ══════════════════════════════════════════════════════════════════════════════
with t_admin:
    st.markdown("""<div style="font-family:'Bebas Neue',sans-serif; font-size:1.6rem; letter-spacing:3px; color:#f59e0b; margin-bottom:20px;">🛡️ SCORE ENTRY</div>""", unsafe_allow_html=True)

    match_opts = {f"{mid}: {txt}": mid for mid, txt in matches_this_week.items()}
    sel_display = st.selectbox("Select Match", list(match_opts.keys()))
    sel_mid = match_opts[sel_display]

    all_submitted = set()
    for mgr_data in db["selections"].get(active_week, {}).values():
        all_submitted.update(mgr_data["squad"])

    teams = sel_display.split(": ")[1].split(" vs ") if " vs " in sel_display.split(": ")[1] else []
    eligible = [p for p in all_submitted if db["player_master"].get(p, {}).get("team") in teams] if teams else []

    if not eligible:
        st.markdown("""
        <div style="background:rgba(245,158,11,0.08); border:1px solid rgba(245,158,11,0.25); border-radius:8px; padding:14px 18px; color:#fbbf24; font-size:13px;">
            ⚠️ No submitted players found for this match.
        </div>
        """, unsafe_allow_html=True)
    else:
        cols_a = st.columns(2)
        for pi, p in enumerate(sorted(eligible)):
            pteam = db['player_master'][p]['team']
            team_color = TEAM_COLORS.get(pteam, '#475569')
            cur = db["scores"].get(p, {}).get(sel_mid, {"r":0,"w":0,"c":0,"s":0})

            with cols_a[pi % 2]:
                st.markdown(f"""
                <div class="admin-player-row">
                    <div class="admin-player-name">
                        {ROLE_EMOJI.get(db['player_master'][p]['role'], '')} {p}
                        <span class="admin-team-badge" style="background:{team_color}22; color:{team_color}; border:1px solid {team_color}44;">{pteam}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                c1, c2, c3, c4 = st.columns(4)
                r = c1.number_input("Runs", 0, 200, int(cur["r"]), key=f"r_{sel_mid}_{p}", label_visibility="visible")
                w = c2.number_input("Wkts", 0, 10, int(cur["w"]), key=f"w_{sel_mid}_{p}")
                c_val = c3.number_input("Cat/RO", 0, 10, int(cur["c"]), key=f"c_{sel_mid}_{p}")
                s = c4.number_input("Stump", 0, 10, int(cur["s"]), key=f"s_{sel_mid}_{p}")
                if {"r":r,"w":w,"c":c_val,"s":s} != cur:
                    if p not in db["scores"]: db["scores"][p] = {}
                    db["scores"][p][sel_mid] = {"r":r,"w":w,"c":c_val,"s":s}
                    save_db(db)

    st.markdown('<hr style="margin: 28px 0;">', unsafe_allow_html=True)
    st.markdown("""<div style="font-family:'Bebas Neue',sans-serif; font-size:1.2rem; letter-spacing:2px; color:#ef4444; margin-bottom:12px;">⚠️ DANGER ZONE</div>""", unsafe_allow_html=True)

    if st.button("🗑️  RESET ALL DATA", use_container_width=False):
        if os.path.exists(DB_FILE): os.remove(DB_FILE)
        st.rerun()
