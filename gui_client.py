import tkinter as tk
from tkinter import ttk, messagebox
import socket
import json
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

HOST = "172.16.61.94"
PORT = 4000


def receive_message(sock, buffer):
    while b"\n" not in buffer:
        chunk = sock.recv(4096)

        if not chunk:
            raise ConnectionError("Server disconnected.")

        buffer += chunk

    message, buffer = buffer.split(b"\n", 1)

    return json.loads(message.decode("utf-8")), buffer


def send_message(sock, data):
    message = json.dumps(data) + "\n"
    sock.sendall(message.encode("utf-8"))


def connect_to_server():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(30)

    try:
        client.connect((HOST, PORT))

        buffer = b""
        greeting, buffer = receive_message(client, buffer)

        if greeting.get("status") != "success":
            raise ConnectionError(
                "Server connection was unsuccessful."
            )

        client.settimeout(None)

        return client, buffer

    except Exception:
        client.close()
        raise


# Create the main window
root = tk.Tk()

root.title("Expense Tracker")
root.geometry("10000x10000")
root.minsize(900, 700)

root.configure(bg="#f4f6f9")
# Configure the appearance of Tkinter widgets
style = ttk.Style()

style.configure(
    "TEntry",
    padding=8,
    fieldbackground="white",
    foreground="#1f2937"
)

style.configure(
    "TButton",
    padding=8,
    font=("Arial", 11)
)


# Application heading
heading = tk.Label(
    root,
    text="Expense Tracker",
    font=("Arial", 24, "bold"),
    bg="#f4f6f9",
    fg="#1f2937"
)

heading.pack(pady=20)

# Connection status
status_label = tk.Label(
    root,
    text="Connecting to server...",
    font=("Arial", 11),
    bg="#f4f6f9",
    fg="#555555"
)

status_label.pack()


# Main content frame
# Container for the canvas and scrollbar
container = tk.Frame(root, bg="#f3f4f6")
container.pack(fill="both", expand=True)

# Canvas makes scrolling possible
canvas = tk.Canvas(container, bg="white", highlightthickness=0)
canvas.pack(side="left", fill="both", expand=True)

# Vertical scrollbar
scrollbar = ttk.Scrollbar(
    container,
    orient="vertical",
    command=canvas.yview
)
scrollbar.pack(side="right", fill="y")

# Connect scrollbar to canvas
canvas.configure(yscrollcommand=scrollbar.set)

# Frame that holds all dashboard components
main_frame = tk.Frame(canvas, bg="white")

# Put main_frame inside the canvas
canvas_window = canvas.create_window(
    (0, 0),
    window=main_frame,
    anchor="nw"
)
def update_scroll_region(event=None):
    canvas.configure(scrollregion=canvas.bbox("all"))

main_frame.bind("<Configure>", update_scroll_region)
def update_canvas_width(event):
    canvas.itemconfigure(canvas_window, width=event.width)

canvas.bind("<Configure>", update_canvas_width)


# Dashboard heading
dashboard_heading = tk.Label(
    main_frame,
    text="Welcome to your Expense Dashboard",
    font=("Arial", 16, "bold"),
    bg="white",
    fg="#1f2937"
)

dashboard_heading.pack(pady=15)

# --------------------------------
# Total Expense Summary Card
# --------------------------------

summary_frame = tk.Frame(
    main_frame,
    bg="#dbeafe",
    padx=25,
    pady=15
)

summary_frame.pack(fill="x", padx=20, pady=10)

tk.Label(
    summary_frame,
    text="TOTAL EXPENSES",
    font=("Arial", 12, "bold"),
    bg="#dbeafe",
    fg="#1e40af"
).pack()

total_expense_label = tk.Label(
    summary_frame,
    text="Loading...",
    font=("Arial", 22, "bold"),
    bg="#dbeafe",
    fg="#1d4ed8"
)

total_expense_label.pack(pady=5)

# Transaction count
transaction_count_label = tk.Label(
    summary_frame,
    text="Transactions: Loading...",
    font=("Arial", 12),
    bg="#dbeafe",
    fg="#1e40af"
)

transaction_count_label.pack(pady=5)

# --------------------------------
# Add Expense Form
# --------------------------------

form_frame = tk.Frame(
    main_frame,
    bg="white"
)

form_frame.pack(pady=10)


# Amount label
amount_label = tk.Label(
    form_frame,
    text="Amount (₹):",
    font=("Arial", 11),
    bg="white",
    fg="#1f2937"
)

amount_label.grid(row=0, column=0, sticky="w", pady=8)


amount_entry = tk.Entry(
    form_frame,
    width=35,
    font=("Arial", 12),
    bg="white",
    fg="#1f2937",
    insertbackground="#1f2937",
    relief="solid",
    bd=1
)
amount_entry.grid(row=0, column=1, pady=8, padx=10)


# Category label
category_label = tk.Label(
    form_frame,
    text="Category:",
    font=("Arial", 11),
    bg="white",
    fg="#1f2937"
)

category_label.grid(row=1, column=0, sticky="w", pady=8)


# Category input
category_entry = tk.Entry(
    form_frame,
    width=35,
    font=("Arial", 12),
    bg="white",
    fg="#1f2937",
    insertbackground="#1f2937",
    relief="solid",
    bd=1
)

category_entry.grid(row=1, column=1, pady=8, padx=10)


# Description label
description_label = tk.Label(
    form_frame,
    text="Description:",
    font=("Arial", 11),
    bg="white",
    fg="#1f2937"
)

description_label.grid(row=2, column=0, sticky="w", pady=8)


# Description input
description_entry = tk.Entry(
    form_frame,
    width=35,
    font=("Arial", 12),
    bg="white",
    fg="#1f2937",
    insertbackground="#1f2937",
    relief="solid",
    bd=1
)

description_entry.grid(row=2, column=1, pady=8, padx=10)


# --------------------------------
# Add Expense Function
# --------------------------------

def add_expense():
    if client is None:
        messagebox.showerror(
            "Connection Error",
            "Not connected to the server."
        )
        return

    try:
        amount = float(amount_entry.get().strip())

        if amount <= 0:
            messagebox.showerror(
                "Invalid Amount",
                "Amount must be greater than zero."
            )
            return

        category = category_entry.get().strip()
        description = description_entry.get().strip()

        if not category:
            messagebox.showerror(
                "Invalid Category",
                "Category cannot be empty."
            )
            return

        request = {
            "action": "add_expense",
            "amount": amount,
            "category": category,
            "description": description
        }

        send_message(client, request)

        response, new_buffer = receive_message(
            client,
            global_buffer[0]
        )

        # Preserve any remaining received bytes.
        global_buffer[0] = new_buffer

        if response.get("status") == "success":
            expense_id = response.get("expense_id")

            messagebox.showinfo(
                "Success",
                f"Expense added successfully!\n"
                f"Expense ID: {expense_id}"

            )

            # Clear the input fields.
            amount_entry.delete(0, tk.END)
            category_entry.delete(0, tk.END)
            description_entry.delete(0, tk.END)

            load_expenses()

        else:
            messagebox.showerror(
                "Error",
                response.get(
                    "message",
                    "Unable to add expense."
                )
            )

    except ValueError:
        messagebox.showerror(
            "Invalid Amount",
            "Please enter a valid numeric amount."
        )

    except (OSError, ConnectionError, json.JSONDecodeError) as e:
        messagebox.showerror(
            "Communication Error",
            str(e)
        )



# Add Expense button
add_button = ttk.Button(
    main_frame,
    text="Add Expense",
    command=add_expense
)

add_button.pack(pady=15)

# --------------------------------
# Expense Records Table
# --------------------------------

table_heading = tk.Label(
    main_frame,
    text="Expense Records",
    font=("Arial", 16, "bold"),
    bg="white",
    fg="#1f2937"
)

table_heading.pack(pady=(20, 10))


# Create a frame for the table
table_frame = tk.Frame(
    main_frame,
    bg="white"
)

table_frame.pack(fill="both", expand=True)


# Create the table
columns = (
    "id",
    "amount",
    "category",
    "description"
)

expense_table = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings",
    height=8
)


# Define column headings
expense_table.heading("id", text="ID")
expense_table.heading("amount", text="Amount (₹)")
expense_table.heading("category", text="Category")
expense_table.heading("description", text="Description")


# Define column widths
expense_table.column("id", width=60, anchor="center")
expense_table.column("amount", width=120, anchor="center")
expense_table.column("category", width=150, anchor="center")
expense_table.column("description", width=300, anchor="w")


# Add vertical scrollbar
scrollbar = ttk.Scrollbar(
    table_frame,
    orient="vertical",
    command=expense_table.yview
)

expense_table.configure(
    yscrollcommand=scrollbar.set
)


# Display the table and scrollbar
expense_table.pack(
    side="left",
    fill="both",
    expand=True
)

scrollbar.pack(
    side="right",
    fill="y"
)

# --------------------------------
# Category Spending Chart
# --------------------------------

chart_frame = tk.Frame(
    main_frame,
    bg="white"
)

chart_frame.pack(
    fill="x",
    expand=True,
    pady=20
)

def load_expenses():
    if client is None:
        messagebox.showerror(
            "Connection Error",
            "Not connected to the server."
        )
        return

    try:
        request = {
            "action": "view_expenses"
        }

        send_message(client, request)

        response, new_buffer = receive_message(
            client,
            global_buffer[0]
        )

        global_buffer[0] = new_buffer

        if response.get("status") != "success":
            messagebox.showerror(
                "Error",
                response.get(
                    "message",
                    "Unable to retrieve expenses."
                )
            )
            return

        # Remove old rows
        for row in expense_table.get_children():
            expense_table.delete(row)

        # Insert updated rows
        expenses = response.get("expenses", [])

        for expense in expenses:
            expense_table.insert(
                "",
                "end",
                values=(
                    expense["id"],
                    f"{expense['amount']:.2f}",
                    expense["category"],
                    expense.get("description") or ""
                )
            )
            load_expense_summary()
            load_category_chart()

    except (OSError, ConnectionError, json.JSONDecodeError) as e:
        messagebox.showerror(
            "Communication Error",
            str(e)
        )

# --------------------------------
# Load Expense Summary
# --------------------------------

def load_expense_summary():
    if client is None:
        total_expense_label.config(
            text="Connection unavailable"
        )
        return

    try:
        request = {
            "action": "expense_summary"
        }

        send_message(client, request)

        response, new_buffer = receive_message(
            client,
            global_buffer[0]
        )

        global_buffer[0] = new_buffer

        if response.get("status") == "success":
            summary = response["summary"]

            total = summary["total_amount"]
            transactions = summary["total_transactions"]

            total_expense_label.config(
                text=f"₹{total:,.2f}"
            )

            transaction_count_label.config(
                text=f"Total Transactions: {transactions}"
            )

        else:
            total_expense_label.config(
                text="Unable to load"
            )

    except (
        OSError,
        ConnectionError,
        json.JSONDecodeError,
        KeyError,
        TypeError
    ) as e:
        print("Error loading expense summary:", e)

        total_expense_label.config(
            text="Error loading total"
        )

# --------------------------------
# Load Category Spending Chart
# --------------------------------

def load_category_chart():
    if client is None:
        return

    try:
        request = {
            "action": "category_summary"
        }

        send_message(client, request)

        response, new_buffer = receive_message(
            client,
            global_buffer[0]
        )

        global_buffer[0] = new_buffer

        if response.get("status") != "success":
            messagebox.showerror(
                "Chart Error",
                response.get(
                    "message",
                    "Unable to load category summary."
                )
            )
            return

        categories = response.get("categories", [])

        # Remove the previous chart
        for widget in chart_frame.winfo_children():
            widget.destroy()

        # Handle an empty database
        if not categories:
            tk.Label(
                chart_frame,
                text="No expense data available for the chart.",
                font=("Arial", 12),
                bg="white",
                fg="#555555"
            ).pack(pady=20)

            return

        # Extract category names and spending amounts
        category_names = [
            item["category"] for item in categories
        ]

        amounts = [
            float(item["total_amount"]) for item in categories
        ]

        # Create the figure
        figure = Figure(
            figsize=(7, 4),
            dpi=100
        )

        axis = figure.add_subplot(111)

        axis.bar(category_names, amounts)

        axis.set_title("Spending by Category")
        axis.set_xlabel("Category")
        axis.set_ylabel("Amount (₹)")

        axis.tick_params(
            axis="x",
            labelrotation=30
        )

        figure.tight_layout()

        # Embed the chart in Tkinter
        canvas = FigureCanvasTkAgg(
            figure,
            master=chart_frame
        )

        canvas.draw()

        canvas.get_tk_widget().pack(
            fill="both",
            expand=True
        )

    except (
        OSError,
        ConnectionError,
        json.JSONDecodeError,
        KeyError,
        TypeError,
        ValueError
    ) as e:
        print("Error loading category chart:", e)

        messagebox.showerror(
            "Chart Error",
            str(e)
        )

# Refresh Expenses button
refresh_button = ttk.Button(
    main_frame,
    text="Refresh Expenses",
    command=load_expenses
)

refresh_button.pack(pady=10)

def delete_selected_expense():
    if client is None:
        messagebox.showerror(
            "Connection Error",
            "Not connected to the server."
        )
        return

    # Get the selected row
    selected_item = expense_table.selection()

    if not selected_item:
        messagebox.showwarning(
            "No Selection",
            "Please select an expense to delete."
        )
        return

    # Get the values from the selected row
    values = expense_table.item(selected_item[0], "values")

    expense_id = int(values[0])

    # Confirm deletion
    confirm = messagebox.askyesno(
        "Confirm Deletion",
        f"Are you sure you want to delete expense ID {expense_id}?"
    )

    if not confirm:
        return

    try:
        request = {
            "action": "delete_expense",
            "expense_id": expense_id
        }

        send_message(client, request)

        response, new_buffer = receive_message(
            client,
            global_buffer[0]
        )

        global_buffer[0] = new_buffer

        if response.get("status") == "success":
            messagebox.showinfo(
                "Success",
                response.get(
                    "message",
                    "Expense deleted successfully."
                )
            )

            # Refresh the table
            load_expenses()

        else:
            messagebox.showerror(
                "Error",
                response.get(
                    "message",
                    "Unable to delete expense."
                )
            )

    except (OSError, ConnectionError, json.JSONDecodeError) as e:
        messagebox.showerror(
            "Communication Error",
            str(e)
        )

def edit_selected_expense():
    if client is None:
        messagebox.showerror(
            "Connection Error",
            "Not connected to the server."
        )
        return

    # Get the selected row
    selected_item = expense_table.selection()

    if not selected_item:
        messagebox.showwarning(
            "No Selection",
            "Please select an expense to edit."
        )
        return

    # Extract the selected expense's details
    values = expense_table.item(selected_item[0], "values")

    expense_id = int(values[0])
    amount = values[1]
    category = values[2]
    description = values[3]

    # Create the editing window
    edit_window = tk.Toplevel(root)
    edit_window.title("Edit Expense")
    edit_window.geometry("400x350")
    edit_window.resizable(False, False)

    # Heading
    tk.Label(
        edit_window,
        text=f"Edit Expense #{expense_id}",
        font=("Arial", 16, "bold")
    ).pack(pady=15)

    # Amount
    tk.Label(edit_window, text="Amount").pack(pady=(5, 0))

    edit_amount = tk.Entry(edit_window, width=35)
    edit_amount.pack(pady=5)
    edit_amount.insert(0, amount)

    # Category
    tk.Label(edit_window, text="Category").pack(pady=(5, 0))

    edit_category = tk.Entry(edit_window, width=35)
    edit_category.pack(pady=5)
    edit_category.insert(0, category)

    # Description
    tk.Label(edit_window, text="Description").pack(pady=(5, 0))

    edit_description = tk.Entry(edit_window, width=35)
    edit_description.pack(pady=5)
    edit_description.insert(0, description)

    # Save changes
    def save_changes():
        new_amount = edit_amount.get().strip()
        new_category = edit_category.get().strip()
        new_description = edit_description.get().strip()

        # Validate input
        try:
            new_amount = float(new_amount)

            if new_amount <= 0:
                raise ValueError

        except ValueError:
            messagebox.showerror(
                "Invalid Amount",
                "Please enter an amount greater than zero.",
                parent=edit_window
            )
            return

        if not new_category:
            messagebox.showerror(
                "Invalid Category",
                "Category cannot be empty.",
                parent=edit_window
            )
            return

        try:
            request = {
                "action": "update_expense",
                "expense_id": expense_id,
                "amount": new_amount,
                "category": new_category,
                "description": new_description
            }

            send_message(client, request)

            response, new_buffer = receive_message(
                client,
                global_buffer[0]
            )

            global_buffer[0] = new_buffer

            if response.get("status") == "success":
                messagebox.showinfo(
                    "Success",
                    "Expense updated successfully!",
                    parent=edit_window
                )

                edit_window.destroy()
                load_expenses()

            else:
                messagebox.showerror(
                    "Update Failed",
                    response.get(
                        "message",
                        "Unable to update expense."
                    ),
                    parent=edit_window
                )

        except (OSError, ConnectionError, json.JSONDecodeError) as e:
            messagebox.showerror(
                "Communication Error",
                str(e),
                parent=edit_window
            )

    tk.Button(
        edit_window,
        text="Save Changes",
        command=save_changes,
        bg="#2563eb",
        fg="white",
        font=("Arial", 11, "bold"),
        padx=15,
        pady=5
    ).pack(pady=15)

# Frame for Edit and Delete buttons
action_frame = tk.Frame(main_frame, bg="white")
action_frame.pack(pady=10)

edit_button = tk.Button(
    action_frame,
    text="Edit Selected Expense",
    command=edit_selected_expense
)
edit_button.pack(side="left", padx=10)

delete_button = tk.Button(
    action_frame,
    text="Delete Selected Expense",
    command=delete_selected_expense
)
delete_button.pack(side="left", padx=10)

# Connection variables
client = None
buffer = b""
global_buffer = [b""]

try:
    client, buffer = connect_to_server()

    global_buffer[0] = buffer

    status_label.config(
        text="Connected to Expense Tracker server",
        fg="green"
    )

except (OSError, ConnectionError, json.JSONDecodeError) as e:
    status_label.config(
        text="Unable to connect to server",
        fg="red"
    )

    messagebox.showerror(
        "Connection Error",
        f"Could not connect to the server.\n\n{e}"
    )


def close_application():
    global client

    if client is not None:
        try:
            send_message(client, {"action": "exit"})
            receive_message(client, buffer)
        except Exception:
            pass
        finally:
            client.close()
            client = None

    root.destroy()


root.protocol("WM_DELETE_WINDOW", close_application)

root.mainloop()