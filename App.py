import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# --- 1. GLOBAL DATA ---
TEAM_STYLING = {
    'RCB': '#d11d26', 'MI': '#004ba0', 'CSK': '#fdb913', 'SRH': '#f26522',
    'RR': '#ea1a85', 'KKR': '#3a225d', 'GT': '#1b2133', 'LSG': '#0057e2',
    'DC': '#0078bc', 'PBKS': '#dd1f2d'
}

# Sat-Fri Cycle Schedule
SEASON_WEEKS = {
    "Week 1 (Mar 28 - Apr 03)": [
        "Match 01: RCB vs SRH (Sat)", "Match 02: MI vs KKR (Sun)", 
        "Match 03: RR vs CSK (Mon)", "Match 04: PBKS vs GT (Tue)",
        "Match 05: LSG vs DC (Wed)", "Match 06: KKR vs SRH (Thu)",
        "Match 07: CSK vs PBKS (Fri)"
    ],
    "Week 2 (Apr 04 - Apr 10)": [
        "Match 08: DC vs MI (Sat)", "Match 09: GT vs RR (Sat)", 
        "Match 10: SRH vs LSG (Sun)", "Match 11: RCB vs CSK (Mon)",
        "Match 12: KKR vs PBKS (Tue)", "Match 13: RR vs MI (Wed)",
        "Match 14: DC vs GT (Thu)", "Match 15: KKR vs LSG (Fri)"
    ]
}

MEMBER_POOLS = {
    'Kazim': ['Rajat Patidar', 'Devdutt Padikkal', 'Shimron Hetmyer', 'Dhruv Jurel', 'Vaibhav Suryavanshi', 'Priyansh Arya', 'Ryan Rickelton', 'Aiden Markram', 'Angkrish Raghuvanshi', 'Shahrukh Khan', 'Nitish Rana', 'Prashant Veer', 'Anshul Kambhoj', 'Axar Patel', 'Gudakesh Motie', 'Will Jacks', 'Marcus Stoinis', 'Shashank Singh', 'Nitish Kumar Reddy', 'Pat Cummins', 'Jacob Duffy', 'Josh Hazlewood'],
    'Adi': ['Philip Salt', 'Yashasvi Jaiswal', 'Prabhsimran Singh', 'Nicholas Pooran', 'Tim Seifert', 'Shubman Gill', 'Ayush Mhatre', 'Ashutosh Sharma', 'Rahul Tewatia', 'Jasprit Bumrah', 'Ravindra Jadeja', 'Abhishek Sharma', 'Harshal Patel', 'Jofra Archer', 'Yuzvendra Chahal', 'Allah Ghazanfar', 'Digvesh Rathi', 'Prasidh Krishna', 'Umran Malik', 'Vipraj Nigam'],
    'Aatish': ['Tim David', 'Jitesh Sharma', 'Nehal Wadhera', 'Quinton de Kock', 'Sherfane Rutherford', 'Rohit Sharma', 'Rishabh Pant', 'Abdul Samad', 'Matthew Breetzke', 'Abishek Porel', 'Tristan Stubbs', 'Pathum Nissanka', 'MS Dhoni', 'Dewald Brevis', 'Shivam Dube', 'Rashid Khan', 'Sunil Narine', 'Shahbaz Ahmed', 'Hardik Pandya', 'Donovan Ferreira', 'Jacob Bethell'],
    'Shreejith': ['Travis Head', 'Ishan Kishan', 'Riyan Parag', 'Shreyas Iyer', 'Ayush Badoni', 'Himmat Singh', 'Manish Pandey', 'Ajinkya Rahane', 'Sai Sudharsan', 'Vishnu Vinod', 'Sarfaraz Khan', 'Ruturaj Gaik
                  
