import sqlite3

DB_Name = "project.db"

conn = sqlite3.connect(DB_Name)
cursor = conn.cursor()

