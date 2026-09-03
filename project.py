import sqlite3
import os
import csv
import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog

DB_Name = "delivery_recording_system.db"

Delivery_Fee = 5.95

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

cursor.execute("""
    UPDATE Orders
    SET totalAmmount = (
        SELECT Dish.dishPrice * Orders.quantity + ?
        FROM Dish
        WHERE Dish.dishID = Orders.dishID
    )
    WHERE dishID IN (SELECT dishID FROM Dish)
""", (Delivery_Fee,))

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
                WHERE Customers.custID = ?
                GROUP BY Customers.custID"""
        },
    4: {"title" : "Count number of orders placed by customer",
        "sql" : """
                SELECT Customers.custID, COUNT(orderID) AS orderCount
                FROM Orders
                JOIN Customers ON Orders.custID = Customers.custID
                WHERE Customers.custID = ?
                GROUP BY Customers.custID"""
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
                WHERE restrauntID = ?
                ORDER BY restrauntID"""
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
                    GROUP BY custID)
            )"""
        },
}

def getCustID(prompt="Enter Customer ID:"):
    custID = simpledialog.askinteger("Customer ID", prompt)
    if custID is None:
        return None
    return (custID,)

def getRestrauntID():
    restrauntID = simpledialog.askinteger("Restraunt ID", "Enter Restraunt ID:")
    if restrauntID is None:
        return None
    return (restrauntID,)

def getRestrauntID2():
    restrauntID = simpledialog.askstring(
        "Restraunt ID",
        "Enter Restraunt ID:"
    )
    if not restrauntID:
        return None
    return (f"%{restrauntID}%",)

def getDateRange():
    startDate = simpledialog.askstring("Start Date", "Enter start date (YYYY-MM-DD):")
    if not startDate:
        return None
    endDate = simpledialog.askstring("End Date", "Enter end date (YYYY-MM-DD):")
    if not endDate:
        return None
    return (startDate, endDate)

inputHandlers = {
    1: lambda: getCustID(),
    2: lambda: getRestrauntID(),
    3: lambda: getCustID(),
    4: lambda: getCustID(),
    6: lambda: getRestrauntID2(),
    13: lambda: getDateRange(),
}

def add_new_order():
    cust_id = simpledialog.askinteger("New Order", "Enter Customer ID:")
    if not cust_id:
        return
    dish_id = simpledialog.askinteger("New Order", "Enter Dish ID:")
    if not dish_id:
        return
    order_date = simpledialog.askstring(
        "New Order", "Enter Order Date (YYYY-MM-DD):"
    )
    if not order_date:
        return
    quantity = simpledialog.askinteger("New Order", "Enter Quantity:")
    if not quantity:
        return

    # Check dish price
    cursor.execute("SELECT dishPrice FROM Dish WHERE dishID = ?", (dish_id,))
    result = cursor.fetchone()

    if not result:
        messagebox.showerror("Error", f"Dish ID {dish_id} does not exist.")
        return

    dish_price = result[0]
    delivery_fee = Delivery_Fee
    total_amount = (quantity * dish_price) + delivery_fee

    sql = """
        INSERT INTO Orders (custID, dishID, orderDate, quantity, totalAmmount)
        VALUES (?, ?, ?, ?, ?)
    """
    cursor.execute(sql, (cust_id, dish_id, order_date, quantity, total_amount))
    conn.commit()
    messagebox.showinfo("Success", "Order added successfully!")

def add_customer():
    first = simpledialog.askstring("New Customer", "First Name:")
    if not first:
        return
    last = simpledialog.askstring("New Customer", "Last Name:")
    if not last:
        return
    email = simpledialog.askstring("New Customer", "Email:")
    if not email:
        return
    address = simpledialog.askstring("New Customer", "Address:")
    if not address:
        return
    suburb = simpledialog.askstring("New Customer", "Suburb:")
    if not suburb:
        return
    postcode = simpledialog.askinteger("New Customer", "Postcode:")
    if not postcode:
        return
    phone = simpledialog.askstring("New Customer", "Phone Number:")
    if not phone:
        return

    sql = """
        INSERT INTO Customers (custFirstName, custSecondName, custEmail, custAddress, suburb, PostCode, custPhoneNo)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    cursor.execute(sql, (first, last, email, address, suburb, postcode, phone))
    conn.commit()
    messagebox.showinfo("Success", "Customer added successfully!")

def add_restraunt():
    name = simpledialog.askstring("New Restraunt", "Restraunt Name:")
    if not name:
        return
    address = simpledialog.askstring("New Restraunt", "Address:")
    if not address:
        return
    phone = simpledialog.askstring("New Restraunt", "Phone Number:")
    if not phone:
        return

    sql = """
        INSERT INTO Restraunt (restrauntName, restrauntAddress, restrauntPhoneNo)
        VALUES (?, ?, ?)
    """
    cursor.execute(sql, (name, address, phone))
    conn.commit()
    messagebox.showinfo("Success", "Restraunt added successfully!")

def add_dish():
    rest_id = simpledialog.askinteger("New Dish", "Restraunt ID:")
    if not rest_id:
        return
    name = simpledialog.askstring("New Dish", "Dish Name:")
    if not name:
        return
    price = simpledialog.askfloat("New Dish", "Dish Price ($):")
    if price is None:
        return

    sql = """
        INSERT INTO Dish (restrauntID, dishName, dishPrice)
        VALUES (?, ?, ?)
    """
    cursor.execute(sql, (rest_id, name, price))
    conn.commit()
    messagebox.showinfo("Success", "Dish added successfully!")

def update_order():
    order_id = simpledialog.askinteger("Update Order", "Enter Order ID to update:")
    if not order_id:
        return
 
    cursor.execute("SELECT * FROM Orders WHERE orderID = ?", (order_id,))
    row = cursor.fetchone()
    if not row:
        messagebox.showerror("Error", f"Order ID {order_id} does not exist.")
        return
 
    cust_id = simpledialog.askinteger("Update Order", "Customer ID:", initialvalue=row[1])
    if not cust_id:
        return
    dish_id = simpledialog.askinteger("Update Order", "Dish ID:", initialvalue=row[2])
    if not dish_id:
        return
    order_date = simpledialog.askstring(
        "Update Order", "Order Date (YYYY-MM-DD):", initialvalue=row[3]
    )
    if not order_date:
        return
    quantity = simpledialog.askinteger("Update Order", "Quantity:", initialvalue=row[4])
    if not quantity:
        return
 
    cursor.execute("SELECT dishPrice FROM Dish WHERE dishID = ?", (dish_id,))
    result = cursor.fetchone()
    if not result:
        messagebox.showerror("Error", f"Dish ID {dish_id} does not exist.")
        return
 
    dish_price = result[0]
    delivery_fee = Delivery_Fee
    total_amount = (quantity * dish_price) + delivery_fee
 
    sql = """
        UPDATE Orders
        SET custID = ?, dishID = ?, orderDate = ?, quantity = ?, totalAmmount = ?
        WHERE orderID = ?
    """
    cursor.execute(sql, (cust_id, dish_id, order_date, quantity, total_amount, order_id))
    conn.commit()
    messagebox.showinfo("Success", "Order updated successfully!")

def update_customer():
    cust_id = simpledialog.askinteger("Update Customer", "Enter Customer ID to update:")
    if not cust_id:
        return
 
    cursor.execute("SELECT * FROM Customers WHERE custID = ?", (cust_id,))
    row = cursor.fetchone()
    if not row:
        messagebox.showerror("Error", f"Customer ID {cust_id} does not exist.")
        return
 
    first = simpledialog.askstring("Update Customer", "First Name:", initialvalue=row[1])
    if not first:
        return
    last = simpledialog.askstring("Update Customer", "Last Name:", initialvalue=row[2])
    if not last:
        return
    email = simpledialog.askstring("Update Customer", "Email:", initialvalue=row[3])
    if not email:
        return
    address = simpledialog.askstring("Update Customer", "Address:", initialvalue=row[4])
    if not address:
        return
    suburb = simpledialog.askstring("Update Customer", "Suburb:", initialvalue=row[5])
    if not suburb:
        return
    postcode = simpledialog.askinteger("Update Customer", "Postcode:", initialvalue=row[6])
    if postcode is None:
        return
    phone = simpledialog.askstring("Update Customer", "Phone Number:", initialvalue=row[7])
    if not phone:
        return
 
    sql = """
        UPDATE Customers
        SET custFirstName = ?, custSecondName = ?, custEmail = ?, custAddress = ?,
            suburb = ?, PostCode = ?, custPhoneNo = ?
        WHERE custID = ?
    """
    cursor.execute(sql, (first, last, email, address, suburb, postcode, phone, cust_id))
    conn.commit()
    messagebox.showinfo("Success", "Customer updated successfully!")

def update_restraunt():
    rest_id = simpledialog.askinteger("Update Restraunt", "Enter Restraunt ID to update:")
    if not rest_id:
        return
 
    cursor.execute("SELECT * FROM Restraunt WHERE restrauntID = ?", (rest_id,))
    row = cursor.fetchone()
    if not row:
        messagebox.showerror("Error", f"Restraunt ID {rest_id} does not exist.")
        return
 
    name = simpledialog.askstring("Update Restraunt", "Restraunt Name:", initialvalue=row[1])
    if not name:
        return
    address = simpledialog.askstring("Update Restraunt", "Address:", initialvalue=row[2])
    if not address:
        return
    phone = simpledialog.askstring("Update Restraunt", "Phone Number:", initialvalue=row[3])
    if not phone:
        return
 
    sql = """
        UPDATE Restraunt
        SET restrauntName = ?, restrauntAddress = ?, restrauntPhoneNo = ?
        WHERE restrauntID = ?
    """
    cursor.execute(sql, (name, address, phone, rest_id))
    conn.commit()
    messagebox.showinfo("Success", "Restraunt updated successfully!")

def update_dish():
    dish_id = simpledialog.askinteger("Update Dish", "Enter Dish ID to update:")
    if not dish_id:
        return
 
    cursor.execute("SELECT * FROM Dish WHERE dishID = ?", (dish_id,))
    row = cursor.fetchone()
    if not row:
        messagebox.showerror("Error", f"Dish ID {dish_id} does not exist.")
        return
 
    rest_id = simpledialog.askinteger("Update Dish", "Restraunt ID:", initialvalue=row[1])
    if not rest_id:
        return
    name = simpledialog.askstring("Update Dish", "Dish Name:", initialvalue=row[2])
    if not name:
        return
    price = simpledialog.askfloat("Update Dish", "Dish Price ($):", initialvalue=row[3])
    if price is None:
        return
 
    sql = """
        UPDATE Dish
        SET restrauntID = ?, dishName = ?, dishPrice = ?
        WHERE dishID = ?
    """
    cursor.execute(sql, (rest_id, name, price, dish_id))
    conn.commit()
    messagebox.showinfo("Success", "Dish updated successfully!")

def delete_order():
    order_id = simpledialog.askinteger("Delete Order", "Enter Order ID to delete:")
    if not order_id:
        return

    confirm = messagebox.askyesno(
        "Confirm Delete",
        f"Are you sure you want to delete Order ID {order_id}? This cannot be undone."
    )
    if not confirm:
        return

    cursor.execute("DELETE FROM Orders WHERE orderID = ?", (order_id,))
    conn.commit()
    if cursor.rowcount == 0:
        messagebox.showerror("Error", f"Order ID {order_id} does not exist.")
    else:
        messagebox.showinfo("Success", "Order deleted successfully!")

def delete_customer():
    cust_id = simpledialog.askinteger("Delete Customer", "Enter Customer ID to delete:")
    if not cust_id:
        return

    confirm = messagebox.askyesno(
        "Confirm Delete",
        f"Are you sure you want to delete Customer ID {cust_id}?\n"
        "This will fail if the customer still has existing orders."
    )
    if not confirm:
        return

    try:
        cursor.execute("DELETE FROM Customers WHERE custID = ?", (cust_id,))
        conn.commit()
        if cursor.rowcount == 0:
            messagebox.showerror("Error", f"Customer ID {cust_id} does not exist.")
        else:
            messagebox.showinfo("Success", "Customer deleted successfully!")
    except sqlite3.IntegrityError:
        messagebox.showerror(
            "Error",
            "Cannot delete this customer because they still have orders on record."
        )

def delete_restraunt():
    rest_id = simpledialog.askinteger("Delete Restraunt", "Enter Restraunt ID to delete:")
    if not rest_id:
        return

    confirm = messagebox.askyesno(
        "Confirm Delete",
        f"Are you sure you want to delete Restraunt ID {rest_id}?\n"
        "This will fail if the restraunt still has dishes on record."
    )
    if not confirm:
        return

    try:
        cursor.execute("DELETE FROM Restraunt WHERE restrauntID = ?", (rest_id,))
        conn.commit()
        if cursor.rowcount == 0:
            messagebox.showerror("Error", f"Restraunt ID {rest_id} does not exist.")
        else:
            messagebox.showinfo("Success", "Restraunt deleted successfully!")
    except sqlite3.IntegrityError:
        messagebox.showerror(
            "Error",
            "Cannot delete this restraunt because it still has dishes on record."
        )

def delete_dish():
    dish_id = simpledialog.askinteger("Delete Dish", "Enter Dish ID to delete:")
    if not dish_id:
        return

    confirm = messagebox.askyesno(
        "Confirm Delete",
        f"Are you sure you want to delete Dish ID {dish_id}?\n"
        "This will fail if the dish still appears on existing orders."
    )
    if not confirm:
        return

    try:
        cursor.execute("DELETE FROM Dish WHERE dishID = ?", (dish_id,))
        conn.commit()
        if cursor.rowcount == 0:
            messagebox.showerror("Error", f"Dish ID {dish_id} does not exist.")
        else:
            messagebox.showinfo("Success", "Dish deleted successfully!")
    except sqlite3.IntegrityError:
        messagebox.showerror(
            "Error",
            "Cannot delete this dish because it still appears on existing orders."
        )

def export_table_to_csv(table_name, columns, filename):
    cursor.execute(f"SELECT {', '.join(columns)} FROM {table_name}")
    rows = cursor.fetchall()
 
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(columns)
        writer.writerows(rows)
 
def export_to_csv():
    export_table_to_csv(
        "Customers",
        ["custID", "custFirstName", "custSecondName", "custEmail",
         "custAddress", "suburb", "PostCode", "custPhoneNo"],
        "customers.csv"
    )
    export_table_to_csv(
        "Orders",
        ["orderID", "custID", "dishID", "orderDate", "quantity", "totalAmmount"],
        "orders.csv"
    )
    export_table_to_csv(
        "Restraunt",
        ["restrauntID", "restrauntName", "restrauntAddress", "restrauntPhoneNo"],
        "restraunt.csv"
    )
    export_table_to_csv(
        "Dish",
        ["dishID", "restrauntID", "dishName", "dishPrice"],
        "dish.csv"
    )
 
def export_and_close():
    try:
        export_to_csv()
    except Exception as e:
        messagebox.showerror("Export Error", f"Could not export to CSV:\n{e}")
        return
    window.destroy()

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


    params = ()
    if selected in inputHandlers:
        params = inputHandlers[selected]()
        if params is None:
            return

    cursor.execute(sql, params)
    results = cursor.fetchall()

    columnNames = []
    for column in cursor.description:
        columnNames.append(column[0])

    filename = f"Query_{selected}_report.txt"

    with open(filename, "w", encoding="utf-8") as file:
        file.write(title + "\n")

        for heading in columnNames:
            file.write(f"{heading:<25}")

        file.write("\n")
        file.write("-" * (25 * len(columnNames)) + "\n")

        for row in results:
            for value in row:
                file.write(f"{str(value):<25}")
            file.write("\n")
        
        messagebox.showinfo(
            "Report created",
            f"{filename} has been successfully created."
        )

window = tk.Tk()

window.title("Query Selection")
window.geometry("900x1300")

title_label = tk.Label(
    window,
    text="Orders Database Query Reports",
    font=("Arial", 18, "bold")
)

title_label.pack(pady=20)

crud_label = tk.Label(
    window,
    text="Manage Records",
    font=("Arial", 14, "bold")
)
crud_label.pack(pady=(0, 5))
 
crud_frame = tk.Frame(window)
crud_frame.pack(pady=10)

crud_entities = [
    ("Order", add_new_order, update_order, delete_order),
    ("Customer", add_customer, update_customer, delete_customer),
    ("Restraunt", add_restraunt, update_restraunt, delete_restraunt),
    ("Dish", add_dish, update_dish, delete_dish),
]
 

tk.Label(crud_frame, text="", width=12).grid(row=0, column=0)
tk.Label(crud_frame, text="Add", font=("Arial", 10, "bold")).grid(row=0, column=1, padx=10)
tk.Label(crud_frame, text="Update", font=("Arial", 10, "bold")).grid(row=0, column=2, padx=10)
tk.Label(crud_frame, text="Delete", font=("Arial", 10, "bold")).grid(row=0, column=3, padx=10)
 
for i, (entity_name, add_fn, update_fn, delete_fn) in enumerate(crud_entities, start=1):
    tk.Label(crud_frame, text=entity_name, font=("Arial", 11)).grid(
        row=i, column=0, sticky="w", padx=10, pady=5
    )
    tk.Button(crud_frame, text="Add", width=12, command=add_fn).grid(
        row=i, column=1, padx=10, pady=5
    )
    tk.Button(crud_frame, text="Update", width=12, command=update_fn).grid(
        row=i, column=2, padx=10, pady=5
    )
    tk.Button(crud_frame, text="Delete", width=12, command=delete_fn, fg="red").grid(
        row=i, column=3, padx=10, pady=5
    )

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
    command=export_and_close,
    font=("Arial", 12, "bold"),
    width=15
)

close_button.pack()

window.mainloop()

conn.close()