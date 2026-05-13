import sqlite3
import os

db_path = os.path.join('instance', 'food_delivery.db')
conn = sqlite3.connect(db_path)
c = conn.cursor()

try:
    c.execute('ALTER TABLE "order" ADD COLUMN restaurant_instructions TEXT')
    print("Added restaurant_instructions")
except sqlite3.OperationalError as e:
    print(f"Skipped: {e}")

try:
    c.execute('ALTER TABLE "order" ADD COLUMN delivery_instructions TEXT')
    print("Added delivery_instructions")
except sqlite3.OperationalError as e:
    print(f"Skipped: {e}")
    
conn.commit()
conn.close()
print("Done")
