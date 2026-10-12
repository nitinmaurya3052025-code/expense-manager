import mysql.connector

con = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Nitin123",
    database="expense_tracker"
)

cur = con.cursor()

amount = float(input("Enter amount: "))
category = input("Enter category: ")
description = input("Enter description: ")

query = """
INSERT INTO expenses (amount, category, description)
VALUES (%s, %s, %s)
"""

values = (amount, category, description)

cur.execute(query, values)

con.commit()

print("Expense added successfully!")

cur.close()
con.close()