import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()
# Connect to MySQL
con = mysql.connector.connect(
    host="localhost",
    user="root",
    password=os.getenv("DB_PASSWORD")
)

cur = con.cursor()

# Create database
cur.execute("CREATE DATABASE IF NOT EXISTS expense_tracker")

# Select database
cur.execute("USE expense_tracker")

# Create table
cur.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INT AUTO_INCREMENT PRIMARY KEY,
        amount DECIMAL(10, 2),
        category VARCHAR(100),
        description VARCHAR(255)
    )
""")
print("Database and table created successfully!")
# Close connection
cur.close()
con.close()

def add_expense(amount, category, description):
    con = mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("DB_PASSWORD"),
        database="expense_tracker"
    )
    cur = con.cursor()
    query = """
    INSERT INTO expenses (amount, category, description)
    VALUES (%s, %s, %s)
    """
    values = (amount, category, description)
    cur.execute(query, values)
    con.commit()
    expense_id = cur.lastrowid
    cur.close()
    con.close()
    return expense_id

def get_expenses():
    con = mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("DB_PASSWORD"),
        database="expense_tracker"
    )
    cur = con.cursor()

    cur.execute("""
        SELECT id, amount, category, description
        FROM expenses
        ORDER BY id DESC
    """)
    expenses = cur.fetchall()
    cur.close()
    con.close()
    result = []

    for expense in expenses:
        result.append({
            "id": expense[0],
            "amount": float(expense[1]),
            "category": expense[2],
            "description": expense[3]
        })
    return result

def delete_expense(expense_id):
    con = mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("DB_PASSWORD"),
        database="expense_tracker"
    )

    cur = con.cursor()

    query = "DELETE FROM expenses WHERE id = %s"

    cur.execute(query, (expense_id,))
    con.commit()

    deleted = cur.rowcount > 0

    cur.close()
    con.close()

    return deleted

def update_expense(expense_id, amount, category, description):
    con = mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("DB_PASSWORD"),
        database="expense_tracker"
    )

    cur = con.cursor()

    query = """
    UPDATE expenses
    SET amount = %s,
        category = %s,
        description = %s
    WHERE id = %s
    """

    cur.execute(
        query,
        (amount, category, description, expense_id)
    )

    con.commit()

    updated = cur.rowcount > 0

    cur.close()
    con.close()

    return updated

def get_expense_summary():
    con = mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("DB_PASSWORD"),
        database="expense_tracker"
    )

    cur = con.cursor()

    query = """
    SELECT
        COUNT(*),
        COALESCE(SUM(amount), 0),
        COALESCE(AVG(amount), 0)
    FROM expenses
    """

    cur.execute(query)

    result = cur.fetchone()

    summary = {
        "total_transactions": result[0],
        "total_amount": float(result[1]),
        "average_amount": float(result[2])
    }

    cur.close()
    con.close()

    return summary

def get_category_summary():
    con = mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("DB_PASSWORD"),
        database="expense_tracker"
    )

    cur = con.cursor()

    query = """
    SELECT category, SUM(amount)
    FROM expenses
    GROUP BY category
    ORDER BY SUM(amount) DESC
    """

    cur.execute(query)

    rows = cur.fetchall()

    result = []

    for row in rows:
        result.append({
            "category": row[0],
            "total_amount": float(row[1])
        })

    cur.close()
    con.close()

    return result

