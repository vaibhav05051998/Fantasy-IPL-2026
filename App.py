# --- 1. GLOBAL DATA UPDATED ---
# Overseas identification logic based on common IPL names
MEMBER_POOLS = {
    'Kazim': ['Rajat Patidar', 'Devdutt Padikkal', 'Shimron Hetmyer', 'Dhruv Jurel', 'Vaibhav Suryavanshi', 'Priyansh Arya', 'Ryan Rickelton', 'Aiden Markram', 'Angkrish Raghuvanshi', 'Jos Buttler', 'David Miller', 'Ben Duckett', 'Nitish Rana', 'Prashant Veer', 'Anshul Kambhoj', 'Axar Patel', 'Gudakesh Motie', 'Will Jacks', 'Marcus Stoinis', 'Shashank Singh', 'Nitish Kumar Reddy', 'Pat Cummins', 'Jacob Duffy', 'Josh Hazlewood', 'Ravi Bishnoi', 'Avesh Khan', 'Ravi Sai Kishore', 'Noor Ahmad', 'Blessing Muzarabani', 'Lockie Ferguson'],
    'Adi': ['Philip Salt', 'Yashasvi Jaiswal', 'Prabhsimran Singh', 'Nicholas Pooran', 'Tim Seifert', 'Shubman Gill', 'Ayush Mhatre', 'Ashutosh Sharma', 'Rahul Tewatia', 'Washington Sundar', 'Cooper Connolly', 'Azmatullah Omarzai', 'Ravindra Jadeja', 'Abhishek Sharma', 'Harshal Patel', 'Jofra Archer', 'Yuzvendra Chahal', 'Allah Ghazanfar', 'Digvesh Rathi', 'Prasidh Krishna', 'Umran Malik', 'Vipraj Nigam'],
    'Aatish': ['Tim David', 'Jitesh Sharma', 'Nehal Wadhera', 'Quinton de Kock', 'Sherfane Rutherford', 'Rohit Sharma', 'Rishabh Pant', 'Abdul Samad', 'Matthew Breetzke', 'Rahul Tripathi', 'Finn Allen', 'Shahrukh Khan', 'Tristan Stubbs', 'Pathum Nissanka', 'MS Dhoni', 'Dewald Brevis', 'Shivam Dube', 'Rashid Khan', 'Sunil Narine', 'Shahbaz Ahmed', 'Hardik Pandya', 'Donovan Ferreira', 'Jacob Bethell', 'Romario Shepherd', 'Yash Dayal', 'Deepak Chahar', 'Vaibhav Arora', 'Mohammed Siraj', 'Kuldeep Yadav', 'Khaleel Ahmed', 'Mukesh Choudhary', 'Rahul Chahar', 'Mayank Yadav', 'Harpreet Brar', 'Tushar Deshpande'],
    'Shreejith': ['Travis Head', 'Ishan Kishan', 'Riyan Parag', 'Shreyas Iyer', 'Ayush Badoni', 'Himmat Singh', 'Manish Pandey', 'Ajinkya Rahane', 'Sai Sudharsan', 'Prithvi Shaw', 'Karun Nair', 'Abishek Porel', 'Sarfaraz Khan', 'Ruturaj Gaikwad', 'Ramakrishna Ghosh', 'Mitchell Marsh', 'Krunal Pandya', 'Venkatesh Iyer', 'Jaydev Unadkat', 'Suyash Sharma', 'Sandeep Sharma', 'Arshdeep Singh', 'Trent Boult', 'Mohammed Shami', 'Kagiso Rabada', 'Mitchell Santner', 'Kartik Sharma'],
    'Nagle': ['Heinrich Klaasen', 'Virat Kohli', 'Suryakumar Yadav', 'Rinku Singh', 'KL Rahul', 'Sanju Samson', 'Cameron Green', 'Tilak Varma', 'Marco Jansen', 'Liam Livingstone', 'Bhuvneshwar Kumar', 'Jasprit Bumrah', 'Varun Chakaravarthy', 'Lungi Ngidi', 'Jason Holder', 'Mitchell Starc']
}

# Players list with full attributes
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
    'Matthew Breetzke', 'Abishek Porel', 'MS Dhoni', 'Donovan Ferreira', 'Ishan Kishan', 
    'Sanju Samson', 'KL Rahul', 'Heinrich Klaasen', 'Josh Inglis'
]

# Function to generate master data
def get_role(name):
    if name in WK_LIST: return 'WK'
    # List of known bowlers for logic
    bowlers = ['Bishnoi', 'Avesh', 'Kishore', 'Noor', 'Muzarabani', 'Lockie', 'Bumrah', 'Chahal', 'Archer', 'Prasidh', 'Umran', 'Dayal', 'Siraj', 'Kuldeep', 'Boult', 'Shami', 'Rabada', 'Starc', 'Varun', 'Ngidi']
    if any(b in name for b in bowlers): return 'BOWL'
    return 'BAT'

PLAYER_MASTER = {
    name: {
        'team': 'IPL', # Default, will be updated by Admin
        'role': get_role(name),
        'is_overseas': name in OVERSEAS_LIST
    } for pool in MEMBER_POOLS.values() for name in pool
}
