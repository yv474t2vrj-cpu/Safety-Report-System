import sqlite3

# Connect to the database
conn = sqlite3.connect('D:/SAFETY/data/incidents.db')
cursor = conn.cursor()

# Add new columns if they don't exist
try:
    cursor.execute("ALTER TABLE incident ADD COLUMN reporter_email TEXT")
    print("✓ Added reporter_email column")
except:
    print("reporter_email column already exists")

try:
    cursor.execute("ALTER TABLE incident ADD COLUMN assigned_to TEXT")
    print("✓ Added assigned_to column")
except:
    print("assigned_to column already exists")

try:
    cursor.execute("ALTER TABLE incident ADD COLUMN notes TEXT")
    print("✓ Added notes column")
except:
    print("notes column already exists")

# Commit changes and close
conn.commit()
conn.close()
print("Database updated successfully!")