import sqlite3

conn=sqlite3.connect("quiz.db")

conn.execute("""
CREATE TABLE students(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
email TEXT,
password TEXT
)
""")

conn.commit()
conn.close()

print("Database created")