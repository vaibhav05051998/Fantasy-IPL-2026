app py
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
HISTORY
