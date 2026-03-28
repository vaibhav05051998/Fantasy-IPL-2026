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
        "Angkrish Raghuvanshi": {"team": "KKR", "role": "WK",   "is_overseas": False},
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

        # ── Unattached / not confirmed in any final 2026 squad ───────────────
        "Gudakesh Motie":       {"team": "IPL", "role": "BOWL", "is_overseas": True},
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
    with open(DB_FILE, 'r') as f: db = json.load(f)
    # ── Always sync player_master from code (picks up any role/team edits) ──
    db['player_master'] = pm
    return db

def save_db(data):
    with open(DB_FILE, 'w') as f: json.dump(data, f)


# ── Cricbuzz match IDs for IPL 2026 (from cricbuzz.com/cricket-match/live) ───
# Format: "M01": cricbuzz_match_id  — admin pastes the 5-digit ID from URL
# e.g. https://www.cricbuzz.com/live-cricket-scores/112233/rcb-vs-srh-...
# These are pre-filled where known, admin can override in UI
CRICBUZZ_MATCH_IDS = {
    "M01": "116484",  # RCB vs SRH  Mar 28
    "M02": "",        # MI  vs KKR  Mar 29
    "M03": "",        # RR  vs CSK  Mar 30
    "M04": "",        # PBKS vs GT  Mar 30
    "M05": "",        # LSG vs DC   Apr 01
    "M06": "",        # KKR vs SRH  Apr 02
    "M07": "",        # CSK vs PBKS Apr 03
}

import re, requests
from difflib import SequenceMatcher

def _fuzzy(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def _best_match(name, candidates, threshold=0.55):
    """Return the best fuzzy match from candidates, or None."""
    scored = [(c, _fuzzy(name, c)) for c in candidates]
    scored.sort(key=lambda x: -x[1])
    if scored and scored[0][1] >= threshold:
        return scored[0][0]
    # Also try matching last name only
    last = name.split()[-1]
    for c in candidates:
        if last.lower() in c.lower() or c.lower().split()[-1] == last.lower():
            return c
    return None

@st.cache_data(ttl=120, show_spinner=False)
def fetch_cricbuzz_scorecard(cb_match_id: str):
    """
    Scrape batting + bowling scorecard from Cricbuzz mobile site.
    Returns dict: { player_name: { "r":int, "w":int, "c":int, "s":int } }
    plus "raw_batting" and "raw_bowling" for display.
    Returns None on error.
    """
    url = f"https://www.cricbuzz.com/api/cricket-match/{cb_match_id}/full-commentary/0"
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15",
        "Accept": "application/json",
        "Referer": "https://www.cricbuzz.com/",
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            return None
        data = r.json()
        return _parse_cricbuzz_json(data)
    except Exception:
        pass

    # Fallback: try the scorecard page HTML
    url2 = f"https://m.cricbuzz.com/cricket-match/{cb_match_id}/full-scorecard"
    try:
        r2 = requests.get(url2, headers={**headers, "Accept": "text/html"}, timeout=10)
        if r2.status_code == 200:
            return _parse_cricbuzz_html(r2.text)
    except Exception:
        pass
    return None

def _parse_cricbuzz_json(data):
    """Parse Cricbuzz JSON API response into player stats."""
    stats = {}
    raw_bat, raw_bowl = [], []
    try:
        innings_list = data.get("scoreCard", [])
        for inn in innings_list:
            # Batting
            bat_list = inn.get("batTeamDetails", {}).get("batsmenData", {})
            if isinstance(bat_list, dict):
                bat_list = list(bat_list.values())
            for b in bat_list:
                name  = b.get("batName", "").strip()
                runs  = int(b.get("runs", 0))
                diss  = b.get("outDesc", "").lower()
                if not name: continue
                if name not in stats: stats[name] = {"r":0,"w":0,"c":0.0,"s":0,"mom":0}
                stats[name]["r"] += runs
                raw_bat.append({"name": name, "runs": runs, "dismissal": diss})
                # Catch / stumping from dismissal
                if "c " in diss and "b " in diss:
                    fielder = re.search(r"c\s+([\w\s]+)\s+b", diss)
                    if fielder:
                        fn = fielder.group(1).strip()
                        if fn not in stats: stats[fn] = {"r":0,"w":0,"c":0.0,"s":0,"mom":0}
                        stats[fn]["c"] += 1
                elif "st " in diss:
                    keeper = re.search(r"st\s+([\w\s]+)\s+b", diss)
                    if keeper:
                        kn = keeper.group(1).strip()
                        if kn not in stats: stats[kn] = {"r":0,"w":0,"c":0.0,"s":0,"mom":0}
                        stats[kn]["s"] += 1
                elif "run out" in diss:
                    ro = re.search(r"run out\s*[\(\[]([\w\s/]+)[\)\]]", diss)
                    if ro:
                        rplayers = [x.strip() for x in re.split(r"[/&]", ro.group(1))]
                        share = 1.0 if len(rplayers) == 1 else 0.5
                        for rp in rplayers:
                            if not rp: continue
                            if rp not in stats: stats[rp] = {"r":0,"w":0,"c":0.0,"s":0,"mom":0}
                            stats[rp]["c"] += share  # run-out stored as catch field

            # Bowling
            bowl_list = inn.get("bowlTeamDetails", {}).get("bowlersData", {})
            if isinstance(bowl_list, dict):
                bowl_list = list(bowl_list.values())
            for bw in bowl_list:
                name  = bw.get("bowlName", "").strip()
                wkts  = int(bw.get("wickets", 0))
                if not name: continue
                if name not in stats: stats[name] = {"r":0,"w":0,"c":0.0,"s":0,"mom":0}
                stats[name]["w"] += wkts
                raw_bowl.append({"name": name, "wickets": wkts})

    except Exception:
        pass

    return {"stats": stats, "raw_batting": raw_bat, "raw_bowling": raw_bowl}

def _parse_cricbuzz_html(html):
    """Fallback HTML parser for Cricbuzz mobile scorecard."""
    stats = {}
    raw_bat, raw_bowl = [], []
    try:
        from html.parser import HTMLParser
        # Simple regex-based extraction from mobile HTML
        # Batting rows
        bat_rows = re.findall(
            r'<td[^>]*class="[^"]*batsman[^"]*"[^>]*>(.*?)</td>.*?<td[^>]*>(\d+)</td>',
            html, re.S
        )
        for name_html, runs in bat_rows:
            name = re.sub(r'<[^>]+>', '', name_html).strip()
            if name:
                if name not in stats: stats[name] = {"r":0,"w":0,"c":0.0,"s":0,"mom":0}
                stats[name]["r"] += int(runs)
                raw_bat.append({"name": name, "runs": int(runs), "dismissal": ""})

        bowl_rows = re.findall(
            r'<td[^>]*class="[^"]*bowler[^"]*"[^>]*>(.*?)</td>.*?<td[^>]*>(\d+)</td>',
            html, re.S
        )
        for name_html, wkts in bowl_rows:
            name = re.sub(r'<[^>]+>', '', name_html).strip()
            if name:
                if name not in stats: stats[name] = {"r":0,"w":0,"c":0.0,"s":0,"mom":0}
                stats[name]["w"] += int(wkts)
                raw_bowl.append({"name": name, "wickets": int(wkts)})
    except Exception:
        pass

    return {"stats": stats, "raw_batting": raw_bat, "raw_bowling": raw_bowl}

def map_fetched_to_pool(fetched_stats, player_master):
    """
    Fuzzy-match scraped player names → canonical names in player_master.
    Returns { canonical_name: {r,w,c,s,mom} }
    """
    pm_names = list(player_master.keys())
    mapped, unmatched = {}, []
    for fetched_name, vals in fetched_stats.items():
        match = _best_match(fetched_name, pm_names)
        if match:
            if match in mapped:
                # Merge (shouldn't happen but safe)
                mapped[match]["r"] += vals["r"]
                mapped[match]["w"] += vals["w"]
                mapped[match]["c"] += vals["c"]
                mapped[match]["s"] += vals["s"]
            else:
                mapped[match] = dict(vals)
        else:
            unmatched.append(fetched_name)
    return mapped, unmatched


st.set_page_config(page_title="Inner Circle IPL Fantasy", layout="wide", page_icon="🏏")

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Rajdhani:wght@400;600;700&family=Roboto+Condensed:wght@400;700&display=swap');
  html, body, [data-testid="stAppViewContainer"] { background: #2a3550 !important; color: #f5f7ff !important; font-family: 'Rajdhani', sans-serif; }
  [data-testid="stAppViewContainer"] {
    background: radial-gradient(ellipse at 20% 0%, rgba(209,29,38,0.15) 0%, transparent 50%),
      radial-gradient(ellipse at 80% 0%, rgba(0,75,160,0.15) 0%, transparent 50%),
      linear-gradient(180deg, #2a3550 0%, #2e3a58 100%); background-attachment: fixed;
  }
  [data-testid="stHeader"] { background: transparent; }
  [data-testid="stSidebar"] { background: linear-gradient(160deg, #2e3d5c 0%, #283555 100%) !important; border-right: 2px solid rgba(255,215,0,0.30); }
  .main-title { font-family: 'Bebas Neue', sans-serif; font-size: 3.2rem; letter-spacing: 4px; text-align: center; background: linear-gradient(135deg, #ffd700 0%, #ff6b35 40%, #d11d26 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 0; line-height: 1; }
  .main-subtitle { text-align: center; font-family: 'Roboto Condensed', sans-serif; font-size: 0.85rem; letter-spacing: 6px; color: rgba(255,215,0,0.70); text-transform: uppercase; margin-top: 4px; margin-bottom: 20px; }
  .pitch-divider { height: 3px; background: linear-gradient(90deg, transparent, #ffd700 20%, #ff6b35 50%, #d11d26 80%, transparent); border-radius: 2px; margin: 8px 0 24px 0; }
  [data-testid="stTabs"] [role="tablist"] { gap: 4px; border-bottom: 2px solid rgba(255,215,0,0.3); background: rgba(0,0,0,0.15); border-radius: 8px 8px 0 0; padding: 4px 6px 0; }
  [data-testid="stTabs"] [role="tab"] { font-family: 'Bebas Neue', sans-serif; font-size: 1.1rem; letter-spacing: 2px; color: rgba(230,235,255,0.75) !important; border: none !important; border-radius: 6px 6px 0 0 !important; padding: 8px 20px !important; background: transparent !important; transition: all 0.2s ease; }
  [data-testid="stTabs"] [role="tab"]:hover { color: #ffd700 !important; background: rgba(255,215,0,0.08) !important; }
  [data-testid="stTabs"] [role="tab"][aria-selected="true"] { color: #ffd700 !important; background: rgba(255,215,0,0.12) !important; border-bottom: 2px solid #ffd700 !important; }
  .player-card { background: rgba(255,255,255,0.10); border: 1px solid rgba(255,255,255,0.18); border-left: 3px solid #ccc; border-radius: 8px; padding: 8px 10px; margin-bottom: 6px; display: flex; align-items: center; gap: 10px; transition: border-color 0.2s, background 0.2s; min-height: 56px; }
  .player-card:hover { background: rgba(255,215,0,0.10); }
  .player-name { font-family: 'Roboto Condensed', sans-serif; font-size: 13px; font-weight: 700; color: #ffffff; line-height: 1.2; }
  .team-badge { font-family: 'Bebas Neue', sans-serif; font-size: 11px; letter-spacing: 1px; padding: 2px 6px; border-radius: 4px; color: white; white-space: nowrap; }
  .role-chip { font-size: 9px; font-family: 'Roboto Condensed', sans-serif; font-weight: 700; letter-spacing: 1px; padding: 2px 5px; border-radius: 3px; border: 1px solid rgba(255,255,255,0.30); color: rgba(240,245,255,0.95); }
  .sidebar-section { background: rgba(255,215,0,0.10); border: 1px solid rgba(255,215,0,0.30); border-radius: 8px; padding: 10px 12px; margin-bottom: 10px; }
  .sidebar-week-title { font-family: 'Bebas Neue', sans-serif; font-size: 1.05rem; letter-spacing: 2px; color: #ffd700; margin-bottom: 6px; }
  .match-pill { background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.25); border-radius: 20px; padding: 3px 10px; font-size: 11px; font-family: 'Roboto Condensed', sans-serif; color: #eef2ff; margin: 2px 0; display: inline-block; }
  .team-stat-row { display: flex; justify-content: space-between; font-size: 12px; font-family: 'Rajdhani', sans-serif; color: #d8e0f5; padding: 2px 0; border-bottom: 1px solid rgba(255,255,255,0.08); }
  .team-stat-name { font-weight: 700; }
  .team-stat-count { background: rgba(255,215,0,0.20); color: #ffd700; font-weight: 700; padding: 0 6px; border-radius: 10px; font-size: 11px; }
  .squad-status { background: linear-gradient(135deg, rgba(0,75,160,0.35), rgba(209,29,38,0.28)); border: 1px solid rgba(255,215,0,0.45); border-radius: 10px; padding: 10px 16px; font-family: 'Roboto Condensed', sans-serif; font-size: 14px; color: #f5f7ff; display: flex; gap: 20px; flex-wrap: wrap; margin-bottom: 12px; align-items: center; }
  .stat-pill { display: flex; align-items: center; gap: 6px; }
  .stat-label { color: rgba(225,235,255,0.90); font-size: 12px; font-weight: 700; }
  .stat-value { font-family: 'Bebas Neue', sans-serif; font-size: 20px; color: #ffd700; }
  .stat-max { font-size: 12px; color: rgba(210,225,255,0.70); }
  .squad-view-box { background: rgba(255,255,255,0.10); border: 1px solid rgba(255,255,255,0.20); border-top: 2px solid #ffd700; border-radius: 10px; padding: 12px; margin-top: 4px; }
  .squad-mgr-title { font-family: 'Bebas Neue', sans-serif; font-size: 1.3rem; letter-spacing: 2px; color: #ffd700; margin-bottom: 8px; text-align: center; }
  .squad-player-row { font-family: 'Roboto Condensed', sans-serif; font-size: 12px; padding: 5px 4px; border-bottom: 1px solid rgba(255,255,255,0.10); display: flex; justify-content: space-between; align-items: center; color: #eef2ff; }
  .squad-player-row:hover { background: rgba(255,215,0,0.08); }
  .cap-badge { background: linear-gradient(135deg, #ffd700, #ff8c00); color: #1a2035; padding: 2px 7px; border-radius: 4px; font-size: 10px; font-family: 'Bebas Neue', sans-serif; letter-spacing: 1px; }
  .lb-table { width: 100%; border-collapse: collapse; }
  .lb-table th { font-family: 'Bebas Neue', sans-serif; font-size: 1rem; letter-spacing: 2px; color: #ffd700; background: rgba(255,215,0,0.12); padding: 10px 14px; text-align: left; border-bottom: 2px solid rgba(255,215,0,0.40); }
  .lb-table td { font-family: 'Roboto Condensed', sans-serif; font-size: 14px; color: #eef2ff; padding: 9px 14px; border-bottom: 1px solid rgba(255,255,255,0.10); }
  .lb-table tr:hover td { background: rgba(255,215,0,0.06); }
  .score-leader { background: linear-gradient(135deg, rgba(255,215,0,0.18), rgba(255,140,0,0.12)); border: 2px solid rgba(255,215,0,0.60); border-radius: 14px; padding: 18px 22px; margin-bottom: 16px; text-align: center; }
  .score-leader-label { font-family: 'Bebas Neue', sans-serif; font-size: 0.9rem; letter-spacing: 4px; color: rgba(255,215,0,0.80); margin-bottom: 2px; }
  .score-leader-name { font-family: 'Bebas Neue', sans-serif; font-size: 2.4rem; letter-spacing: 3px; color: #ffd700; line-height: 1.1; }
  .score-leader-pts { font-family: 'Bebas Neue', sans-serif; font-size: 1.4rem; color: #ff8c00; letter-spacing: 2px; }
  .score-rival-row { display: flex; justify-content: space-between; align-items: center; background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.15); border-radius: 10px; padding: 10px 16px; margin-bottom: 8px; }
  .score-rival-rank { font-family: 'Bebas Neue', sans-serif; font-size: 1.4rem; color: rgba(200,215,255,0.60); width: 36px; }
  .score-rival-name { font-family: 'Roboto Condensed', sans-serif; font-size: 15px; font-weight: 700; color: #eef2ff; flex-grow: 1; }
  .score-rival-pts { font-family: 'Bebas Neue', sans-serif; font-size: 1.2rem; color: #64b5f6; margin-right: 12px; }
  .score-gap-badge { background: rgba(209,29,38,0.30); border: 1px solid rgba(209,29,38,0.50); color: #ff8a80; font-family: 'Roboto Condensed', sans-serif; font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 20px; white-space: nowrap; }
  .score-gap-close { background: rgba(76,175,80,0.25); border: 1px solid rgba(76,175,80,0.45); color: #a5d6a7; }
  .section-header { font-family: 'Bebas Neue', sans-serif; font-size: 1.5rem; letter-spacing: 3px; color: #ffd700; border-left: 4px solid #d11d26; padding-left: 12px; margin: 16px 0 12px; }
  .lock-status { font-family: 'Roboto Condensed', sans-serif; font-size: 13px; font-weight: 700; letter-spacing: 1px; padding: 6px 12px; border-radius: 20px; display: inline-block; margin-top: 4px; }
  .lock-open   { background: rgba(76,175,80,0.20); color: #a5d6a7; border: 1px solid rgba(76,175,80,0.40); }
  .lock-closed { background: rgba(244,67,54,0.20); color: #ef9a9a; border: 1px solid rgba(244,67,54,0.40); }
  .admin-box { background: rgba(255,255,255,0.09); border: 1px solid rgba(255,255,255,0.18); border-radius: 10px; padding: 16px; margin-bottom: 12px; }
  .fetch-box { background: rgba(0,100,200,0.15); border: 1px solid rgba(100,180,255,0.35); border-radius: 10px; padding: 14px 16px; margin-bottom: 14px; }
  .fetch-box-title { font-family: 'Bebas Neue', sans-serif; font-size: 1.1rem; letter-spacing: 2px; color: #90caf9; margin-bottom: 6px; }
  .mapped-row { display: flex; justify-content: space-between; align-items: center; padding: 4px 8px; border-radius: 5px; margin-bottom: 3px; background: rgba(255,255,255,0.06); font-family: 'Roboto Condensed', sans-serif; font-size: 12px; color: #eef2ff; }
  .mapped-good { border-left: 3px solid #66bb6a; }
  .mapped-warn { border-left: 3px solid #ffa726; background: rgba(255,167,38,0.10); }
  .scoring-rule-box { background: rgba(255,215,0,0.08); border: 1px solid rgba(255,215,0,0.25); border-radius: 8px; padding: 10px 14px; margin-bottom: 14px; font-family: 'Rajdhani', sans-serif; font-size: 13px; color: #e8f0ff; }
  .scoring-rule-box strong { color: #ffd700; }
  .mom-badge { background: linear-gradient(135deg, #ff6b35, #ffd700); color: #1a2035; font-family: 'Bebas Neue', sans-serif; font-size: 11px; padding: 2px 8px; border-radius: 4px; letter-spacing: 1px; }
  .stSelectbox label, .stTextInput label, .stNumberInput label, .stCheckbox label { color: #eef2ff !important; font-family: 'Rajdhani', sans-serif !important; font-weight: 700; font-size: 14px; }
  .stSelectbox > div > div, .stTextInput > div > div > input { background: rgba(255,255,255,0.12) !important; border: 1px solid rgba(255,255,255,0.28) !important; color: #ffffff !important; border-radius: 8px !important; font-family: 'Roboto Condensed', sans-serif !important; }
  .stButton > button { font-family: 'Bebas Neue', sans-serif !important; font-size: 1.2rem !important; letter-spacing: 3px !important; border-radius: 8px !important; border: none !important; background: linear-gradient(135deg, #ffd700 0%, #ff8c00 50%, #d11d26 100%) !important; color: white !important; padding: 10px 24px !important; transition: opacity 0.2s, transform 0.1s !important; width: 100%; }
  .stButton > button:hover { opacity: 0.9 !important; transform: translateY(-1px) !important; }
  .stAlert { border-radius: 8px !important; font-family: 'Rajdhani', sans-serif !important; }
  input[type="number"] { background: rgba(255,255,255,0.12) !important; color: #ffffff !important; border: 1px solid rgba(255,255,255,0.28) !important; border-radius: 6px !important; }
  [data-testid="stNumberInput"] label { color: #eef2ff !important; font-family: 'Bebas Neue', sans-serif !important; font-size: 0.78rem !important; letter-spacing: 1.5px !important; }
  ::-webkit-scrollbar { width: 6px; height: 6px; }
  ::-webkit-scrollbar-track { background: #2a3550; }
  ::-webkit-scrollbar-thumb { background: rgba(255,215,0,0.35); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🏏 Inner Circle IPL Fantasy 2026</div>', unsafe_allow_html=True)
st.markdown('<div class="main-subtitle">Pick Your XI · Rule the Season · Outsmart Your Rivals</div>', unsafe_allow_html=True)
st.markdown('<div class="pitch-divider"></div>', unsafe_allow_html=True)

db = load_db()

def calc_points(scores_dict, match_ids):
    total = 0.0
    for mid in match_ids:
        s = scores_dict.get(mid, {})
        r=s.get("r",0); w=s.get("w",0); c=s.get("c",0.0); st_=s.get("s",0); mom=s.get("mom",0)
        pts = r*1 + w*20 + c*5 + st_*5 + mom*100
        if r>=100: pts+=10
        elif r>=50: pts+=5
        if w>=5: pts+=10
        elif w>=3: pts+=5
        total += pts
    return total

def build_leaderboard(db, week_keys, active_week_name):
    lb = []
    for mgr in db["pools"].keys():
        total, week_pts = 0.0, 0.0
        for idx, wk_key in enumerate(week_keys):
            sel = db["selections"].get(wk_key, {}).get(mgr, None)
            if not sel:
                for prev_wk in reversed(week_keys[:idx]):
                    lookback = db["selections"].get(prev_wk, {}).get(mgr, None)
                    if lookback: sel = lookback; break
            w_sum = 0.0
            if sel:
                for p in sel["squad"]:
                    p_pts = calc_points(db["scores"].get(p, {}), list(SEASON_WEEKS[wk_key]["matches"].keys()))
                    if p == sel["cap"]: p_pts *= 2
                    w_sum += p_pts
            total += w_sum
            if wk_key == active_week_name: week_pts = w_sum
        lb.append({"Manager": mgr, "Weekly": round(week_pts,1), "Total": round(total,1)})
    return sorted(lb, key=lambda x: x["Total"], reverse=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.markdown('<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.4rem;letter-spacing:3px;color:#ffd700;margin-bottom:12px;text-align:center;">🗓️ Season Calendar</div>', unsafe_allow_html=True)
active_week_name = st.sidebar.selectbox("Select Week", list(SEASON_WEEKS.keys()), label_visibility="collapsed")
week_config  = SEASON_WEEKS[active_week_name]
lock_time    = datetime.strptime(week_config["lock"], "%Y-%m-%d %H:%M:%S")
is_locked    = datetime.now() > lock_time
week_keys    = list(SEASON_WEEKS.keys())

if is_locked:
    st.sidebar.markdown(f'<span class="lock-status lock-closed">🔒 Locked — {lock_time.strftime("%I:%M %p, %b %d")}</span>', unsafe_allow_html=True)
else:
    st.sidebar.markdown(f'<span class="lock-status lock-open">🔓 Open · Closes {lock_time.strftime("%I:%M %p, %b %d")}</span>', unsafe_allow_html=True)

matches_this_week = week_config["matches"]
st.sidebar.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="sidebar-section"><div class="sidebar-week-title">⚡ THIS WEEK\'S MATCHES</div>', unsafe_allow_html=True)
for mid, fixture in matches_this_week.items():
    st.sidebar.markdown(f'<div class="match-pill">🏟️ {fixture}</div>', unsafe_allow_html=True)
st.sidebar.markdown('</div>', unsafe_allow_html=True)

all_teams_week = []
for f in matches_this_week.values(): all_teams_week.extend(f.split(" vs "))
team_counts = Counter(all_teams_week)
st.sidebar.markdown('<div class="sidebar-section"><div class="sidebar-week-title">🏆 TEAMS IN ACTION</div>', unsafe_allow_html=True)
for team, count in sorted(team_counts.items()):
    color = TEAM_COLORS.get(team, "#888")
    st.sidebar.markdown(f'<div class="team-stat-row"><span class="team-stat-name" style="color:{color}">▮ {team}</span><span class="team-stat-count">{count} match{"es" if count>1 else ""}</span></div>', unsafe_allow_html=True)
st.sidebar.markdown('</div>', unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
t1, t_view, t2, t_admin = st.tabs(["🏏  MY SQUAD", "👀  ALL SQUADS", "📊  STANDINGS", "🛡️  ADMIN"])

with t1:
    user   = st.selectbox("Manager Name", list(db["pools"].keys()))
    pool   = db["pools"].get(user, [])
    saved  = db["selections"].get(active_week_name, {}).get(user, {"squad": [], "cap": ""})
    state_key = f"sel_{user}_{active_week_name}"
    if state_key not in st.session_state: st.session_state[state_key] = list(saved["squad"])
    if is_locked: st.warning("🔒 Deadline passed — squad is locked for this week.")

    f1, f2, f3 = st.columns([2, 1, 1])
    search = f1.text_input("🔍 Search player", key="src_v10", placeholder="Type name...")
    team_f = f2.selectbox("Team", ["All"] + sorted(list(TEAM_COLORS.keys())), key="team_v10")
    role_f = f3.selectbox("Role", ["All", "BAT", "BOWL", "WK"], key="rol_v10")

    cols = st.columns(2); display_idx = 0
    for p in sorted(pool):
        info = db["player_master"].get(p, {"team":"IPL","role":"BAT","is_overseas":False})
        if not (search.lower() in p.lower()): continue
        if not (team_f == "All" or info["team"] == team_f): continue
        if not (role_f == "All" or info["role"] == role_f): continue
        tc = TEAM_COLORS.get(info["team"], "#666")
        ri = {"BAT":"🏏","BOWL":"🎳","WK":"🧤"}
        ot = " ✈️" if info["is_overseas"] else ""
        with cols[display_idx % 2]:
            cc, cb = st.columns([5,1])
            with cc:
                st.markdown(f'''<div class="player-card" style="border-left-color:{tc};">
                  <div style="flex-grow:1;"><div class="player-name">{p}{ot}</div>
                  <div style="display:flex;gap:6px;margin-top:3px;align-items:center;">
                    <span class="team-badge" style="background:{tc};">{info["team"]}</span>
                    <span class="role-chip">{ri.get(info["role"],"🏏")} {info["role"]}</span>
                  </div></div></div>''', unsafe_allow_html=True)
            with cb:
                chk = st.checkbox("", key=f"cb_{user}_{p}", value=(p in st.session_state[state_key]), disabled=is_locked)
                if not is_locked:
                    if chk and p not in st.session_state[state_key]: st.session_state[state_key].append(p); st.rerun()
                    elif not chk and p in st.session_state[state_key]: st.session_state[state_key].remove(p); st.rerun()
        display_idx += 1

    final_squad = st.session_state[state_key]
    os_c2 = sum(1 for p in final_squad if db["player_master"].get(p,{}).get("is_overseas"))
    wk_c2 = sum(1 for p in final_squad if db["player_master"].get(p,{}).get("role")=="WK")
    bw_c2 = sum(1 for p in final_squad if db["player_master"].get(p,{}).get("role")=="BOWL")
    sq_cl = "#ffd700" if len(final_squad)==11 else "#ff6b6b"
    os_cl = "#ffd700" if os_c2<=4 else "#ff6b6b"
    wk_cl = "#ffd700" if wk_c2>=1 else "#ff6b6b"
    bw_cl = "#ffd700" if bw_c2>=4 else "#ff6b6b"
    st.markdown(f'''<div class="squad-status">
      <div class="stat-pill"><span class="stat-label">SQUAD</span><span class="stat-value" style="color:{sq_cl};">{len(final_squad)}</span><span class="stat-max">/11</span></div>
      <div class="stat-pill"><span class="stat-label">✈️ OVERSEAS</span><span class="stat-value" style="color:{os_cl};">{os_c2}</span><span class="stat-max">/4 max</span></div>
      <div class="stat-pill"><span class="stat-label">🧤 KEEPERS</span><span class="stat-value" style="color:{wk_cl};">{wk_c2}</span><span class="stat-max">min 1</span></div>
      <div class="stat-pill"><span class="stat-label">🎳 BOWLERS</span><span class="stat-value" style="color:{bw_cl};">{bw_c2}</span><span class="stat-max">/4 min</span></div>
    </div>''', unsafe_allow_html=True)

    if len(final_squad)==11 and os_c2<=4 and wk_c2>=1 and bw_c2>=4:
        cap = st.selectbox("🛡️ Select Captain (2× points)", final_squad,
                           index=(final_squad.index(saved["cap"]) if saved["cap"] in final_squad else 0),
                           disabled=is_locked)
        if not is_locked and st.button("🚀  LOCK IN SQUAD", type="primary", use_container_width=True):
            if active_week_name not in db["selections"]: db["selections"][active_week_name] = {}
            db["selections"][active_week_name][user] = {"squad": final_squad, "cap": cap}
            save_db(db); st.success("✅ Squad saved! Good luck this week!")
    else:
        st.warning("⚠️ Complete your squad: exactly 11 players | max 4 overseas | min 1 keeper | min 4 bowlers")

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
                    tc = TEAM_COLORS.get(info.get("team",""), "#888")
                    st.markdown(f'<div class="squad-player-row"><span><span style="color:{tc};font-size:9px;">●</span> {player} <span style="color:rgba(210,225,255,0.55);font-size:10px;">({info.get("team","")})</span></span>{cap_tag}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="text-align:center;padding:20px;color:rgba(200,220,255,0.45);font-family:\'Rajdhani\',sans-serif;border:1px dashed rgba(255,255,255,0.15);border-radius:8px;font-size:13px;">No squad selected</div>', unsafe_allow_html=True)

with t2:
    db        = load_db()
    sorted_lb = build_leaderboard(db, week_keys, active_week_name)
    st.markdown('<div class="section-header">🏆 LIVE SCOREBOARD</div>', unsafe_allow_html=True)
    if sorted_lb:
        leader = sorted_lb[0]
        st.markdown(f'''<div class="score-leader">
          <div class="score-leader-label">🥇 LEADING THE PACK</div>
          <div class="score-leader-name">{leader["Manager"]}</div>
          <div class="score-leader-pts">{leader["Total"]} pts total &nbsp;|&nbsp; {leader["Weekly"]} pts this week</div>
        </div>''', unsafe_allow_html=True)
        rank_labels = {1:"🥈", 2:"🥉"}
        for rank, row in enumerate(sorted_lb[1:], start=1):
            gap = round(leader["Total"] - row["Total"], 1)
            gap_cls = "score-gap-close" if gap <= 50 else ""
            gap_txt = f"▼ {gap} behind" if gap > 0 else "🔥 LEVEL!"
            st.markdown(f'''<div class="score-rival-row">
              <div class="score-rival-rank">{rank_labels.get(rank,f"#{rank+1}")}</div>
              <div class="score-rival-name">{row["Manager"]}</div>
              <div class="score-rival-pts">{row["Total"]} pts</div>
              <div class="score-gap-badge {gap_cls}">{gap_txt}</div>
            </div>''', unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown('<div class="section-header">📊 FULL LEADERBOARD</div>', unsafe_allow_html=True)
    rank_icons = {0:"🥇",1:"🥈",2:"🥉"}
    rows_html = ""
    for rank, row in enumerate(sorted_lb):
        icon = rank_icons.get(rank, f"#{rank+1}")
        rows_html += (f"<tr><td style='text-align:center;font-family:\"Bebas Neue\",sans-serif;font-size:1.1rem;'>{icon}</td>"
                      f"<td style='font-weight:700;color:#eef2ff;'>{row['Manager']}</td>"
                      f"<td style='text-align:right;color:#90caf9;font-family:\"Bebas Neue\",sans-serif;font-size:1.05rem;'>{row['Weekly']}</td>"
                      f"<td style='text-align:right;color:#ffd700;font-family:\"Bebas Neue\",sans-serif;font-size:1.15rem;font-weight:700;'>{row['Total']}</td></tr>")
    st.markdown(f"""<table class="lb-table"><thead><tr>
      <th style="text-align:center;width:60px;">RANK</th><th>MANAGER</th>
      <th style="text-align:right;">THIS WEEK</th><th style="text-align:right;">TOTAL PTS</th>
    </tr></thead><tbody>{rows_html}</tbody></table>""", unsafe_allow_html=True)
    st.caption("📡 Scores update live after admin pushes results. Half run-outs (0.5) = 2.5 pts. MOM = +100 pts.")

# ─────────────────────────────────────────────────────────────────────────────
with t_admin:
    st.markdown('<div class="section-header">🛡️ SCORE MANAGEMENT</div>', unsafe_allow_html=True)

    st.markdown("""<div class="scoring-rule-box">
    <strong>Scoring:</strong> Run=1pt | Wicket=20pt | Catch/Full RO=5pt | Half RO=2.5pt (enter 0.5) | Stumping=5pt | MOM=100pt<br>
    <strong>Bonuses:</strong> 50+runs→+5pt | 100+runs→+10pt | 3+wkts→+5pt | 5+wkts→+10pt
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="admin-box">', unsafe_allow_html=True)
    sel_mid = st.selectbox("Select Match", list(matches_this_week.keys()),
                           format_func=lambda x: f"{x} — {matches_this_week[x]}")
    teams = matches_this_week[sel_mid].split(" vs ")

    # ── AUTO-FETCH SECTION ────────────────────────────────────────────────────
    st.markdown('<div class="fetch-box">', unsafe_allow_html=True)
    st.markdown('<div class="fetch-box-title">🌐 AUTO-FETCH FROM CRICBUZZ</div>', unsafe_allow_html=True)

    # Cricbuzz match ID input — pre-filled from our dict, editable
    default_cb_id = CRICBUZZ_MATCH_IDS.get(sel_mid, "")
    cb_id_input = st.text_input(
        "Cricbuzz Match ID",
        value=default_cb_id,
        key=f"cbid_{sel_mid}",
        placeholder="e.g. 116484  (5-6 digit number from cricbuzz.com URL)",
        help="Go to cricbuzz.com → find the match → copy the number from the URL: cricbuzz.com/live-cricket-scores/116484/..."
    )

    col_fetch, col_howto = st.columns([2, 3])
    fetch_clicked = col_fetch.button("⬇️  FETCH SCORECARD", key=f"fetch_{sel_mid}", use_container_width=True)
    col_howto.markdown(
        '<div style="font-size:11px;color:rgba(180,210,255,0.75);font-family:\'Rajdhani\',sans-serif;padding-top:8px;">'
        '🔗 Go to <b>cricbuzz.com</b> → search the match → copy the <b>6-digit ID</b> from the URL → paste above → click Fetch</div>',
        unsafe_allow_html=True
    )

    if fetch_clicked and cb_id_input.strip():
        with st.spinner("🏏 Fetching scorecard from Cricbuzz..."):
            result = fetch_cricbuzz_scorecard(cb_id_input.strip())

        if result and result.get("stats"):
            mapped, unmatched = map_fetched_to_pool(result["stats"], db["player_master"])

            st.markdown(f'<div style="color:#a5d6a7;font-family:\'Roboto Condensed\',sans-serif;font-size:13px;margin:8px 0 4px;">✅ Fetched {len(result["stats"])} players · matched <b>{len(mapped)}</b> to your pool · <span style="color:#ffa726;">{len(unmatched)} unmatched</span></div>', unsafe_allow_html=True)

            # Show match table
            if result.get("raw_batting"):
                st.markdown('<div style="font-family:\'Bebas Neue\',sans-serif;font-size:0.85rem;letter-spacing:2px;color:#ffd700;margin:10px 0 4px;">BATTING</div>', unsafe_allow_html=True)
                for b in result["raw_batting"][:12]:
                    pm = _best_match(b["name"], list(db["player_master"].keys()))
                    mc = "mapped-good" if pm else "mapped-warn"
                    pm_label = f"→ {pm}" if pm else "⚠️ no match"
                    st.markdown(f'<div class="mapped-row {mc}"><span>{b["name"]}</span><span style="color:rgba(200,220,255,0.6);font-size:10px;">{pm_label}</span><span style="color:#ffd700;font-family:\'Bebas Neue\',sans-serif;">{b["runs"]}r</span></div>', unsafe_allow_html=True)

            if result.get("raw_bowling"):
                st.markdown('<div style="font-family:\'Bebas Neue\',sans-serif;font-size:0.85rem;letter-spacing:2px;color:#ffd700;margin:10px 0 4px;">BOWLING</div>', unsafe_allow_html=True)
                for bw in result["raw_bowling"][:10]:
                    pm = _best_match(bw["name"], list(db["player_master"].keys()))
                    mc = "mapped-good" if pm else "mapped-warn"
                    pm_label = f"→ {pm}" if pm else "⚠️ no match"
                    st.markdown(f'<div class="mapped-row {mc}"><span>{bw["name"]}</span><span style="color:rgba(200,220,255,0.6);font-size:10px;">{pm_label}</span><span style="color:#90caf9;font-family:\'Bebas Neue\',sans-serif;">{bw["wickets"]}w</span></div>', unsafe_allow_html=True)

            if unmatched:
                st.markdown(f'<div style="font-size:11px;color:#ffa726;font-family:\'Rajdhani\',sans-serif;margin-top:6px;">⚠️ Unmatched names (not in your player pool): {", ".join(unmatched)}</div>', unsafe_allow_html=True)

            # Apply to db scores
            apply_col, _ = st.columns([2, 3])
            if apply_col.button("✅  APPLY FETCHED SCORES TO MATCH", key=f"apply_{sel_mid}", use_container_width=True):
                for canon_name, vals in mapped.items():
                    if canon_name not in db["scores"]: db["scores"][canon_name] = {}
                    existing = db["scores"][canon_name].get(sel_mid, {"r":0,"w":0,"c":0.0,"s":0,"mom":0})
                    db["scores"][canon_name][sel_mid] = {
                        "r": vals.get("r", existing["r"]),
                        "w": vals.get("w", existing["w"]),
                        "c": vals.get("c", existing["c"]),
                        "s": vals.get("s", existing["s"]),
                        "mom": existing.get("mom", 0),  # keep existing MOM
                    }
                save_db(db)
                st.success(f"✅ Applied {len(mapped)} player scores. Review and adjust below, then push.")
                st.rerun()
        else:
            st.error("❌ Could not fetch scorecard. Check the Cricbuzz Match ID, or the match may not have started yet.")
            st.markdown('<div style="font-size:12px;color:rgba(200,220,255,0.7);font-family:\'Rajdhani\',sans-serif;margin-top:6px;">💡 <b>Tip:</b> Cricbuzz sometimes blocks automated requests. If this fails, enter scores manually below.</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # end fetch-box

    # ── Manual player search (team override) ─────────────────────────────────
    st.markdown("**🔍 Add extra player** (if team is wrong in master, search by name):")
    all_p_in_squads = set()
    for wk in db["selections"].values():
        for m_sel in wk.values(): all_p_in_squads.update(m_sel["squad"])
    eligible_squad = [p for p in all_p_in_squads if db["player_master"].get(p,{}).get("team") in teams]

    manual_search = st.text_input("Type player name", key="manual_search_admin", placeholder="e.g. Kohli, Bumrah...")
    if manual_search.strip():
        manual_candidates = [p for p in db["player_master"].keys() if manual_search.lower() in p.lower()]
        if manual_candidates:
            manual_pick = st.selectbox("Select to add:", ["— skip —"] + manual_candidates, key="manual_pick")
            if manual_pick and manual_pick != "— skip —" and manual_pick not in eligible_squad:
                eligible_squad.append(manual_pick)

    # ── MOM selection ─────────────────────────────────────────────────────────
    st.markdown('<hr style="border:none;border-top:1px solid rgba(255,215,0,0.35);margin:8px 0 10px;">', unsafe_allow_html=True)
    st.markdown("**🏆 Man of the Match** (+100 pts)")
    all_scorable = sorted(eligible_squad)
    current_mom  = next((p for p in all_scorable if db["scores"].get(p,{}).get(sel_mid,{}).get("mom",0)==1), None)
    mom_options  = ["— None —"] + all_scorable
    mom_default  = mom_options.index(current_mom) if current_mom in mom_options else 0
    selected_mom = st.selectbox("Select MOM:", mom_options, index=mom_default, key=f"mom_{sel_mid}")
    st.markdown('<hr style="border:none;border-top:1px solid rgba(255,215,0,0.35);margin:8px 0 10px;">', unsafe_allow_html=True)

    # ── Score entry column headers ────────────────────────────────────────────
    hdr = st.columns([2, 1, 1, 1, 1, 1])
    hdr[0].markdown('<div style="font-family:\'Bebas Neue\',sans-serif;font-size:0.82rem;letter-spacing:2px;color:#ffd700;padding:4px 0 2px;">PLAYER</div>', unsafe_allow_html=True)
    for col, lbl, sub in [
        (hdr[1],"🏏 RUNS","1r=1pt | 50+=+5 | 100+=+10"),
        (hdr[2],"🎳 WICKETS","1w=20pt | 3+=+5 | 5+=+10"),
        (hdr[3],"🤲 CATCH/RO","1=5pt | 0.5=2.5pt"),
        (hdr[4],"🧤 STUMPING","1 = 5 pts"),
        (hdr[5],"PTS","live"),
    ]:
        col.markdown(f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:0.78rem;letter-spacing:1.5px;color:#ffd700;text-align:center;padding:4px 0 0;">{lbl}</div>'
                     f'<div style="font-size:9px;color:#aac0e0;font-family:\'Rajdhani\',sans-serif;text-align:center;padding-bottom:4px;">{sub}</div>', unsafe_allow_html=True)
    st.markdown('<hr style="border:none;border-top:1px solid rgba(255,215,0,0.35);margin:4px 0 8px;">', unsafe_allow_html=True)

    if eligible_squad:
        for p in sorted(eligible_squad):
            cur  = db["scores"].get(p,{}).get(sel_mid, {"r":0,"w":0,"c":0.0,"s":0,"mom":0})
            info = db["player_master"].get(p, {})
            tc   = TEAM_COLORS.get(info.get("team",""), "#888")
            is_mom = (selected_mom == p)

            cols = st.columns([2,1,1,1,1,1])
            mom_tag = ' <span class="mom-badge">⭐ MOM</span>' if is_mom else ""
            cols[0].markdown(
                f'<div style="padding:6px 0 2px;font-family:\'Roboto Condensed\',sans-serif;font-size:13px;line-height:1.4;">'
                f'<span style="color:{tc};font-size:10px;">●</span> <b style="color:#fff;">{p}</b>{mom_tag}<br>'
                f'<span style="color:rgba(210,230,255,0.65);font-size:10px;">({info.get("team","")}) {ROLE_EMOJI.get(info.get("role",""),"")}</span></div>',
                unsafe_allow_html=True
            )
            r  = cols[1].number_input("Runs",     min_value=0,   max_value=300,  value=int(cur.get("r",0)),   step=1,   key=f"r_{sel_mid}_{p}")
            w  = cols[2].number_input("Wkts",     min_value=0,   max_value=10,   value=int(cur.get("w",0)),   step=1,   key=f"w_{sel_mid}_{p}")
            c  = cols[3].number_input("Catch/RO", min_value=0.0, max_value=10.0, value=float(cur.get("c",0.0)), step=0.5, key=f"c_{sel_mid}_{p}")
            s  = cols[4].number_input("Stumping", min_value=0,   max_value=10,   value=int(cur.get("s",0)),   step=1,   key=f"s_{sel_mid}_{p}")

            mom_pts  = 100 if is_mom else 0
            live_pts = r*1 + w*20 + c*5 + s*5 + mom_pts
            if r>=100: live_pts+=10
            elif r>=50: live_pts+=5
            if w>=5: live_pts+=10
            elif w>=3: live_pts+=5
            cols[5].markdown(f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:1.4rem;color:#ffd700;text-align:center;padding-top:6px;">{live_pts:.1f}</div>', unsafe_allow_html=True)

            new_score = {"r":r,"w":w,"c":c,"s":s,"mom":1 if is_mom else 0}
            if new_score != cur:
                if p not in db["scores"]: db["scores"][p] = {}
                db["scores"][p][sel_mid] = new_score
    else:
        st.info("No eligible players found. Submit squads first, or use search above.")

    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🚀  PUSH SCORES", type="primary", use_container_width=True):
        if selected_mom and selected_mom != "— None —":
            for p in list(db["scores"].keys()):
                if sel_mid in db["scores"][p]:
                    db["scores"][p][sel_mid]["mom"] = 1 if p == selected_mom else 0
        save_db(db)
        st.success("✅ Scores saved! Leaderboard updates automatically.")

    st.markdown('<div class="section-header">⚠️ DANGER ZONE</div>', unsafe_allow_html=True)
    st.markdown('<div class="admin-box">', unsafe_allow_html=True)
    reset_confirm = st.checkbox("☢️ Confirm: Permanently delete ALL selections and scores.")
    if reset_confirm and st.button("💣  CLEAR ALL DATA", type="primary"):
        if os.path.exists(DB_FILE): os.remove(DB_FILE)
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
