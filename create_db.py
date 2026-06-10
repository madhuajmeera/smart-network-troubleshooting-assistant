# import sqlite3

# conn = sqlite3.connect('database.db')

# cursor = conn.cursor()

# cursor.execute('''
# CREATE TABLE IF NOT EXISTS tickets (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     customer_name TEXT,
#     issue_type TEXT,
#     status TEXT
# )
# ''')

# conn.commit()
# conn.close()

# print("Database created successfully")


import sqlite3

conn = sqlite3.connect('database.db')

cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT,
password TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT,
password TEXT
)
''')

conn.commit()
conn.close()

print("Database created successfully")


