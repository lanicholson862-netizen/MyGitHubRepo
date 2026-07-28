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

conn.execute("""
    CREATE TABLE IF NOT EXISTS Customers(
        custID INTEGER PRIMARY KEY,
        custFirstName TEXT NOT NULL,
        custSecondName TEXT NOT NULL,
        custEmail TEXT NOT NULL,
        custAddress TEXT NOT NULL,
        suburb TEXT NOT NULL,
        PostCode INTEGER NOT NULL, 
        custPhoneNo TEXT NOT NULL
    )
""")

conn.execute("""
    CREATE TABLE IF NOT EXISTS Restraunt(
        restrauntID INTEGER PRIMARY KEY,
        restrauntName TEXT NOT NULL,
        restrauntAddress TEXT NOT NULL,
        restrauntPhoneNo TEXT NOT NULL
    )
""")

conn.execute("""
    CREATE TABLE IF NOT EXISTS Dish(
        dishID INTEGER PRIMARY KEY,
        restrauntID INTEGER NOT NULL,
        dishName TEXT NOT NULL, 
        dishPrice REAL NOT NULL,
        FOREIGN KEY(restrauntID) REFERENCES Restraunt(restrauntID)
    )
""")