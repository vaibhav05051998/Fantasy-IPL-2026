# VERSION: ver03_27032026_Sporty_Cricket_UI
# STATUS: V1 Calendar + Sporty Cricket UI + Team Filter + Min 4 Bowlers + Team Display + IPL 2026 Verified Squads

import streamlit as st
import pandas as pd
import json
import os
from collections import Counter
from datetime import datetime

# --- 1. CONFIGURATION & DATA ---
DB_FILE = 'tournament_db.json'
TEAM_COLORS = {
    'RCB': '#d11d26', 'MI': '#004ba0', 'CSK': '#fdb913', 'SRH': '#f26522',
    'RR': '#ea1a85', 'KKR': '#3a225d', 'GT': '#1b2133', 'LSG': '#0057e2',
    'DC': '#0078bc', 'PBKS': '#dd1f2d', 'IPL': '#000080'
}
ROLE_EMOJI = {'BAT': '🏏', 'BOWL': '🎳', 'WK': '🧤'}

# V1 SCHEDULE
SEASON_WEEKS = {
    "Week 1 (Mar 28 - Apr 03)": {"lock": "2026-03-28 19:00:00", "matches": {"M01": "RCB vs SRH", "M02": "MI vs KKR", "M03": "RR vs CSK", "M04": "PBKS vs GT", "M05": "LSG vs DC", "M06": "KKR vs SRH", "M07": "CSK vs PBKS"}},
    "Week 2 (Apr 04 - Apr 10)": {"lock": "2026-04-04 19:00:00", "matches": {"M08": "DC vs MI", "M09": "GT vs RR", "M10": "SRH vs LSG", "M11": "RCB vs CSK", "M12": "KKR vs PBKS", "M13": "RR vs MI", "M14": "DC vs GT"}},
    "Week 3 (Apr 11 - Apr 17)": {"lock": "2026-04-11 19:00:00", "matches": {"M15": "SRH vs RCB", "M16": "KKR vs MI", "M17": "CSK vs RR", "M18": "GT vs PBKS", "M19": "DC vs LSG", "M20": "SRH vs KKR", "M21": "PBKS vs CSK"}},
    "Week 4 (Apr 18 - Apr 24)": {"lock": "2026-04-18 19:00:00", "matches": {"M22": "MI vs DC", "M23": "RR vs GT", "M24": "LSG vs SRH", "M25": "CSK vs RCB", "M26": "PBKS vs KKR", "M27": "MI vs RR", "M28": "GT vs DC"}},
    "Week 5 (Apr 25 - May 01)": {"lock": "2026-04-25 19:00:00", "matches": {"M29": "LSG vs KKR", "M30": "RCB vs GT", "M31": "SRH vs RR", "M32": "DC vs CSK", "M33": "MI vs PBKS", "M34": "KKR vs RCB", "M35": "RR vs LSG"}},
    "Week 6 (May 02 - May 08)": {"lock": "2026-05-02 19:00:00", "matches": {"M36": "GT vs SRH", "M37": "CSK vs MI", "M38": "PBKS vs DC", "M39": "RCB vs LSG", "M40": "RR vs KKR", "M41": "SRH vs PBKS", "M42": "GT vs CSK"}},
    "Week 7 (May 09 - May 15)": {"lock": "2026-05-09 19:00:00", "matches": {"M43": "DC vs RCB", "M44": "LSG vs MI", "M45": "KKR vs GT", "M46": "CSK vs SRH", "M47": "PBKS vs RR", "M48": "MI vs LSG", "M49": "RCB vs DC"}},
    "Week 8 (May 16 - May 22)": {"lock": "2026-05-16 19:00:00", "matches": {"M50": "GT vs KKR", "M51": "SRH vs CSK", "M52": "RR vs PBKS", "M53": "DC vs RR", "M54": "KKR vs PBKS", "M55": "LSG vs GT", "M56": "MI vs RCB"}},
}

def load_db():
    # -----------------------------------------------------------------------
    # PLAYER MASTER — IPL 2026 VERIFIED SQUADS
    # Pools sourced directly from IPL_teams-1.xlsx (Mar 27 2026)
    # Team assignments cross-checked: ESPNcricinfo, Wikipedia, Sky Sports,
    # SportsTak, CREX injury/withdrawal tracker
    # -----------------------------------------------------------------------
    pm = {
        # ── RCB ──────────────────────────────────────────────────────────────
        "Rajat Patidar":        {"team": "RCB", "role": "BAT",  "is_overseas": False},
        "Devdutt Padikkal":     {"team": "RCB", "role": "BAT",  "is_overseas": False},
        "Phil Salt":            {"team": "RCB", "role": "WK",   "is_overseas": True},
        "Josh Hazlewood":       {"team": "RCB", "role": "BOWL", "is_overseas": True},
        "Bhuvneshwar Kumar":    {"team": "RCB", "role": "BOWL", "is_overseas": False},
        "Yash Dayal":           {"team": "RCB", "role": "BOWL", "is_overseas": False},
        "Suyash Sharma":        {"team": "RCB", "role": "BOWL", "is_overseas": False},
        "Virat Kohli":          {"team": "RCB", "role": "BAT",  "is_overseas": False},
        "Jacob Bethell":        {"team": "RCB", "role": "BAT",  "is_overseas": True},
        "Jitesh Sharma":        {"team": "RCB", "role": "WK",   "is_overseas": False},
        "Romario Shepherd":     {"team": "RCB", "role": "BOWL", "is_overseas": True},
        "Krunal Pandya":        {"team": "RCB", "role": "BOWL", "is_overseas": False},
        "Tim David":            {"team": "RCB", "role": "BAT",  "is_overseas": True},
        "Venkatesh Iyer":       {"team": "RCB", "role": "BAT",  "is_overseas": False},
        "Jacob Duffy":          {"team": "RCB", "role": "BOWL", "is_overseas": True},

        # ── MI ───────────────────────────────────────────────────────────────
        "Ryan Rickelton":       {"team": "MI",  "role": "WK",   "is_overseas": True},
        "Rohit Sharma":         {"team": "MI",  "role": "BAT",  "is_overseas": False},
        "Suryakumar Yadav":     {"team": "MI",  "role": "BAT",  "is_overseas": False},
        "Hardik Pandya":        {"team": "MI",  "role": "BOWL", "is_overseas": False},
        "Tilak Varma":          {"team": "MI",  "role": "BAT",  "is_overseas": False},
        "Jasprit Bumrah":       {"team": "MI",  "role": "BOWL", "is_overseas": False},
        "Trent Boult":          {"team": "MI",  "role": "BOWL", "is_overseas": True},
        "Quinton de Kock":      {"team": "MI",  "role": "WK",   "is_overseas": True},
        "Will Jacks":           {"team": "MI",  "role": "BAT",  "is_overseas": True},
        "Sherfane Rutherford":  {"team": "MI",  "role": "BAT",  "is_overseas": True},
        "Mitchell Santner":     {"team": "MI",  "role": "BOWL", "is_overseas": True},
        "Deepak Chahar":        {"team": "MI",  "role": "BOWL", "is_overseas": False},
        "AM Ghazanfar":         {"team": "MI",  "role": "BOWL", "is_overseas": True},

        # ── CSK ──────────────────────────────────────────────────────────────
        "MS Dhoni":             {"team": "CSK", "role": "WK",   "is_overseas": False},
        "Ruturaj Gaikwad":      {"team": "CSK", "role": "BAT",  "is_overseas": False},
        "Sanju Samson":         {"team": "CSK", "role": "WK",   "is_overseas": False},
        "Shivam Dube":          {"team": "CSK", "role": "BAT",  "is_overseas": False},
        "Dewald Brevis":        {"team": "CSK", "role": "BAT",  "is_overseas": True},
        "Ayush Mhatre":         {"team": "CSK", "role": "BAT",  "is_overseas": False},
        "Anshul Kamboj":        {"team": "CSK", "role": "BOWL", "is_overseas": False},
        "Mukesh Choudhary":     {"team": "CSK", "role": "BOWL", "is_overseas": False},
        "Noor Ahmad":           {"team": "CSK", "role": "BOWL", "is_overseas": True},
        "Khaleel Ahmed":        {"team": "CSK", "role": "BOWL", "is_overseas": False},
        "Prashant Veer":        {"team": "CSK", "role": "BOWL", "is_overseas": False},
        "Kartik Sharma":        {"team": "CSK", "role": "BAT",  "is_overseas": False},
        "Ramakrishna Ghosh":    {"team": "CSK", "role": "BOWL", "is_overseas": False},
        "Sarfaraz Khan":        {"team": "CSK", "role": "BAT",  "is_overseas": False},
        "Rahul Chahar":         {"team": "CSK", "role": "BOWL", "is_overseas": False},

        # ── SRH ──────────────────────────────────────────────────────────────
        "Heinrich Klaasen":     {"team": "SRH", "role": "WK",   "is_overseas": True},
        "Pat Cummins":          {"team": "SRH", "role": "BOWL", "is_overseas": True},
        "Travis Head":          {"team": "SRH", "role": "BAT",  "is_overseas": True},
        "Abhishek Sharma":      {"team": "SRH", "role": "BAT",  "is_overseas": False},
        "Ishan Kishan":         {"team": "SRH", "role": "WK",   "is_overseas": False},
        "Nitish Kumar Reddy":   {"team": "SRH", "role": "BAT",  "is_overseas": False},
        "Harshal Patel":        {"team": "SRH", "role": "BOWL", "is_overseas": False},
        "Liam Livingstone":     {"team": "SRH", "role": "BAT",  "is_overseas": True},
        "Jaydev Unadkat":       {"team": "SRH", "role": "BOWL", "is_overseas": False},

        # ── RR ───────────────────────────────────────────────────────────────
        "Yashasvi Jaiswal":     {"team": "RR",  "role": "BAT",  "is_overseas": False},
        "Riyan Parag":          {"team": "RR",  "role": "BAT",  "is_overseas": False},
        "Ravindra Jadeja":      {"team": "RR",  "role": "BOWL", "is_overseas": False},
        "Dhruv Jurel":          {"team": "RR",  "role": "WK",   "is_overseas": False},
        "Jofra Archer":         {"team": "RR",  "role": "BOWL", "is_overseas": True},
        "Shimron Hetmyer":      {"team": "RR",  "role": "BAT",  "is_overseas": True},
        "Vaibhav Suryavanshi":  {"team": "RR",  "role": "BAT",  "is_overseas": False},
        "Tushar Deshpande":     {"team": "RR",  "role": "BOWL", "is_overseas": False},
        "Sandeep Sharma":       {"team": "RR",  "role": "BOWL", "is_overseas": False},
        "Donovan Ferreira":     {"team": "RR",  "role": "WK",   "is_overseas": True},
        "Ravi Bishnoi":         {"team": "RR",  "role": "BOWL", "is_overseas": False},

        # ── KKR ──────────────────────────────────────────────────────────────
        "Ajinkya Rahane":       {"team": "KKR", "role": "BAT",  "is_overseas": False},
        "Sunil Narine":         {"team": "KKR", "role": "BOWL", "is_overseas": True},
        "Varun Chakaravarthy":  {"team": "KKR", "role": "BOWL", "is_overseas": False},
        "Rinku Singh":          {"team": "KKR", "role": "BAT",  "is_overseas": False},
        "Cameron Green":        {"team": "KKR", "role": "BOWL", "is_overseas": True},
        "Angkrish Raghuvanshi": {"team": "KKR", "role": "BAT",  "is_overseas": False},
        "Finn Allen":           {"team": "KKR", "role": "WK",   "is_overseas": True},
        "Tim Seifert":          {"team": "KKR", "role": "WK",   "is_overseas": True},
        "Umran Malik":          {"team": "KKR", "role": "BOWL", "is_overseas": False},
        "Vaibhav Arora":        {"team": "KKR", "role": "BOWL", "is_overseas": False},
        "Blessing Muzarabani":  {"team": "KKR", "role": "BOWL", "is_overseas": True},
        "Manish Pandey":        {"team": "KKR", "role": "BAT",  "is_overseas": False},
        "Rahul Tripathi":       {"team": "KKR", "role": "BAT",  "is_overseas": False},

        # ── GT ───────────────────────────────────────────────────────────────
        "Shubman Gill":         {"team": "GT",  "role": "BAT",  "is_overseas": False},
        "Rashid Khan":          {"team": "GT",  "role": "BOWL", "is_overseas": True},
        "Jos Buttler":          {"team": "GT",  "role": "WK",   "is_overseas": True},
        "Mohammed Siraj":       {"team": "GT",  "role": "BOWL", "is_overseas": False},
        "Kagiso Rabada":        {"team": "GT",  "role": "BOWL", "is_overseas": True},
        "Prasidh Krishna":      {"team": "GT",  "role": "BOWL", "is_overseas": False},
        "Sai Sudharsan":        {"team": "GT",  "role": "BAT",  "is_overseas": False},
        "Rahul Tewatia":        {"team": "GT",  "role": "BAT",  "is_overseas": False},
        "Shahrukh Khan":        {"team": "GT",  "role": "BAT",  "is_overseas": False},
        "Washington Sundar":    {"team": "GT",  "role": "BOWL", "is_overseas": False},
        "Ravi Sai Kishore":     {"team": "GT",  "role": "BOWL", "is_overseas": False},
        "Jason Holder":         {"team": "GT",  "role": "BOWL", "is_overseas": True},

        # ── LSG ──────────────────────────────────────────────────────────────
        "Rishabh Pant":         {"team": "LSG", "role": "WK",   "is_overseas": False},
        "Nicholas Pooran":      {"team": "LSG", "role": "WK",   "is_overseas": True},
        "Mayank Yadav":         {"team": "LSG", "role": "BOWL", "is_overseas": False},
        "Mohammed Shami":       {"team": "LSG", "role": "BOWL", "is_overseas": False},
        "Avesh Khan":           {"team": "LSG", "role": "BOWL", "is_overseas": False},
        "Ayush Badoni":         {"team": "LSG", "role": "BAT",  "is_overseas": False},
        "Mitchell Marsh":       {"team": "LSG", "role": "BAT",  "is_overseas": True},
        "Aiden Markram":        {"team": "LSG", "role": "BAT",  "is_overseas": True},
        "Shahbaz Ahmed":        {"team": "LSG", "role": "BOWL", "is_overseas": False},
        "Matthew Breetzke":     {"team": "LSG", "role": "BAT",  "is_overseas": True},
        "Abdul Samad":          {"team": "LSG", "role": "BAT",  "is_overseas": False},
        "Himmat Singh":         {"team": "LSG", "role": "BAT",  "is_overseas": False},
        "Digvesh Singh":        {"team": "LSG", "role": "BOWL", "is_overseas": False},

        # ── DC ───────────────────────────────────────────────────────────────
        "Axar Patel":           {"team": "DC",  "role": "BOWL", "is_overseas": False},
        "KL Rahul":             {"team": "DC",  "role": "WK",   "is_overseas": False},
        "Kuldeep Yadav":        {"team": "DC",  "role": "BOWL", "is_overseas": False},
        "Mitchell Starc":       {"team": "DC",  "role": "BOWL", "is_overseas": True},
        "Tristan Stubbs":       {"team": "DC",  "role": "WK",   "is_overseas": True},
        "Nitish Rana":          {"team": "DC",  "role": "BAT",  "is_overseas": False},
        "Abishek Porel":        {"team": "DC",  "role": "WK",   "is_overseas": False},
        "Ashutosh Sharma":      {"team": "DC",  "role": "BAT",  "is_overseas": False},
        "Karun Nair":           {"team": "DC",  "role": "BAT",  "is_overseas": False},
        "Lungi Ngidi":          {"team": "DC",  "role": "BOWL", "is_overseas": True},
        "Vipraj Nigam":         {"team": "DC",  "role": "BOWL", "is_overseas": False},
        "Pathum Nissanka":      {"team": "DC",  "role": "BAT",  "is_overseas": True},
        "Ben Duckett":          {"team": "DC",  "role": "WK",   "is_overseas": True},
        "Prithvi Shaw":         {"team": "DC",  "role": "BAT",  "is_overseas": False},
        "David Miller":         {"team": "DC",  "role": "BAT",  "is_overseas": True},

        # ── PBKS ─────────────────────────────────────────────────────────────
        "Shreyas Iyer":         {"team": "PBKS","role": "BAT",  "is_overseas": False},
        "Arshdeep Singh":       {"team": "PBKS","role": "BOWL", "is_overseas": False},
        "Yuzvendra Chahal":     {"team": "PBKS","role": "BOWL", "is_overseas": False},
        "Marcus Stoinis":       {"team": "PBKS","role": "BAT",  "is_overseas": True},
        "Marco Jansen":         {"team": "PBKS","role": "BOWL", "is_overseas": True},
        "Shashank Singh":       {"team": "PBKS","role": "BAT",  "is_overseas": False},
        "Nehal Wadhera":        {"team": "PBKS","role": "BAT",  "is_overseas": False},
        "Prabhsimran Singh":    {"team": "PBKS","role": "WK",   "is_overseas": False},
        "Priyansh Arya":        {"team": "PBKS","role": "BAT",  "is_overseas": False},
        "Azmatullah Omarzai":   {"team": "PBKS","role": "BOWL", "is_overseas": True},
        "Lockie Ferguson":      {"team": "PBKS","role": "BOWL", "is_overseas": True},
        "Harpreet Brar":        {"team": "PBKS","role": "BOWL", "is_overseas": False},
        "Cooper Connolly":      {"team": "PBKS","role": "BAT",  "is_overseas": True},

        # ── GT (additional) ───────────────────────────────────────────────────
        "Gudakesh Motie":       {"team": "GT",  "role": "BOWL", "is_overseas": True},
    }

    # ── POOLS SOURCED DIRECTLY FROM IPL_teams-1.xlsx ─────────────────────────
    excel_pools = {
        "Kazim": [
            "Rajat Patidar", "Devdutt Padikkal", "Shimron Hetmyer", "Dhruv Jurel",
            "Vaibhav Suryavanshi", "Priyansh Arya", "Ryan Rickelton", "Aiden Markram",
            "Angkrish Raghuvanshi", "Jos Buttler", "David Miller", "Ben Duckett",
            "Nitish Rana", "Prashant Veer", "Anshul Kamboj", "Axar Patel",
            "Gudakesh Motie", "Will Jacks", "Marcus Stoinis", "Shashank Singh",
            "Nitish Kumar Reddy", "Pat Cummins", "Jacob Duffy", "Josh Hazlewood",
            "Ravi Bishnoi", "Avesh Khan", "Ravi Sai Kishore", "Noor Ahmad",
            "Blessing Muzarabani", "Lockie Ferguson",
        ],
        "Aman": [
            "Phil Salt", "Yashasvi Jaiswal", "Prabhsimran Singh", "Nicholas Pooran",
            "Tim Seifert", "Shubman Gill", "Ayush Mhatre", "Ashutosh Sharma",
            "Rahul Tewatia", "Washington Sundar", "Cooper Connolly", "Azmatullah Omarzai",
            "Ravindra Jadeja", "Abhishek Sharma", "Harshal Patel", "Jofra Archer",
            "Yuzvendra Chahal", "AM Ghazanfar", "Digvesh Singh", "Prasidh Krishna",
            "Umran Malik", "Vipraj Nigam",
        ],
        "Aatish": [
            "Tim David", "Jitesh Sharma", "Nehal Wadhera", "Quinton de Kock",
            "Sherfane Rutherford", "Rohit Sharma", "Rishabh Pant", "Abdul Samad",
            "Matthew Breetzke", "Rahul Tripathi", "Finn Allen", "Shahrukh Khan",
            "Tristan Stubbs", "Pathum Nissanka", "MS Dhoni", "Dewald Brevis",
            "Shivam Dube", "Rashid Khan", "Sunil Narine", "Shahbaz Ahmed",
            "Hardik Pandya", "Donovan Ferreira", "Jacob Bethell", "Romario Shepherd",
            "Yash Dayal", "Deepak Chahar", "Vaibhav Arora", "Mohammed Siraj",
            "Kuldeep Yadav", "Khaleel Ahmed", "Mukesh Choudhary", "Rahul Chahar",
            "Mayank Yadav", "Harpreet Brar", "Tushar Deshpande",
        ],
        "Shrijeet": [
            "Travis Head", "Ishan Kishan", "Riyan Parag", "Shreyas Iyer",
            "Ayush Badoni", "Himmat Singh", "Manish Pandey", "Ajinkya Rahane",
            "Sai Sudharsan", "Prithvi Shaw", "Karun Nair", "Abishek Porel",
            "Sarfaraz Khan", "Ruturaj Gaikwad", "Ramakrishna Ghosh", "Mitchell Marsh",
            "Krunal Pandya", "Venkatesh Iyer", "Jaydev Unadkat", "Suyash Sharma",
            "Sandeep Sharma", "Arshdeep Singh", "Trent Boult", "Mohammed Shami",
            "Kagiso Rabada", "Mitchell Santner", "Kartik Sharma",
        ],
        "Nagle": [
            "Heinrich Klaasen", "Virat Kohli", "Suryakumar Yadav", "Rinku Singh",
            "KL Rahul", "Sanju Samson", "Cameron Green", "Tilak Varma",
            "Marco Jansen", "Liam Livingstone", "Bhuvneshwar Kumar", "Jasprit Bumrah",
            "Varun Chakaravarthy", "Lungi Ngidi", "Jason Holder", "Mitchell Starc",
        ],
    }
    initial_pools = excel_pools
    if not os.path.exists(DB_FILE): return {"selections": {}, "scores": {}, "pools": excel_pools, "player_master": pm}
    with open(DB_FILE, 'r') as f: return json.load(f)

def save_db(data):
    with open(DB_FILE, 'w') as f: json.dump(data, f)

st.set_page_config(page_title="Inner Circle IPL Fantasy", layout="wide", page_icon="🏏")

# ─── SPORTY CRICKET UI ────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Rajdhani:wght@400;600;700&family=Roboto+Condensed:wght@400;700&display=swap');

  /* ── Base & background ── */
  html, body, [data-testid="stAppViewContainer"] {
    background: #0a0e1a !important;
    color: #e8eaf0 !important;
    font-family: 'Rajdhani', sans-serif;
  }
  [data-testid="stAppViewContainer"] {
    background:
      radial-gradient(ellipse at 20% 0%, rgba(209,29,38,0.12) 0%, transparent 55%),
      radial-gradient(ellipse at 80% 0%, rgba(0,75,160,0.12) 0%, transparent 55%),
      linear-gradient(180deg, #0a0e1a 0%, #0d1220 100%);
    background-attachment: fixed;
  }
  [data-testid="stHeader"] { background: transparent; }
  [data-testid="stSidebar"] {
    background: linear-gradient(160deg, #0d1526 0%, #111827 100%) !important;
    border-right: 1px solid rgba(255,215,0,0.15);
  }

  /* ── Main title ── */
  .main-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 3.2rem;
    letter-spacing: 4px;
    text-align: center;
    background: linear-gradient(135deg, #ffd700 0%, #ff6b35 40%, #d11d26 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-shadow: none;
    margin-bottom: 0;
    line-height: 1;
  }
  .main-subtitle {
    text-align: center;
    font-family: 'Roboto Condensed', sans-serif;
    font-size: 0.85rem;
    letter-spacing: 6px;
    color: rgba(255,215,0,0.55);
    text-transform: uppercase;
    margin-top: 4px;
    margin-bottom: 20px;
  }
  .pitch-divider {
    height: 3px;
    background: linear-gradient(90deg, transparent, #ffd700 20%, #ff6b35 50%, #d11d26 80%, transparent);
    border-radius: 2px;
    margin: 8px 0 24px 0;
  }

  /* ── Tab overrides ── */
  [data-testid="stTabs"] [role="tablist"] {
    gap: 4px;
    border-bottom: 2px solid rgba(255,215,0,0.2);
    background: rgba(255,255,255,0.02);
    border-radius: 8px 8px 0 0;
    padding: 4px 6px 0;
  }
  [data-testid="stTabs"] [role="tab"] {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.1rem;
    letter-spacing: 2px;
    color: rgba(200,210,230,0.6) !important;
    border: none !important;
    border-radius: 6px 6px 0 0 !important;
    padding: 8px 20px !important;
    background: transparent !important;
    transition: all 0.2s ease;
  }
  [data-testid="stTabs"] [role="tab"]:hover {
    color: #ffd700 !important;
    background: rgba(255,215,0,0.06) !important;
  }
  [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: #ffd700 !important;
    background: rgba(255,215,0,0.1) !important;
    border-bottom: 2px solid #ffd700 !important;
  }

  /* ── Player card ── */
  .player-card {
    background: linear-gradient(135deg, rgba(255,255,255,0.04) 0%, rgba(255,255,255,0.02) 100%);
    border: 1px solid rgba(255,255,255,0.08);
    border-left: 3px solid #ccc;
    border-radius: 8px;
    padding: 8px 10px;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 10px;
    transition: border-color 0.2s, background 0.2s;
    min-height: 56px;
  }
  .player-card:hover {
    background: rgba(255,215,0,0.06);
  }
  .player-name {
    font-family: 'Roboto Condensed', sans-serif;
    font-size: 13px;
    font-weight: 700;
    color: #e8eaf0;
    line-height: 1.2;
  }
  .player-meta {
    font-size: 10px;
    color: rgba(200,210,230,0.5);
    font-family: 'Rajdhani', sans-serif;
    letter-spacing: 0.5px;
  }
  .team-badge {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 11px;
    letter-spacing: 1px;
    padding: 2px 6px;
    border-radius: 4px;
    color: white;
    white-space: nowrap;
  }
  .role-chip {
    font-size: 9px;
    font-family: 'Roboto Condensed', sans-serif;
    font-weight: 700;
    letter-spacing: 1px;
    padding: 2px 5px;
    border-radius: 3px;
    border: 1px solid rgba(255,255,255,0.15);
    color: rgba(230,240,255,0.75);
  }

  /* ── Sidebar widgets ── */
  .sidebar-section {
    background: rgba(255,215,0,0.05);
    border: 1px solid rgba(255,215,0,0.15);
    border-radius: 8px;
    padding: 10px 12px;
    margin-bottom: 10px;
  }
  .sidebar-week-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.05rem;
    letter-spacing: 2px;
    color: #ffd700;
    margin-bottom: 6px;
  }
  .match-pill {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 3px 10px;
    font-size: 11px;
    font-family: 'Roboto Condensed', sans-serif;
    color: #c8d2e6;
    margin: 2px 0;
    display: inline-block;
  }
  .team-stat-row {
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    font-family: 'Rajdhani', sans-serif;
    color: #b0bec5;
    padding: 2px 0;
    border-bottom: 1px solid rgba(255,255,255,0.04);
  }
  .team-stat-name { font-weight: 700; }
  .team-stat-count {
    background: rgba(255,215,0,0.15);
    color: #ffd700;
    font-weight: 700;
    padding: 0 6px;
    border-radius: 10px;
    font-size: 11px;
  }

  /* ── Squad status bar ── */
  .squad-status {
    background: linear-gradient(135deg, rgba(0,75,160,0.2), rgba(209,29,38,0.15));
    border: 1px solid rgba(255,215,0,0.2);
    border-radius: 10px;
    padding: 10px 16px;
    font-family: 'Roboto Condensed', sans-serif;
    font-size: 14px;
    color: #e8eaf0;
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
    margin-bottom: 12px;
    align-items: center;
  }
  .stat-pill {
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .stat-label { color: rgba(200,210,230,0.6); font-size: 12px; }
  .stat-value {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 18px;
    color: #ffd700;
  }
  .stat-max { font-size: 12px; color: rgba(200,210,230,0.4); }

  /* ── View all squads ── */
  .squad-view-box {
    background: linear-gradient(160deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02));
    border: 1px solid rgba(255,255,255,0.1);
    border-top: 2px solid #ffd700;
    border-radius: 10px;
    padding: 12px;
    margin-top: 4px;
  }
  .squad-mgr-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.3rem;
    letter-spacing: 2px;
    color: #ffd700;
    margin-bottom: 8px;
    text-align: center;
  }
  .squad-player-row {
    font-family: 'Roboto Condensed', sans-serif;
    font-size: 12px;
    padding: 5px 4px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: #c8d2e6;
  }
  .squad-player-row:hover { background: rgba(255,215,0,0.04); }
  .cap-badge {
    background: linear-gradient(135deg, #ffd700, #ff8c00);
    color: #0a0e1a;
    padding: 2px 7px;
    border-radius: 4px;
    font-size: 10px;
    font-family: 'Bebas Neue', sans-serif;
    letter-spacing: 1px;
  }

  /* ── Leaderboard ── */
  .lb-table { width: 100%; border-collapse: collapse; }
  .lb-table th {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1rem;
    letter-spacing: 2px;
    color: #ffd700;
    background: rgba(255,215,0,0.08);
    padding: 10px 14px;
    text-align: left;
    border-bottom: 2px solid rgba(255,215,0,0.3);
  }
  .lb-table td {
    font-family: 'Roboto Condensed', sans-serif;
    font-size: 14px;
    color: #c8d2e6;
    padding: 9px 14px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
  }
  .lb-table tr:first-child td { color: #ffd700; font-weight: 700; font-size: 15px; }
  .lb-table tr:hover td { background: rgba(255,215,0,0.04); }
  .rank-gold   { color: #ffd700; font-family: 'Bebas Neue', sans-serif; font-size: 1.1rem; }
  .rank-silver { color: #b0bec5; font-family: 'Bebas Neue', sans-serif; }
  .rank-bronze { color: #cd7f32; font-family: 'Bebas Neue', sans-serif; }

  /* ── Streamlit native overrides ── */
  .stSelectbox label, .stTextInput label, .stNumberInput label, .stCheckbox label {
    color: rgba(200,210,230,0.8) !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 600;
    font-size: 13px;
  }
  .stSelectbox > div > div,
  .stTextInput > div > div > input {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    color: #e8eaf0 !important;
    border-radius: 8px !important;
    font-family: 'Roboto Condensed', sans-serif !important;
  }
  .stButton > button {
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 1.2rem !important;
    letter-spacing: 3px !important;
    border-radius: 8px !important;
    border: none !important;
    background: linear-gradient(135deg, #ffd700 0%, #ff8c00 50%, #d11d26 100%) !important;
    color: white !important;
    padding: 10px 24px !important;
    transition: opacity 0.2s, transform 0.1s !important;
    width: 100%;
  }
  .stButton > button:hover { opacity: 0.9 !important; transform: translateY(-1px) !important; }
  .stButton > button:active { transform: translateY(0) !important; }

  .stAlert { border-radius: 8px !important; font-family: 'Rajdhani', sans-serif !important; }

  /* ── Section headers ── */
  .section-header {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.5rem;
    letter-spacing: 3px;
    color: #ffd700;
    border-left: 4px solid #d11d26;
    padding-left: 12px;
    margin: 16px 0 12px;
  }

  /* ── Lock / unlock status ── */
  .lock-status {
    font-family: 'Roboto Condensed', sans-serif;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 1px;
    padding: 6px 12px;
    border-radius: 20px;
    display: inline-block;
    margin-top: 4px;
  }
  .lock-open  { background: rgba(76,175,80,0.15); color: #81c784; border: 1px solid rgba(76,175,80,0.3); }
  .lock-closed{ background: rgba(244,67,54,0.15); color: #e57373; border: 1px solid rgba(244,67,54,0.3); }

  /* Admin section */
  .admin-box {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 12px;
  }

  /* Scrollbar */
  ::-webkit-scrollbar { width: 6px; height: 6px; }
  ::-webkit-scrollbar-track { background: #0a0e1a; }
  ::-webkit-scrollbar-thumb { background: rgba(255,215,0,0.3); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── Page Header ──────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">🏏 Inner Circle IPL Fantasy 2026</div>', unsafe_allow_html=True)
st.markdown('<div class="main-subtitle">Pick Your XI · Rule the Season · Outsmart Your Rivals</div>', unsafe_allow_html=True)
st.markdown('<div class="pitch-divider"></div>', unsafe_allow_html=True)

db = load_db()

# ── Sidebar ──────────────────────────────────────────────────────────────────
st.sidebar.markdown(
    '<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.4rem;letter-spacing:3px;'
    'color:#ffd700;margin-bottom:12px;text-align:center;">🗓️ Season Calendar</div>',
    unsafe_allow_html=True
)

active_week_name = st.sidebar.selectbox("Select Week", list(SEASON_WEEKS.keys()), label_visibility="collapsed")
week_config = SEASON_WEEKS[active_week_name]
lock_time = datetime.strptime(week_config["lock"], "%Y-%m-%d %H:%M:%S")
is_locked = datetime.now() > lock_time

if is_locked:
    st.sidebar.markdown(f'<span class="lock-status lock-closed">🔒 Locked — {lock_time.strftime("%I:%M %p, %b %d")}</span>', unsafe_allow_html=True)
else:
    st.sidebar.markdown(f'<span class="lock-status lock-open">🔓 Open · Closes {lock_time.strftime("%I:%M %p, %b %d")}</span>', unsafe_allow_html=True)

matches_this_week = week_config["matches"]
st.sidebar.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
st.sidebar.markdown('<div class="sidebar-week-title">⚡ THIS WEEK\'S MATCHES</div>', unsafe_allow_html=True)
for mid, fixture in matches_this_week.items():
    st.sidebar.markdown(f'<div class="match-pill">🏟️ {fixture}</div>', unsafe_allow_html=True)
st.sidebar.markdown('</div>', unsafe_allow_html=True)

all_teams_week = []
for f in matches_this_week.values(): all_teams_week.extend(f.split(" vs "))
team_counts = Counter(all_teams_week)
st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
st.sidebar.markdown('<div class="sidebar-week-title">🏆 TEAMS IN ACTION</div>', unsafe_allow_html=True)
for team, count in sorted(team_counts.items()):
    color = TEAM_COLORS.get(team, "#888")
    st.sidebar.markdown(
        f'<div class="team-stat-row">'
        f'<span class="team-stat-name" style="color:{color}">▮ {team}</span>'
        f'<span class="team-stat-count">{count} match{"es" if count>1 else ""}</span>'
        f'</div>',
        unsafe_allow_html=True
    )
st.sidebar.markdown('</div>', unsafe_allow_html=True)

# ── Main Tabs ─────────────────────────────────────────────────────────────────
t1, t_view, t2, t_admin = st.tabs(["🏏  MY SQUAD", "👀  ALL SQUADS", "📊  STANDINGS", "🛡️  ADMIN"])

# ─────────────────────────────────────────────────────────────────────────────
with t1:
    user = st.selectbox("Manager Name", list(db["pools"].keys()))
    pool = db["pools"].get(user, [])
    saved = db["selections"].get(active_week_name, {}).get(user, {"squad": [], "cap": ""})
    state_key = f"sel_{user}_{active_week_name}"
    if state_key not in st.session_state: st.session_state[state_key] = list(saved["squad"])
    if is_locked: st.warning("🔒 Deadline passed — squad is locked for this week.")

    # FILTERS
    f1, f2, f3 = st.columns([2, 1, 1])
    search  = f1.text_input("🔍 Search player", key="src_v10", placeholder="Type name...")
    team_f  = f2.selectbox("Team", ["All"] + sorted(list(TEAM_COLORS.keys())), key="team_v10")
    role_f  = f3.selectbox("Role", ["All", "BAT", "BOWL", "WK"], key="rol_v10")

    cols = st.columns(2)
    display_idx = 0
    for p in sorted(pool):
        info = db["player_master"].get(p, {"team": "IPL", "role": "BAT", "is_overseas": False})
        match_search = search.lower() in p.lower()
        match_team   = (team_f == "All" or info["team"] == team_f)
        match_role   = (role_f == "All" or info["role"] == role_f)

        if match_search and match_team and match_role:
            team_color  = TEAM_COLORS.get(info["team"], "#666")
            role_icons  = {"BAT": "🏏", "BOWL": "🎳", "WK": "🧤"}
            overseas_tag = " ✈️" if info["is_overseas"] else ""
            with cols[display_idx % 2]:
                c_cell, c_box = st.columns([5, 1])
                with c_cell:
                    st.markdown(f'''
                    <div class="player-card" style="border-left-color:{team_color};">
                      <div style="flex-grow:1;">
                        <div class="player-name">{p}{overseas_tag}</div>
                        <div style="display:flex;gap:6px;margin-top:3px;align-items:center;">
                          <span class="team-badge" style="background:{team_color};">{info["team"]}</span>
                          <span class="role-chip">{role_icons.get(info["role"],"🏏")} {info["role"]}</span>
                        </div>
                      </div>
                    </div>''', unsafe_allow_html=True)
                with c_box:
                    checked = st.checkbox("", key=f"cb_{user}_{p}",
                                         value=(p in st.session_state[state_key]),
                                         disabled=is_locked)
                    if not is_locked:
                        if checked and p not in st.session_state[state_key]:
                            st.session_state[state_key].append(p); st.rerun()
                        elif not checked and p in st.session_state[state_key]:
                            st.session_state[state_key].remove(p); st.rerun()
            display_idx += 1

    final_squad = st.session_state[state_key]
    os_count   = sum(1 for p in final_squad if db["player_master"].get(p, {}).get("is_overseas"))
    wk_count   = sum(1 for p in final_squad if db["player_master"].get(p, {}).get("role") == "WK")
    bowl_count  = sum(1 for p in final_squad if db["player_master"].get(p, {}).get("role") == "BOWL")

    # Squad status bar
    sq_color = "#ffd700" if len(final_squad) == 11 else "#e57373"
    os_color = "#ffd700" if os_count <= 4 else "#e57373"
    wk_color = "#ffd700" if wk_count >= 1 else "#e57373"
    bw_color = "#ffd700" if bowl_count >= 4 else "#e57373"
    st.markdown(f'''
    <div class="squad-status">
      <div class="stat-pill">
        <span class="stat-label">SQUAD</span>
        <span class="stat-value" style="color:{sq_color};">{len(final_squad)}</span>
        <span class="stat-max">/11</span>
      </div>
      <div class="stat-pill">
        <span class="stat-label">✈️ OVERSEAS</span>
        <span class="stat-value" style="color:{os_color};">{os_count}</span>
        <span class="stat-max">/4 max</span>
      </div>
      <div class="stat-pill">
        <span class="stat-label">🧤 KEEPERS</span>
        <span class="stat-value" style="color:{wk_color};">{wk_count}</span>
        <span class="stat-max">min 1</span>
      </div>
      <div class="stat-pill">
        <span class="stat-label">🎳 BOWLERS</span>
        <span class="stat-value" style="color:{bw_color};">{bowl_count}</span>
        <span class="stat-max">/4 min</span>
      </div>
    </div>
    ''', unsafe_allow_html=True)

    if len(final_squad) == 11 and os_count <= 4 and wk_count >= 1 and bowl_count >= 4:
        cap = st.selectbox("🛡️ Select Captain (2× points)",
                           final_squad,
                           index=(final_squad.index(saved["cap"]) if saved["cap"] in final_squad else 0),
                           disabled=is_locked)
        if not is_locked and st.button("🚀  LOCK IN SQUAD", type="primary", use_container_width=True):
            if active_week_name not in db["selections"]: db["selections"][active_week_name] = {}
            db["selections"][active_week_name][user] = {"squad": final_squad, "cap": cap}
            save_db(db); st.success("✅ Squad saved! Good luck this week!")
    else:
        st.warning("⚠️ Complete your squad: exactly 11 players | max 4 overseas | min 1 keeper | min 4 bowlers")

# ─────────────────────────────────────────────────────────────────────────────
with t_view:
    st.markdown('<div class="section-header">ALL MANAGERS\' SQUADS</div>', unsafe_allow_html=True)
    cols = st.columns(len(db["pools"]))
    for i, mgr in enumerate(db["pools"].keys()):
        with cols[i]:
            s_data = db["selections"].get(active_week_name, {}).get(mgr, None)
            st.markdown(f'<div class="squad-mgr-title">⚡ {mgr}</div>', unsafe_allow_html=True)
            if s_data:
                st.markdown('<div class="squad-view-box">', unsafe_allow_html=True)
                for player in sorted(s_data["squad"]):
                    info = db["player_master"].get(player, {})
                    cap_tag = '<span class="cap-badge">CAP</span>' if player == s_data["cap"] else ""
                    t_color = TEAM_COLORS.get(info.get("team",""), "#888")
                    st.markdown(
                        f'<div class="squad-player-row">'
                        f'<span><span style="color:{t_color};font-size:9px;">●</span> {player} '
                        f'<span style="color:rgba(200,210,230,0.4);font-size:10px;">({info.get("team","")})</span>'
                        f'</span>{cap_tag}</div>',
                        unsafe_allow_html=True
                    )
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown(
                    '<div style="text-align:center;padding:20px;color:rgba(200,210,230,0.3);'
                    'font-family:\'Rajdhani\',sans-serif;border:1px dashed rgba(255,255,255,0.08);'
                    'border-radius:8px;font-size:13px;">No squad selected</div>',
                    unsafe_allow_html=True
                )

# ─────────────────────────────────────────────────────────────────────────────
with t2:
    st.markdown('<div class="section-header">📊 LEADERBOARD</div>', unsafe_allow_html=True)
    lb_data = []
    week_keys = list(SEASON_WEEKS.keys())
    for m in db["pools"].keys():
        total, week_pts = 0, 0
        for idx, wk_key in enumerate(week_keys):
            sel = db["selections"].get(wk_key, {}).get(m, None)
            if not sel:
                for prev_wk in reversed(week_keys[:idx]):
                    lookback = db["selections"].get(prev_wk, {}).get(m, None)
                    if lookback: sel = lookback; break
            w_sum = 0
            if sel:
                for p in sel["squad"]:
                    p_pts = 0
                    for mid in SEASON_WEEKS[wk_key]["matches"]:
                        s = db["scores"].get(p, {}).get(mid, {"r":0, "w":0, "c":0, "s":0})
                        p_pts += (s.get("r",0)*1) + (s.get("w",0)*20) + (s.get("c",0)*5) + (s.get("s",0)*5)
                    if p == sel["cap"]: p_pts *= 2
                    w_sum += p_pts
            total += w_sum
            if wk_key == active_week_name: week_pts = w_sum
        lb_data.append({"Manager": m, "Weekly": week_pts, "Total": total})

    sorted_lb = sorted(lb_data, key=lambda x: x['Total'], reverse=True)
    rank_icons = {0: "🥇", 1: "🥈", 2: "🥉"}

    # Build HTML table
    rows_html = ""
    for rank, row in enumerate(sorted_lb):
        icon = rank_icons.get(rank, f"#{rank+1}")
        rows_html += (
            f"<tr>"
            f"<td style='text-align:center;font-family:\"Bebas Neue\",sans-serif;font-size:1.1rem;'>{icon}</td>"
            f"<td style='font-weight:700;color:#e8eaf0;'>{row['Manager']}</td>"
            f"<td style='text-align:right;color:#64b5f6;'>{row['Weekly']}</td>"
            f"<td style='text-align:right;color:#ffd700;font-family:\"Bebas Neue\",sans-serif;font-size:1.1rem;'>{row['Total']}</td>"
            f"</tr>"
        )

    st.markdown(f"""
    <table class="lb-table">
      <thead>
        <tr>
          <th style="text-align:center;">RANK</th>
          <th>MANAGER</th>
          <th style="text-align:right;">THIS WEEK</th>
          <th style="text-align:right;">TOTAL PTS</th>
        </tr>
      </thead>
      <tbody>{rows_html}</tbody>
    </table>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
with t_admin:
    st.markdown('<div class="section-header">🛡️ SCORE MANAGEMENT</div>', unsafe_allow_html=True)
    st.markdown('<div class="admin-box">', unsafe_allow_html=True)
    sel_mid = st.selectbox("Select Match", list(matches_this_week.keys()),
                           format_func=lambda x: f"{x} — {matches_this_week[x]}")
    teams = matches_this_week[sel_mid].split(" vs ")
    all_p = set()
    for wk in db["selections"].values():
        for m_sel in wk.values(): all_p.update(m_sel["squad"])
    eligible = [p for p in all_p if db["player_master"].get(p, {}).get("team") in teams]

    if eligible:
        for p in sorted(eligible):
            cur = db["scores"].get(p, {}).get(sel_mid, {"r":0, "w":0, "c":0, "s":0})
            info = db["player_master"].get(p, {})
            t_color = TEAM_COLORS.get(info.get("team",""), "#888")
            cols = st.columns([2, 1, 1, 1, 1])
            cols[0].markdown(
                f'<div style="padding:8px 0;font-family:\'Roboto Condensed\',sans-serif;font-size:13px;">'
                f'<span style="color:{t_color};">●</span> <b>{p}</b> '
                f'<span style="color:rgba(200,210,230,0.4);font-size:11px;">({info.get("team","")})</span></div>',
                unsafe_allow_html=True
            )
            r = cols[1].number_input("Runs",    0, 200, cur["r"], key=f"r_{p}", label_visibility="collapsed")
            w = cols[2].number_input("Wkts",    0, 10,  cur["w"], key=f"w_{p}", label_visibility="collapsed")
            c = cols[3].number_input("Catches", 0, 10,  cur["c"], key=f"c_{p}", label_visibility="collapsed")
            s = cols[4].number_input("Stump",   0, 10,  cur["s"], key=f"s_{p}", label_visibility="collapsed")
            if {"r":r,"w":w,"c":c,"s":s} != cur:
                if p not in db["scores"]: db["scores"][p] = {}
                db["scores"][p][sel_mid] = {"r":r,"w":w,"c":c,"s":s}
    else:
        st.info("No eligible players found for this match. Squads may not have been submitted yet.")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🚀  PUSH SCORES", type="primary", use_container_width=True):
        save_db(db); st.success("✅ Scores saved successfully!")

    st.markdown('<div class="section-header">⚠️ DANGER ZONE</div>', unsafe_allow_html=True)
    st.markdown('<div class="admin-box">', unsafe_allow_html=True)
    reset_confirm = st.checkbox("☢️ Confirm: Permanently delete ALL selections and scores.")
    if reset_confirm and st.button("💣  CLEAR ALL DATA", type="primary"):
        if os.path.exists(DB_FILE): os.remove(DB_FILE)
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
