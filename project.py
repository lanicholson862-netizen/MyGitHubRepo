import sqlite3
import os
import csv

DB_Name = "project.db"

conn = sqlite3.connect(DB_Name)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS Orders(
        orderID INTEGER PRIMARY KEY,
        custID INTEGER NOT NULL,
        dishID INTEGER NOT NULL,
        orderDate TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        totalAmmount REAL NOT NULL,
        FOREIGN KEY(dishID) REFERENCES Dish(dishID),
        FOREIGN KEY(custID) REFERENCES Customers(custID)
    )
""")

cursor.execute("""
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

cursor.execute("""
    CREATE TABLE IF NOT EXISTS Restraunt(
        restrauntID INTEGER PRIMARY KEY,
        restrauntName TEXT NOT NULL,
        restrauntAddress TEXT NOT NULL,
        restrauntPhoneNo TEXT NOT NULL
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS Dish(
        dishID INTEGER PRIMARY KEY,
        restrauntID INTEGER NOT NULL,
        dishName TEXT NOT NULL, 
        dishPrice REAL NOT NULL,
        FOREIGN KEY(restrauntID) REFERENCES Restraunt(restrauntID)
    )
""")


with open("customers.csv", "r", encoding="utf-8-sig") as custData:
    reader = csv.reader(custData)
    next(reader)

    for row in reader:
        cursor.execute(
            "INSERT INTO Customers VALUES (?, ?, ?, ?, ?, ?, ?, ?)", row
            )