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
ROLE_EMOJI = {'BAT': '🏏', 'BOWL': '🔴', 'WK': '🧤'}

# V1 SCHEDULE — lock times stored in UTC (IST - 5:30). 7:00pm IST = 13:30 UTC
SEASON_WEEKS = {
    "Week 1 (Mar 28 - Apr 03)": {"lock": "2026-03-28 13:30:00", "matches": {"M01": "RCB vs SRH", "M02": "MI vs KKR", "M03": "RR vs CSK", "M04": "PBKS vs GT", "M05": "LSG vs DC", "M06": "KKR vs SRH", "M07": "CSK vs PBKS"}},
    "Week 2 (Apr 04 - Apr 10)": {"lock": "2026-04-04 13:30:00", "matches": {"M08": "DC vs MI", "M09": "GT vs RR", "M10": "SRH vs LSG", "M11": "RCB vs CSK", "M12": "KKR vs PBKS", "M13": "RR vs MI", "M14": "DC vs GT"}},
    "Week 3 (Apr 11 - Apr 17)": {"lock": "2026-04-11 13:30:00", "matches": {"M15": "SRH vs RCB", "M16": "KKR vs MI", "M17": "CSK vs RR", "M18": "GT vs PBKS", "M19": "DC vs LSG", "M20": "SRH vs KKR", "M21": "PBKS vs CSK"}},
    "Week 4 (Apr 18 - Apr 24)": {"lock": "2026-04-18 13:30:00", "matches": {"M22": "MI vs DC", "M23": "RR vs GT", "M24": "LSG vs SRH", "M25": "CSK vs RCB", "M26": "PBKS vs KKR", "M27": "MI vs RR", "M28": "GT vs DC"}},
    "Week 5 (Apr 25 - May 01)": {"lock": "2026-04-25 13:30:00", "matches": {"M29": "LSG vs KKR", "M30": "RCB vs GT", "M31": "SRH vs RR", "M32": "DC vs CSK", "M33": "MI vs PBKS", "M34": "KKR vs RCB", "M35": "RR vs LSG"}},
    "Week 6 (May 02 - May 08)": {"lock": "2026-05-02 13:30:00", "matches": {"M36": "GT vs SRH", "M37": "CSK vs MI", "M38": "PBKS vs DC", "M39": "RCB vs LSG", "M40": "RR vs KKR", "M41": "SRH vs PBKS", "M42": "GT vs CSK"}},
    "Week 7 (May 09 - May 15)": {"lock": "2026-05-09 13:30:00", "matches": {"M43": "DC vs RCB", "M44": "LSG vs MI", "M45": "KKR vs GT", "M46": "CSK vs SRH", "M47": "PBKS vs RR", "M48": "MI vs LSG", "M49": "RCB vs DC"}},
    "Week 8 (May 16 - May 22)": {"lock": "2026-05-16 13:30:00", "matches": {"M50": "GT vs KKR", "M51": "SRH vs CSK", "M52": "RR vs PBKS", "M53": "DC vs RR", "M54": "KKR vs PBKS", "M55": "LSG vs GT", "M56": "MI vs RCB"}},
}

# --- PERSISTENT STORAGE via GitHub Gist ---
# Survives Streamlit Cloud restarts/sleep cycles.
# Setup (one time):
#   1. Go to github.com → Settings → Developer Settings → Personal Access Tokens → Tokens (classic)
#   2. Generate token with "gist" scope only
#   3. Create a new Secret Gist at gist.github.com with filename "tournament_db.json" and content "{}"
#   4. Copy the Gist ID from the URL (32-char string after gist.github.com/username/)
#   5. In Streamlit Cloud → App Settings → Secrets, add:
#        GIST_TOKEN = "ghp_your_token_here"
#        GIST_ID    = "your_gist_id_here"
# If secrets are not set, falls back to local file (for local dev).

DB_FILE      = 'tournament_db.json'          # local fallback
GIST_TOKEN   = st.secrets.get("GIST_TOKEN", "")
GIST_ID      = st.secrets.get("GIST_ID",    "")
USE_GIST     = bool(GIST_TOKEN and GIST_ID)

import requests as _req

def _gist_read():
    """Read DB from GitHub Gist. Returns parsed dict or None on failure."""
    try:
        r = _req.get(
            f"https://api.github.com/gists/{GIST_ID}",
            headers={
                "Authorization": f"token {GIST_TOKEN}",
                "Accept": "application/vnd.github.v3+json",
            },
            timeout=10
        )
        if r.status_code == 200:
            raw = r.json()["files"]["tournament_db.json"]["content"]
            return json.loads(raw)
    except Exception:
        pass
    return None

def _gist_write(data):
    """Write DB to GitHub Gist. Returns True on success."""
    try:
        r = _req.patch(
            f"https://api.github.com/gists/{GIST_ID}",
            headers={
                "Authorization": f"token {GIST_TOKEN}",
                "Accept": "application/vnd.github.v3+json",
            },
            json={"files": {"tournament_db.json": {"content": json.dumps(data)}}},
            timeout=10
        )
        return r.status_code == 200
    except Exception:
        return False

def load_db():
    pm = _build_player_master()
    excel_pools = _build_excel_pools()
    empty = {"selections": {}, "scores": {}, "pools": excel_pools, "player_master": pm}

    # ── Try Gist first ────────────────────────────────────────────────────────
    if USE_GIST:
        data = _gist_read()
        if data:
            data["player_master"] = pm   # always sync roles/teams from code
            data.setdefault("selections", {})
            data.setdefault("scores", {})
            data.setdefault("pools", excel_pools)
            return data
        # Gist read failed — fall through to local file

    # ── Local file fallback ───────────────────────────────────────────────────
    if not os.path.exists(DB_FILE):
        return empty
    try:
        with open(DB_FILE, 'r') as f:
            content = f.read().strip()
        if not content:
            raise ValueError("Empty file")
        data = json.loads(content)
        data["player_master"] = pm
        data.setdefault("selections", {})
        data.setdefault("scores", {})
        data.setdefault("pools", excel_pools)
        return data
    except Exception as e:
        try:
            import shutil, time
            shutil.copy(DB_FILE, DB_FILE + f".bak_{int(time.time())}")
        except Exception:
            pass
        st.error(f"⚠️ Local DB corrupted ({e}). Starting fresh.")
        return empty

def save_db(data):
    """Save to Gist (persistent) AND local file (backup)."""
    # ── Gist write ────────────────────────────────────────────────────────────
    if USE_GIST:
        ok = _gist_write(data)
        if not ok:
            st.warning("⚠️ Gist save failed — data saved locally only (may be lost on restart).")

    # ── Local file write (always, as a local-dev fallback) ────────────────────
    tmp = DB_FILE + ".tmp"
    try:
        with open(tmp, 'w') as f:
            json.dump(data, f)
        os.replace(tmp, DB_FILE)
    except Exception:
        try:
            with open(DB_FILE, 'w') as f:
                json.dump(data, f)
        except Exception:
            pass


def _build_player_master():
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
    return pm


def _build_excel_pools():
    return {
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

@st.cache_data(ttl=180, show_spinner=False)
def fetch_scorecard(espn_match_url: str):
    """
    Scrape full scorecard from ESPNcricinfo match page.
    Input: full URL like https://www.espncricinfo.com/series/.../full-scorecard
           OR just the match path slug.
    Returns {"stats":{...}, "raw_batting":[...], "raw_bowling":[...], "error": str|None}
    """
    import re as _re
    errors = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
    }

    # Normalise URL
    url = espn_match_url.strip()
    if not url.startswith("http"):
        url = "https://www.espncricinfo.com" + ("/" if not url.startswith("/") else "") + url
    if "full-scorecard" not in url:
        url = url.rstrip("/") + "/full-scorecard"

    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code != 200:
            errors.append(f"ESPNcricinfo → HTTP {resp.status_code}")
        else:
            result = _parse_espn_html(resp.text)
            if result.get("stats"):
                result["error"] = None
                return result
            errors.append("ESPNcricinfo 200 but no stats parsed — scorecard may not be available yet")
    except Exception as e:
        errors.append(f"ESPNcricinfo → {type(e).__name__}: {e}")

    return {"stats": {}, "raw_batting": [], "raw_bowling": [], "error": " | ".join(errors)}

def _parse_espn_html(html):
    """
    Parse ESPNcricinfo full-scorecard HTML.
    Extracts batting (name, runs, dismissal) and bowling (name, wickets) for all innings.
    """
    import re as _re
    from html import unescape

    stats    = {}
    raw_bat  = []
    raw_bowl = []

    def clean(s):
        s = _re.sub(r"<[^>]+>", " ", s)
        s = unescape(s).strip()
        return _re.sub(r"\s+", " ", s)

    # ── Batting: look for scorecard rows ─────────────────────────────────────
    # ESPNcricinfo uses a table structure:
    # <td class="...batsman...">Name</td>...<td class="...runs...">42</td>
    # We match by positional pattern across the entire HTML.

    # Strategy: find all <tr> blocks inside scorecard tables
    # Batting block identified by presence of "Runs" "Balls" "4s" "6s" "SR" headers
    # We use a broad regex then filter

    bat_pattern = _re.compile(
        r'<tr[^>]*>\s*'
        r'<td[^>]*>\s*<a[^>]*>([^<]{2,40})</a>\s*</td>\s*'   # batsman name
        r'<td[^>]*>([^<]{0,100})</td>\s*'                      # dismissal
        r'<td[^>]*>(\d+)</td>',                                 # runs
        _re.S
    )
    for m in bat_pattern.finditer(html):
        name = clean(m.group(1))
        diss = clean(m.group(2)).lower()
        try: runs = int(m.group(3))
        except: continue
        if not name or len(name) > 40 or name in ("Extras","Total","Did not bat"): continue
        if name not in stats: stats[name] = {"r":0,"w":0,"c":0.0,"s":0,"mom":0}
        # avoid double-counting if name appears in both innings
        if stats[name]["r"] == 0:
            stats[name]["r"] = runs
        else:
            stats[name]["r"] += runs
        raw_bat.append({"name": name, "runs": runs, "dismissal": diss})
        _credit_fielding(stats, diss)

    # ── Bowling: look for bowling rows ────────────────────────────────────────
    # Pattern: name link, then O, M, R, W columns
    bowl_pattern = _re.compile(
        r'<tr[^>]*>\s*'
        r'<td[^>]*>\s*<a[^>]*>([^<]{2,40})</a>\s*</td>\s*'   # bowler name
        r'<td[^>]*>[^<]*</td>\s*'                              # overs
        r'<td[^>]*>[^<]*</td>\s*'                              # maidens
        r'<td[^>]*>[^<]*</td>\s*'                              # runs conceded
        r'<td[^>]*>(\d+)</td>',                                # wickets
        _re.S
    )
    for m in bowl_pattern.finditer(html):
        name = clean(m.group(1))
        try: wkts = int(m.group(2))
        except: continue
        if not name or len(name) > 40: continue
        if name not in stats: stats[name] = {"r":0,"w":0,"c":0.0,"s":0,"mom":0}
        stats[name]["w"] += wkts
        raw_bowl.append({"name": name, "wickets": wkts})

    # De-duplicate raw lists keeping last occurrence per name
    seen_bat  = {}
    for b in raw_bat:  seen_bat[b["name"]]  = b
    seen_bowl = {}
    for b in raw_bowl: seen_bowl[b["name"]] = b

    return {
        "stats":       stats,
        "raw_batting": list(seen_bat.values()),
        "raw_bowling": list(seen_bowl.values()),
    }

def _credit_fielding(stats, diss):
    """Credit catches / stumpings / run-outs from dismissal text."""
    import re as _re
    if "c " in diss and "b " in diss:
        m = _re.search(r"c\s+([\w\s\-']+)\s+b", diss)
        if m:
            fn = m.group(1).strip()
            if fn not in stats: stats[fn] = {"r":0,"w":0,"c":0.0,"s":0,"mom":0}
            stats[fn]["c"] += 1
    elif "st " in diss:
        m = _re.search(r"st\s+([\w\s\-']+)\s+b", diss)
        if m:
            kn = m.group(1).strip()
            if kn not in stats: stats[kn] = {"r":0,"w":0,"c":0.0,"s":0,"mom":0}
            stats[kn]["s"] += 1
    elif "run out" in diss:
        m = _re.search(r"run out\s*[\(\[]([\w\s/\-']+)[\)\]]", diss)
        if m:
            players = [x.strip() for x in _re.split(r"[/&]", m.group(1)) if x.strip()]
            share   = 1.0 if len(players) == 1 else 0.5
            for rp in players:
                if rp not in stats: stats[rp] = {"r":0,"w":0,"c":0.0,"s":0,"mom":0}
                stats[rp]["c"] += share

def test_fetch_connection():
    """Test if ESPNcricinfo is reachable from this server."""
    try:
        r = requests.get(
            "https://www.espncricinfo.com/",
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/123.0.0.0"},
            timeout=8
        )
        return True, f"✅ ESPNcricinfo reachable — HTTP {r.status_code}"
    except Exception as e:
        return False, f"❌ Cannot reach ESPNcricinfo — {type(e).__name__}: {e}"

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
  /* ── All labels ── */
  .stSelectbox label, .stTextInput label, .stNumberInput label, .stCheckbox label { color: #eef2ff !important; font-family: 'Rajdhani', sans-serif !important; font-weight: 700; font-size: 14px; }
  [data-testid="stNumberInput"] label { color: #eef2ff !important; font-family: 'Bebas Neue', sans-serif !important; font-size: 0.78rem !important; letter-spacing: 1.5px !important; }
  /* ── Number inputs — solid dark bg so text always visible ── */
  input[type="number"] {
    background: #1a2740 !important;
    color: #ffffff !important;
    border: 1px solid rgba(255,215,0,0.45) !important;
    border-radius: 6px !important;
    caret-color: #ffd700 !important;
    -webkit-text-fill-color: #ffffff !important;
  }
  input[type="number"]:focus {
    background: #1e2e4a !important;
    border-color: #ffd700 !important;
    box-shadow: 0 0 0 2px rgba(255,215,0,0.20) !important;
    outline: none !important;
    -webkit-text-fill-color: #ffffff !important;
  }
  /* Streamlit wraps number inputs — target those wrappers too */
  [data-testid="stNumberInput"] > div > div {
    background: #1a2740 !important;
    border: 1px solid rgba(255,215,0,0.45) !important;
    border-radius: 6px !important;
  }
  [data-testid="stNumberInput"] > div > div > input {
    background: #1a2740 !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
  }
  /* ── Text inputs ── */
  .stTextInput > div > div > input {
    background: #1a2740 !important;
    border: 1px solid rgba(255,215,0,0.45) !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    border-radius: 8px !important;
    font-family: 'Roboto Condensed', sans-serif !important;
  }
  .stTextInput > div > div > input:focus {
    border-color: #ffd700 !important;
    box-shadow: 0 0 0 2px rgba(255,215,0,0.20) !important;
  }
  /* ── Select boxes ── */
  .stSelectbox > div > div {
    background: #1a2740 !important;
    border: 1px solid rgba(255,215,0,0.45) !important;
    color: #ffffff !important;
    border-radius: 8px !important;
    font-family: 'Roboto Condensed', sans-serif !important;
  }
  /* Dropdown options */
  [data-baseweb="select"] [data-testid="stMarkdownContainer"],
  [data-baseweb="popover"] { background: #1a2740 !important; }
  /* ── Buttons ── */
  .stButton > button { font-family: 'Bebas Neue', sans-serif !important; font-size: 1.2rem !important; letter-spacing: 3px !important; border-radius: 8px !important; border: none !important; background: linear-gradient(135deg, #ffd700 0%, #ff8c00 50%, #d11d26 100%) !important; color: white !important; padding: 10px 24px !important; transition: opacity 0.2s, transform 0.1s !important; width: 100%; }
  .stButton > button:hover { opacity: 0.9 !important; transform: translateY(-1px) !important; }
  .stAlert { border-radius: 8px !important; font-family: 'Rajdhani', sans-serif !important; }
  ::-webkit-scrollbar { width: 6px; height: 6px; }
  ::-webkit-scrollbar-track { background: #2a3550; }
  ::-webkit-scrollbar-thumb { background: rgba(255,215,0,0.35); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🏏 Inner Circle IPL Fantasy 2026</div>', unsafe_allow_html=True)
st.markdown('<div class="main-subtitle">Pick Your XI · Rule the Season · Outsmart Your Rivals</div>', unsafe_allow_html=True)
st.markdown('<div class="pitch-divider"></div>', unsafe_allow_html=True)

db = load_db()

# ── Storage status banner — always visible so you know if data is safe ────────
if USE_GIST:
    st.sidebar.markdown(
        '<div style="background:rgba(76,175,80,0.15);border:1px solid rgba(76,175,80,0.40);'
        'border-radius:6px;padding:6px 10px;margin-bottom:8px;font-family:\'Rajdhani\',sans-serif;'
        'font-size:12px;color:#a5d6a7;">🟢 <b>Gist connected</b> — data is persistent</div>',
        unsafe_allow_html=True
    )
else:
    st.sidebar.markdown(
        '<div style="background:rgba(244,67,54,0.20);border:1px solid rgba(244,67,54,0.50);'
        'border-radius:6px;padding:6px 10px;margin-bottom:8px;font-family:\'Rajdhani\',sans-serif;'
        'font-size:12px;color:#ef9a9a;">🔴 <b>Gist NOT set up</b> — data will vanish on restart!<br>'
        '<span style="font-size:10px;">Go to App Settings → Secrets → add GIST_TOKEN + GIST_ID</span></div>',
        unsafe_allow_html=True
    )

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
lock_time_utc = datetime.strptime(week_config["lock"], "%Y-%m-%d %H:%M:%S")
lock_time_ist = lock_time_utc + __import__('datetime').timedelta(hours=5, minutes=30)
is_locked     = datetime.utcnow() > lock_time_utc
week_keys     = list(SEASON_WEEKS.keys())

if is_locked:
    st.sidebar.markdown(f'<span class="lock-status lock-closed">🔒 Locked — {lock_time_ist.strftime("%I:%M %p, %b %d")} IST</span>', unsafe_allow_html=True)
else:
    st.sidebar.markdown(f'<span class="lock-status lock-open">🔓 Open · Closes {lock_time_ist.strftime("%I:%M %p, %b %d")} IST</span>', unsafe_allow_html=True)

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
t1, t_view, t2, t_admin, t_restore = st.tabs(["🏏  MY SQUAD", "👀  ALL SQUADS", "📊  STANDINGS", "🛡️  ADMIN", "🔐  RESTORE"])

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
        ri = {"BAT":"🏏","BOWL":"🔴","WK":"🧤"}
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
    bw_cl = "#ffd700" if bw_c2>=3 else "#ff6b6b"
    st.markdown(f'''<div class="squad-status">
      <div class="stat-pill"><span class="stat-label">SQUAD</span><span class="stat-value" style="color:{sq_cl};">{len(final_squad)}</span><span class="stat-max">/11</span></div>
      <div class="stat-pill"><span class="stat-label">✈️ OVERSEAS</span><span class="stat-value" style="color:{os_cl};">{os_c2}</span><span class="stat-max">/4 max</span></div>
      <div class="stat-pill"><span class="stat-label">🧤 KEEPERS</span><span class="stat-value" style="color:{wk_cl};">{wk_c2}</span><span class="stat-max">min 1</span></div>
      <div class="stat-pill"><span class="stat-label">🔴 BOWLERS</span><span class="stat-value" style="color:{bw_cl};">{bw_c2}</span><span class="stat-max">/3 min</span></div>
    </div>''', unsafe_allow_html=True)

    if len(final_squad)==11 and os_c2<=4 and wk_c2>=1 and bw_c2>=3:
        cap = st.selectbox("🛡️ Select Captain (2× points)", final_squad,
                           index=(final_squad.index(saved["cap"]) if saved["cap"] in final_squad else 0),
                           disabled=is_locked)
        if not is_locked and st.button("🚀  LOCK IN SQUAD", type="primary", use_container_width=True):
            if active_week_name not in db["selections"]: db["selections"][active_week_name] = {}
            db["selections"][active_week_name][user] = {"squad": final_squad, "cap": cap}
            save_db(db); st.success("✅ Squad saved! Good luck this week!")
    else:
        st.warning("⚠️ Complete your squad: exactly 11 players | max 4 overseas | min 1 keeper | min 3 bowlers")

with t_view:
    st.markdown('<div class="section-header">ALL MANAGERS\' SQUADS</div>', unsafe_allow_html=True)
    cols = st.columns(len(db["pools"]))
    for i, mgr in enumerate(db["pools"].keys()):
        with cols[i]:
            s_data = db["selections"].get(active_week_name, {}).get(mgr, None)
            st.markdown(f'<div class="squad-mgr-title">⚡ {mgr}</div>', unsafe_allow_html=True)
            if s_data:
                st.markdown('<div class="squad-view-box">', unsafe_allow_html=True)
                def squad_sort_key(p):
                    if p == s_data["cap"]: return 0
                    role = db["player_master"].get(p, {}).get("role", "BAT")
                    return {"BAT": 1, "WK": 2, "BOWL": 3}.get(role, 1)

                for player in sorted(s_data["squad"], key=squad_sort_key):
                    info     = db["player_master"].get(player, {})
                    cap_tag  = '<span class="cap-badge">CAP</span>' if player == s_data["cap"] else ""
                    tc       = TEAM_COLORS.get(info.get("team",""), "#888")
                    role_icon = {"BAT":"🏏","WK":"🧤","BOWL":"🔴"}.get(info.get("role",""),"🏏")
                    st.markdown(f'<div class="squad-player-row"><span><span style="color:{tc};font-size:9px;">●</span> {role_icon} {player} <span style="color:rgba(210,225,255,0.55);font-size:10px;">({info.get("team","")})</span></span>{cap_tag}</div>', unsafe_allow_html=True)
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

    # ══ SCORE MANAGEMENT ═════════════════════════════════════════════════════
    st.markdown('<div class="section-header">🛡️ SCORE MANAGEMENT</div>', unsafe_allow_html=True)

    st.markdown("""<div class="scoring-rule-box">
    <strong>Scoring:</strong> Run=1pt | Wicket=20pt | Catch/Full RO=5pt | Half RO=2.5pt (enter 0.5) | Stumping=5pt | MOM=100pt<br>
    <strong>Bonuses:</strong> 50+runs→+5pt | 100+runs→+10pt | 3+wkts→+5pt | 5+wkts→+10pt
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="admin-box">', unsafe_allow_html=True)
    sel_mid = st.selectbox("Select Match", list(matches_this_week.keys()),
                           format_func=lambda x: f"{x} — {matches_this_week[x]}")
    teams = matches_this_week[sel_mid].split(" vs ")

    # ══ AUTO-FETCH WITH ERROR DISPLAY + TEST CONNECTION + CLEAR CACHE ════════
    st.markdown('<div class="fetch-box">', unsafe_allow_html=True)
    st.markdown('<div class="fetch-box-title">🌐 AUTO-FETCH FROM ESPNcricinfo</div>', unsafe_allow_html=True)

    espn_url_input = st.text_input(
        "ESPNcricinfo Scorecard URL",
        value="",
        key=f"espnurl_{sel_mid}",
        placeholder="https://www.espncricinfo.com/series/.../full-scorecard",
        help="Go to espncricinfo.com → open the match → click Full Scorecard tab → copy the URL"
    )
    st.markdown(
        '<div style="font-size:11px;color:rgba(180,210,255,0.75);font-family:\'Rajdhani\',sans-serif;padding:4px 0 8px;">'
        '🔗 <b>How:</b> espncricinfo.com → Series → Match → <b>Full Scorecard</b> tab → copy full URL from browser bar</div>',
        unsafe_allow_html=True
    )

    btn1, btn2, btn3 = st.columns(3)
    fetch_clicked = btn1.button("⬇️  FETCH SCORECARD",    key=f"fetch_{sel_mid}",  use_container_width=True)
    test_clicked  = btn2.button("🔍  TEST CONNECTION",     key="test_conn",          use_container_width=True)
    clear_clicked = btn3.button("🗑️  CLEAR CACHE & RETRY", key="clear_cache",        use_container_width=True)

    if test_clicked:
        with st.spinner("Testing connection to ESPNcricinfo..."):
            ok, msg = test_fetch_connection()
        if ok: st.success(msg)
        else:
            st.error(msg)
            st.warning("⚠️ ESPNcricinfo blocked — enter scores manually below.")

    if clear_clicked:
        st.cache_data.clear()
        st.success("✅ Cache cleared — click Fetch Scorecard again.")

    if fetch_clicked and espn_url_input.strip():
        with st.spinner("🏏 Fetching scorecard from ESPNcricinfo..."):
            result = fetch_scorecard(espn_url_input.strip())

        if result.get("error") and not result.get("stats"):
            st.error(f"❌ Fetch failed: {result['error']}")
            st.markdown(
                '<div style="font-size:12px;color:rgba(200,220,255,0.7);font-family:\'Rajdhani\',sans-serif;margin-top:4px;">'
                '💡 <b>HTTP 403</b> → ESPNcricinfo blocked — enter scores manually.<br>'
                '💡 <b>HTTP 404</b> → URL wrong — make sure it ends in <code>/full-scorecard</code>.<br>'
                '💡 <b>No stats</b> → Match not started or scorecard not published yet.<br>'
                '💡 Try <b>Clear Cache &amp; Retry</b> if match has finished since last fetch.'
                '</div>', unsafe_allow_html=True
            )
        else:
            if result.get("error"):
                st.warning(f"⚠️ {result['error']}")
            mapped, unmatched = map_fetched_to_pool(result["stats"], db["player_master"])
            st.markdown(f'<div style="color:#a5d6a7;font-family:\'Roboto Condensed\',sans-serif;font-size:13px;margin:8px 0 4px;">✅ Fetched {len(result["stats"])} players · matched <b>{len(mapped)}</b> · <span style="color:#ffa726;">{len(unmatched)} unmatched</span></div>', unsafe_allow_html=True)

            if result.get("raw_batting"):
                st.markdown('<div style="font-family:\'Bebas Neue\',sans-serif;font-size:0.85rem;letter-spacing:2px;color:#ffd700;margin:10px 0 4px;">BATTING</div>', unsafe_allow_html=True)
                for b in result["raw_batting"][:12]:
                    pm_n = _best_match(b["name"], list(db["player_master"].keys()))
                    mc = "mapped-good" if pm_n else "mapped-warn"
                    pm_label = f"→ {pm_n}" if pm_n else "⚠️ no match"
                    st.markdown(f'<div class="mapped-row {mc}"><span>{b["name"]}</span><span style="color:rgba(200,220,255,0.6);font-size:10px;">{pm_label}</span><span style="color:#ffd700;font-family:\'Bebas Neue\',sans-serif;">{b["runs"]}r</span></div>', unsafe_allow_html=True)

            if result.get("raw_bowling"):
                st.markdown('<div style="font-family:\'Bebas Neue\',sans-serif;font-size:0.85rem;letter-spacing:2px;color:#ffd700;margin:10px 0 4px;">BOWLING</div>', unsafe_allow_html=True)
                for bw in result["raw_bowling"][:10]:
                    pm_n = _best_match(bw["name"], list(db["player_master"].keys()))
                    mc = "mapped-good" if pm_n else "mapped-warn"
                    pm_label = f"→ {pm_n}" if pm_n else "⚠️ no match"
                    st.markdown(f'<div class="mapped-row {mc}"><span>{bw["name"]}</span><span style="color:rgba(200,220,255,0.6);font-size:10px;">{pm_label}</span><span style="color:#90caf9;font-family:\'Bebas Neue\',sans-serif;">{bw["wickets"]}w</span></div>', unsafe_allow_html=True)

            if unmatched:
                st.markdown(f'<div style="font-size:11px;color:#ffa726;font-family:\'Rajdhani\',sans-serif;margin-top:6px;">⚠️ Unmatched: {", ".join(unmatched)}</div>', unsafe_allow_html=True)

            apply_col, _ = st.columns([2, 3])
            if apply_col.button("✅  APPLY FETCHED SCORES", key=f"apply_{sel_mid}", use_container_width=True):
                for canon_name, vals in mapped.items():
                    if canon_name not in db["scores"]: db["scores"][canon_name] = {}
                    existing = db["scores"][canon_name].get(sel_mid, {"r":0,"w":0,"c":0.0,"s":0,"mom":0})
                    db["scores"][canon_name][sel_mid] = {
                        "r": vals.get("r", existing["r"]),
                        "w": vals.get("w", existing["w"]),
                        "c": vals.get("c", existing["c"]),
                        "s": vals.get("s", existing["s"]),
                        "mom": existing.get("mom", 0),
                    }
                save_db(db)
                st.success(f"✅ Applied {len(mapped)} player scores. Review below then push.")
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)  # end fetch-box

    # ── Manual player search ──────────────────────────────────────────────────
    st.markdown("**🔍 Add extra player** (search full master if team assignment is wrong):")
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
        (hdr[2],"🔴 WICKETS","1w=20pt | 3+=+5 | 5+=+10"),
        (hdr[3],"🤲 CATCH/RO","1=5pt | 0.5=2.5pt"),
        (hdr[4],"🧤 STUMPING","1 = 5 pts"),
        (hdr[5],"PTS","live"),
    ]:
        col.markdown(f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:0.78rem;letter-spacing:1.5px;color:#ffd700;text-align:center;padding:4px 0 0;">{lbl}</div>'
                     f'<div style="font-size:9px;color:#aac0e0;font-family:\'Rajdhani\',sans-serif;text-align:center;padding-bottom:4px;">{sub}</div>', unsafe_allow_html=True)
    st.markdown('<hr style="border:none;border-top:1px solid rgba(255,215,0,0.35);margin:4px 0 8px;">', unsafe_allow_html=True)

    if eligible_squad:
        for p in sorted(eligible_squad):
            cur    = db["scores"].get(p,{}).get(sel_mid, {"r":0,"w":0,"c":0.0,"s":0,"mom":0})
            info   = db["player_master"].get(p, {})
            tc     = TEAM_COLORS.get(info.get("team",""), "#888")
            is_mom = (selected_mom == p)

            cols = st.columns([2,1,1,1,1,1])
            mom_tag = ' <span class="mom-badge">⭐ MOM</span>' if is_mom else ""
            cols[0].markdown(
                f'<div style="padding:6px 0 2px;font-family:\'Roboto Condensed\',sans-serif;font-size:13px;line-height:1.4;">'
                f'<span style="color:{tc};font-size:10px;">●</span> <b style="color:#fff;">{p}</b>{mom_tag}<br>'
                f'<span style="color:rgba(210,230,255,0.65);font-size:10px;">({info.get("team","")}) {ROLE_EMOJI.get(info.get("role",""),"")}</span></div>',
                unsafe_allow_html=True
            )
            r = cols[1].number_input("Runs",     min_value=0,   max_value=300,  value=int(cur.get("r",0)),     step=1,   key=f"r_{sel_mid}_{p}")
            w = cols[2].number_input("Wkts",     min_value=0,   max_value=10,   value=int(cur.get("w",0)),     step=1,   key=f"w_{sel_mid}_{p}")
            c = cols[3].number_input("Catch/RO", min_value=0.0, max_value=10.0, value=float(cur.get("c",0.0)), step=0.5, key=f"c_{sel_mid}_{p}")
            s = cols[4].number_input("Stumping", min_value=0,   max_value=10,   value=int(cur.get("s",0)),     step=1,   key=f"s_{sel_mid}_{p}")

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
        st.info("No eligible players found. Submit squads first, or use the search above to add a player manually.")

    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🚀  PUSH SCORES", type="primary", use_container_width=True):
        if selected_mom and selected_mom != "— None —":
            for p in list(db["scores"].keys()):
                if sel_mid in db["scores"][p]:
                    db["scores"][p][sel_mid]["mom"] = 1 if p == selected_mom else 0
        save_db(db)
        st.success("✅ Scores saved! Leaderboard updates automatically.")

    # ══ DANGER ZONE ══════════════════════════════════════════════════════════
    st.markdown('<div class="section-header">⚠️ DANGER ZONE</div>', unsafe_allow_html=True)
    st.markdown('<div class="admin-box">', unsafe_allow_html=True)
    reset_confirm = st.checkbox("☢️ Confirm: Permanently delete ALL selections and scores.")
    if reset_confirm and st.button("💣  CLEAR ALL DATA", type="primary"):
        empty = {"selections": {}, "scores": {}, "pools": _build_excel_pools(), "player_master": _build_player_master()}
        save_db(empty)  # wipes gist AND local file
        if os.path.exists(DB_FILE): os.remove(DB_FILE)
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
with t_restore:
    st.markdown('<div class="section-header">🔐 RESTORE SQUADS</div>', unsafe_allow_html=True)
    st.markdown("""<div style="background:rgba(255,100,0,0.10);border:1px solid rgba(255,140,0,0.35);
        border-radius:8px;padding:10px 14px;margin-bottom:16px;font-family:'Rajdhani',sans-serif;
        font-size:13px;color:#ffe0b2;">
        🔒 Password protected. Use this to restore lost squads or override entries after the deadline.
        Bypasses the lock entirely — saves directly to the database.
    </div>""", unsafe_allow_html=True)

    # ── Password gate ─────────────────────────────────────────────────────────
    RESTORE_PASSWORD = "ipl2026"
    pwd_input = st.text_input("Enter restore password", type="password", key="restore_pwd")

    if not pwd_input:
        st.info("🔑 Enter the password above to access squad restore tools.")
    elif pwd_input != RESTORE_PASSWORD:
        st.error("❌ Incorrect password.")
    else:
        st.success("✅ Access granted.")
        st.markdown('<hr style="border:none;border-top:1px solid rgba(255,215,0,0.25);margin:12px 0;">', unsafe_allow_html=True)

        # ── Week selector (can restore for any week, not just active) ─────────
        restore_week = st.selectbox(
            "Restore squad for which week?",
            list(SEASON_WEEKS.keys()),
            index=list(SEASON_WEEKS.keys()).index(active_week_name),
            key="restore_week"
        )

        # ── Manager selector ──────────────────────────────────────────────────
        restore_mgr  = st.selectbox("Select Manager", list(db["pools"].keys()), key="restore_mgr")
        r_pool       = db["pools"].get(restore_mgr, [])
        existing_sel = db["selections"].get(restore_week, {}).get(restore_mgr, {"squad": [], "cap": ""})

        # Show existing squad if any
        if existing_sel.get("squad"):
            st.markdown(f'<div style="font-size:12px;color:#a5d6a7;font-family:\'Rajdhani\',sans-serif;margin-bottom:6px;">ℹ️ {restore_mgr} already has a squad for {restore_week} — shown below. Override it if needed.</div>', unsafe_allow_html=True)

        # ── PASTE TO DETECT ───────────────────────────────────────────────────
        st.markdown("""<div style="background:rgba(0,120,255,0.10);border:1px solid rgba(100,180,255,0.30);
            border-radius:8px;padding:10px 14px;margin:10px 0 8px;font-family:'Rajdhani',sans-serif;font-size:13px;color:#cce4ff;">
            📋 <b>Paste squad list</b> — paste any text containing player names (WhatsApp message, notes, etc.)
            and the app will auto-detect matching players from the pool.
        </div>""", unsafe_allow_html=True)

        paste_text = st.text_area(
            "Paste player list here",
            height=120,
            key=f"paste_{restore_mgr}_{restore_week}",
            placeholder="e.g.\n1. Virat Kohli (c)\n2. Rohit Sharma\nJasprit Bumrah\nMS Dhoni (wk)\n..."
        )

        detected_players = []
        undetected_lines = []

        if paste_text.strip():
            # Split on newlines and common separators
            import re as _re
            raw_lines = _re.split(r"[\n,;|]+", paste_text)
            pm_names  = list(db["player_master"].keys())

            for raw in raw_lines:
                # Strip numbering, bullets, role tags, brackets, emojis
                cleaned = _re.sub(r"^\s*[\d\.\-\*\•]+\s*", "", raw)        # leading numbers/bullets
                cleaned = _re.sub(r"\(c\)|\(wk\)|\(vc\)", "", cleaned, flags=_re.I)  # role tags
                cleaned = _re.sub(r"\([^)]*\)", "", cleaned)                # anything in brackets
                cleaned = _re.sub(r"[^\w\s\-\']", "", cleaned)             # non-word chars
                cleaned = cleaned.strip()
                if len(cleaned) < 3:
                    continue

                # Try exact match first
                match = next((p for p in pm_names if p.lower() == cleaned.lower()), None)

                # Try fuzzy match if no exact match
                if not match:
                    match = _best_match(cleaned, pm_names, threshold=0.60)

                # Try matching last name only (e.g. "Kohli" → "Virat Kohli")
                if not match:
                    last_word = cleaned.split()[-1].lower()
                    candidates = [p for p in pm_names if p.lower().split()[-1] == last_word]
                    if len(candidates) == 1:
                        match = candidates[0]

                if match:
                    if match not in detected_players:
                        detected_players.append(match)
                else:
                    if cleaned:
                        undetected_lines.append(cleaned)

            # Show detection results
            if detected_players:
                st.markdown(f'<div style="color:#a5d6a7;font-family:\'Roboto Condensed\',sans-serif;font-size:13px;margin:6px 0 4px;">✅ Detected <b>{len(detected_players)}</b> players</div>', unsafe_allow_html=True)
                for dp in detected_players:
                    info = db["player_master"].get(dp, {})
                    tc   = TEAM_COLORS.get(info.get("team",""), "#888")
                    ri   = {"BAT":"🏏","WK":"🧤","BOWL":"🔴"}.get(info.get("role",""),"🏏")
                    in_pool = "✓" if dp in r_pool else "⚠️ not in pool"
                    in_pool_color = "#a5d6a7" if dp in r_pool else "#ffa726"
                    st.markdown(
                        f'<div style="display:flex;justify-content:space-between;align-items:center;'
                        f'padding:3px 8px;border-radius:5px;margin-bottom:2px;background:rgba(255,255,255,0.06);">'
                        f'<span><span style="color:{tc};font-size:9px;">●</span> {ri} <b style="color:#eef2ff;">{dp}</b> '
                        f'<span style="color:rgba(210,225,255,0.55);font-size:10px;">({info.get("team","")})</span></span>'
                        f'<span style="color:{in_pool_color};font-size:11px;font-family:\'Rajdhani\',sans-serif;">{in_pool}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

            if undetected_lines:
                st.markdown(f'<div style="color:#ffa726;font-size:11px;font-family:\'Rajdhani\',sans-serif;margin-top:4px;">⚠️ Could not match: {", ".join(undetected_lines)}</div>', unsafe_allow_html=True)

            # Apply detected to multiselect default
            if detected_players and st.button("⚡  USE DETECTED PLAYERS", key=f"use_detected_{restore_mgr}", use_container_width=False):
                st.session_state[f"restore_squad_{restore_mgr}_{restore_week}"] = [p for p in detected_players if p in r_pool]
                st.rerun()

        st.markdown('<hr style="border:none;border-top:1px solid rgba(255,255,255,0.10);margin:10px 0 8px;">', unsafe_allow_html=True)

        # ── Squad multiselect — pre-filled from paste detection or existing ───
        paste_default = st.session_state.get(
            f"restore_squad_{restore_mgr}_{restore_week}",
            [p for p in existing_sel.get("squad", []) if p in r_pool]
        )
        # ── Squad multiselect ─────────────────────────────────────────────────
        r_squad = st.multiselect(
            f"Select 11 players for {restore_mgr}",
            options=sorted(r_pool),
            default=[p for p in paste_default if p in r_pool],
            key=f"restore_squad_{restore_mgr}_{restore_week}"
        )

        # ── Live validation metrics ───────────────────────────────────────────
        r_os   = sum(1 for p in r_squad if db["player_master"].get(p,{}).get("is_overseas"))
        r_wk   = sum(1 for p in r_squad if db["player_master"].get(p,{}).get("role")=="WK")
        r_bowl = sum(1 for p in r_squad if db["player_master"].get(p,{}).get("role")=="BOWL")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Players",  f"{len(r_squad)}/11",  delta=None)
        m2.metric("Overseas", f"{r_os}/4 max",        delta=None)
        m3.metric("Keepers",  f"{r_wk} (min 1)",      delta=None)
        m4.metric("Bowlers",  f"{r_bowl} (min 3)",     delta=None)

        # ── Captain selector ──────────────────────────────────────────────────
        r_cap_options = r_squad if r_squad else ["— pick squad first —"]
        r_cap_default = existing_sel.get("cap", "")
        r_cap = st.selectbox(
            "🛡️ Captain (2× points)",
            r_cap_options,
            index=(r_cap_options.index(r_cap_default) if r_cap_default in r_cap_options else 0),
            key=f"restore_cap_{restore_mgr}_{restore_week}"
        )

        # ── Show selected squad preview ───────────────────────────────────────
        if r_squad:
            st.markdown('<div style="font-family:\'Bebas Neue\',sans-serif;font-size:0.85rem;letter-spacing:2px;color:#ffd700;margin:10px 0 4px;">SQUAD PREVIEW</div>', unsafe_allow_html=True)
            def r_sort(p):
                if p == r_cap: return 0
                return {"BAT":1,"WK":2,"BOWL":3}.get(db["player_master"].get(p,{}).get("role","BAT"),1)
            for pl in sorted(r_squad, key=r_sort):
                info   = db["player_master"].get(pl, {})
                tc     = TEAM_COLORS.get(info.get("team",""), "#888")
                ri_map = {"BAT":"🏏","WK":"🧤","BOWL":"🔴"}
                ri     = ri_map.get(info.get("role",""),"🏏")
                cap_tag = ' <span class="cap-badge">CAP</span>' if pl == r_cap else ""
                st.markdown(
                    f'<div class="squad-player-row"><span>'
                    f'<span style="color:{tc};font-size:9px;">●</span> {ri} {pl} '
                    f'<span style="color:rgba(210,225,255,0.55);font-size:10px;">({info.get("team","")})</span>'
                    f'</span>{cap_tag}</div>',
                    unsafe_allow_html=True
                )

        st.markdown('<br>', unsafe_allow_html=True)

        # ── Save button ───────────────────────────────────────────────────────
        r_valid = len(r_squad)==11 and r_os<=4 and r_wk>=1 and r_bowl>=3 and r_cap in r_squad
        if st.button("💾  FORCE SAVE SQUAD", type="primary", use_container_width=True, disabled=not r_valid):
            if restore_week not in db["selections"]:
                db["selections"][restore_week] = {}
            db["selections"][restore_week][restore_mgr] = {"squad": r_squad, "cap": r_cap}
            save_db(db)
            st.success(f"✅ Squad restored for **{restore_mgr}** — Week: {restore_week} — Captain: {r_cap}")
            st.balloons()
        if not r_valid and r_squad:
            st.warning("⚠️ Fix squad: exactly 11 players | ≤4 overseas | ≥1 keeper | ≥3 bowlers | captain selected")
