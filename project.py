import sqlite3
import os
import csv
import tkinter as tk
from tkinter import messagebox

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
            "INSERT OR IGNORE INTO Customers VALUES (?, ?, ?, ?, ?, ?, ?, ?)", row
            )

with open("orders.csv", "r", encoding="utf-8-sig") as ordersData:
    reader = csv.reader(ordersData)
    next(reader)

    for row in reader:
        cursor.execute(
            "INSERT OR IGNORE INTO Orders VALUES (?, ?, ?, ?, ?, ?)", row
            )

with open("restraunt.csv", "r", encoding="utf-8-sig") as restrauntData:
    reader = csv.reader(restrauntData)
    next(reader)

    for row in reader:
        cursor.execute(
            "INSERT OR IGNORE INTO Restraunt VALUES (?, ?, ?, ?)", row
            )

with open("dish.csv", "r", encoding="utf-8-sig") as dishData:
    reader = csv.reader(dishData)
    next(reader)

    for row in reader:
        cursor.execute(
            "INSERT OR IGNORE INTO Dish VALUES (?, ?, ?, ?)", row
            )

conn.commit()

queries = {
    1: {"title" : "Retrieve all orders based on cust",
        "sql" : """
                SELECT orderID, totalAmmount
                FROM Orders
                WHERE custID = ?"""
        },
    2: {"title" : "List all dishes at restraunt",
        "sql" : """
                SELECT dishName, dishPrice
                FROM Dish
                WHERE restrauntID = ?"""
        },
    3: {"title" : "Total spent by customer on all orders",
        "sql" : """
                SELECT Customers.custID, custFirstName, custSecondName, SUM(totalAmmount) AS totalSpent
                FROM Orders
                JOIN Customers ON Orders.custID = Customers.custID
                GROUP BY Customers.custID"""
        },
    4: {"title" : "Count number of orders placed by customer",
        "sql" : """
                SELECT Customer.custID, COUNT(orderID) AS orderCount
                FROM Orders
                JOIN Customers ON Orders.custID = Customers.custID"""
        },
    5: {"title" : "Customers without an order",
        "sql" : """
                SELECT Customers.custID, custFirstName, custSecondName
                FROM Customers
                LEFT JOIN Orders ON Customers.custID = Orders.custID
                WHERE Orders.orderID IS NULL"""
        },
    6: {"title" : "Dishes and the restraunts that serve them",
        "sql" : """
                SELECT restrauntName, dishName
                FROM Dish
                JOIN Restraunt ON Dish.restrauntID = Restraunt.restrauntID
                ORDER BY restrauntName"""
        },
    7: {"title" : "Most popular dish by total quantity sold",
        "sql" : """
                SELECT Dish.dishID, dishName, SUM(quantity) AS totalQuantitySold
                FROM Orders
                JOIN Dish ON Orders.dishID = Dish.dishID
                GROUP BY Dish.dishID
                ORDER BY totalQuantitySold DESC
                LIMIT 1"""
        },
    8: {"title" : "Average dish price per restraunt",
        "sql" : """
                SELECT Restraunt.restrauntID, restrauntName, AVG(dishPrice) AS avgDishPrice
                FROM Dish
                JOIN Restraunt ON Dish.restrauntID = Restraunt.restrauntID
                GROUP BY Restraunt.restrauntID"""
        },
    9: {"title" : "All orders with dish names and quantities",
        "sql" : """
                SELECT orderID, dishName, quantity
                FROM Orders
                JOIN Dish ON Orders.dishID = Dish.dishID"""
        },
    10: {"title" : "Total revenue generated by each restraunt",
        "sql" : """
                SELECT Restraunt.restrauntID, restrauntName, SUM(totalAmmount) AS totalRevenue
                FROM Orders
                JOIN Dish ON Orders.dishID = Dish.dishID
                JOIN Restraunt ON Dish.restrauntID = Restraunt.restrauntID
                GROUP BY Restraunt.restrauntID"""
        },
    11: {"title" : "Customer name and email combined",
        "sql" : """
                SELECT custFirstName || ' ' || custSecondName || ' (' || custEmail || ')' AS custContact
                FROM Customers"""
        },
    12: {"title" : "Each dish ordered with calculated total cost",
        "sql" : """
                SELECT orderID, dishName, quantity, dishPrice, (dishPrice * quantity) AS calculatedTotal
                FROM Orders
                JOIN Dish ON Orders.dishID = Dish.dishID"""
        },
    13: {"title" : "Orders placed within a date range",
        "sql" : """
                SELECT orderID, custID, orderDate, totalAmmount
                FROM Orders
                WHERE orderDate BETWEEN ? AND ?"""
        },
    14: {"title" : "Top 5 highest-spending customers",
        "sql" : """
                SELECT Customers.custID, custFirstName, custSecondName, SUM(totalAmmount) AS totalSpent
                FROM Orders
                JOIN Customers ON Orders.custID = Customers.custID
                GROUP BY Customers.custID
                ORDER BY totalSpent DESC
                LIMIT 5"""
        },
    15: {"title" : "Top 3 best-selling dishes per restraunt",
        "sql" : """
                WITH ranked AS (
                SELECT Restraunt.restrauntID, restrauntName, dishName, SUM(quantity) AS totalSold,
                       ROW_NUMBER() OVER (
                           PARTITION BY Restraunt.restrauntID
                           ORDER BY SUM(quantity) DESC
                       ) AS rnk
                FROM Orders
                JOIN Dish ON Orders.dishID = Dish.dishID
                JOIN Restraunt ON Dish.restrauntID = Restraunt.restrauntID
                GROUP BY Restraunt.restrauntID, Dish.dishID
            )
            SELECT restrauntID, restrauntName, dishName, totalSold
            FROM ranked
            WHERE rnk <= 3
            ORDER BY restrauntID, totalSold DESC"""
        },
    16: {"title" : "Dishes that have never been ordered",
        "sql" : """
                SELECT Dish.dishID, dishName
                FROM Dish
                LEFT JOIN Orders ON Dish.dishID = Orders.dishID
                WHERE Orders.orderID IS NULL"""
        },
    17: {"title" : "Restraunts with no dishes listed",
        "sql" : """
                SELECT Restraunt.restrauntID, restrauntName
                FROM Restraunt
                LEFT JOIN Dish ON Restraunt.restrauntID = Dish.restrauntID
                WHERE Dish.dishID IS NULL"""
        },
    18: {"title" : "Customers who have spent above the average customer spend",
        "sql" : """
                SELECT Customers.custID, custFirstName, custSecondName, SUM(totalAmmount) AS totalSpent
            FROM Orders
            JOIN Customers ON Orders.custID = Customers.custID
            GROUP BY Customers.custID
            HAVING totalSpent > (
                SELECT AVG(custTotal) FROM (
                    SELECT SUM(totalAmmount) AS custTotal
                    FROM Orders
                    GROUP BY custID
            )"""
        },
}

def processQuery():
    selected = query_choice.get()
    if selected == 0:
        messagebox.showwarning(
            "No Query Selected",
            "Please select a query first."
        )
        return

    sql = queries[selected]["sql"]
    title = queries[selected]["title"]


    cursor.execute(sql)
    results = cursor.fetchall()

    columnNames = []
    for column in cursor.description():
        columnNames.append(column[0])

    filename = f"Query_{selected}_report.txt"

    with open(filename, "w", encoding="utf-8") as file:
        file.write(title + "\n")

        for heading in columnNames:
            file.write(f"{heading:<25}")
        
            file.write("\n")
            file.write("-" * 70 + "\n")
        
            for row in results:
                for value in row:
                    file.write(f"{str(value):<25}")
                file.write("\n")
        
        messagebox.showinfo(
            "Report created",
            f"{filename} has been successfully created."
        )

window = tk.Tk()

window.title("IDEK")
window.geometry("900x1000")

title_label = tk.Label(
    window,
    text="Orders Database Query Reports",
    font=("Arial", 18, "bold")
)

title_label.pack(pady=20)

instruction_label = tk.Label(
    window,
    text="Select a query and press Process",
    font=("Arial", 12)
)

instruction_label.pack(pady=10)

query_choice = tk.IntVar()
query_choice.set(0)

for number in queries:
    radio = tk.Radiobutton(
        window,
        text=f"Query {number}: {queries[number]['title']}",
        variable=query_choice,
        value=number,
        font=("Arial", 11),
        anchor="w"
    )

    radio.pack(
        fill="x",
        padx=80,
        pady=5
    )

process_button = tk.Button(
    window,
    text="Process",
    command=processQuery,
    font=("Arial", 12, "bold"),
    width=15
)

process_button.pack(pady=25)

close_button = tk.Button(
    window,
    text="Close",
    command=window.destroy,
    font=("Arial", 12, "bold"),
    width=15
)

close_button.pack()

window.mainloop()

conn.close()