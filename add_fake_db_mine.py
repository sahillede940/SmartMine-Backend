import sqlite3
import numpy as np
from faker import Faker
import datetime

# Initialize Faker
fake = Faker()

# Start date for data generation
start_date = datetime.datetime(2024, 11, 3, 0, 0, 0)

# Real machine names and types
machine_data = [
    {"name": "CAT 797F", "type": "Excavator", "date": start_date},
    {"name": "Komatsu PC8000", "type": "Excavator", "date": start_date},
    {"name": "Volvo EC950F", "type": "Excavator", "date": start_date},
    {"name": "Sandvik DD422i", "type": "Drill", "date": start_date},
    {"name": "Caterpillar MD6310", "type": "Drill", "date": start_date},
    {"name": "Joy Overland Conveyor", "type": "Conveyor Belt", "date": start_date},
    {"name": "Fenner Dunlop Conveyor Systems", "type": "Conveyor Belt", "date": start_date},
    {"name": "Liebherr T 284", "type": "Loader", "date": start_date},
    {"name": "CAT 994K", "type": "Loader", "date": start_date},
    {"name": "Sandvik LH621i", "type": "Loader", "date": start_date},
]

# Database file
db_file = "mining_machines.db"

# Create SQLite connection
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Create the table schema with indexes
cursor.execute("""
CREATE TABLE IF NOT EXISTS Machines (
    machine_id TEXT PRIMARY KEY,
    machine_name TEXT,
    machine_type TEXT,
    operating_hours INTEGER,
    fuel_consumption REAL,
    temperature REAL,
    vibration_levels REAL,
    load_capacity_utilization INTEGER,
    maintenance_status TEXT,
    breakdown_frequency INTEGER,
    location TEXT,
    safety_alarms_triggered INTEGER,
    power_usage REAL,
    dust_levels REAL,
    ore_processed INTEGER,
    created_at DATETIME
);
""")

# Add indexes
cursor.execute("CREATE INDEX IF NOT EXISTS idx_machine_type ON Machines(machine_type);")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_operating_hours ON Machines(operating_hours);")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON Machines(created_at);")

# Number of entries
num_entries = 4000

# Insert data
data = []
for i in range(num_entries):
    machine = np.random.choice(machine_data)
    machine_id = f"{machine['type'][:2].upper()}{str(i+1).zfill(4)}"
    machine_name = machine["name"]
    machine_type = machine["type"]
    operating_hours = np.random.randint(100, 10000)
    fuel_consumption = round(np.random.uniform(5, 50), 1) if machine["type"] != "Conveyor Belt" else None
    temperature = round(np.random.uniform(30, 100), 1)
    vibration_levels = round(np.random.uniform(0.5, 5), 2)
    load_capacity_utilization = np.random.randint(50, 101)
    maintenance_status = np.random.choice(["Yes", "No"], p=[0.3, 0.7])
    breakdown_frequency = np.random.randint(0, 11)
    location = f"{fake.latitude()}, {fake.longitude()}"
    safety_alarms_triggered = np.random.randint(0, 6)
    power_usage = round(np.random.uniform(50, 500), 1)
    dust_levels = round(np.random.uniform(100, 500), 1)
    ore_processed = np.random.randint(100, 1001)
    created_at = machine["date"] + datetime.timedelta(hours=i)
    
    machine["date"] = created_at

    data.append((
        machine_id, machine_name, machine_type, operating_hours, fuel_consumption,
        temperature, vibration_levels, load_capacity_utilization, maintenance_status,
        breakdown_frequency, location, safety_alarms_triggered, power_usage,
        dust_levels, ore_processed, created_at
    ))

# Insert data into SQLite
cursor.executemany("""
INSERT INTO Machines (
    machine_id, machine_name, machine_type, operating_hours, fuel_consumption, 
    temperature, vibration_levels, load_capacity_utilization, maintenance_status, 
    breakdown_frequency, location, safety_alarms_triggered, power_usage, 
    dust_levels, ore_processed, created_at
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", data)

# Commit and close
conn.commit()
conn.close()

print(f"Data successfully inserted into {db_file} with indexes!")
