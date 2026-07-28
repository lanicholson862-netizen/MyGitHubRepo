import sqlite3

DB_Name = "project.db"

conn = sqlite3.connect(DB_Name)
cursor = conn.cursor()

conn.execute("""
    CREATE TABLE IF NOT EXISTS Orders(
        orderID INTEGER PRIMARY KEY,
        dishID INTEGER NOT NULL,
        FOREIGN KEY(dishID) REFERENCES Dish(dishID)
    )
""")