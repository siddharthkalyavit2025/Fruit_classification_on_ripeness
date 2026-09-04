import sys
import os
sys.path.insert(0, 'd:/fcar/backend')
from database.database import get_connection

conn = get_connection()
cursor = conn.execute("UPDATE predictions SET sorting_status = 'SIMULATED' WHERE sorting_status = 'ARDUINO_ERROR'")
conn.commit()
print(f"Updated {cursor.rowcount} records from ARDUINO_ERROR to SIMULATED")
conn.close()
