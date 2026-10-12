import socket
import threading
import json
from database import (add_expense, get_expenses, delete_expense, update_expense,get_expense_summary, get_category_summary)

HOST = "0.0.0.0"
PORT = 4000


def receive_message(conn, buffer):
    while b"\n" not in buffer:
        chunk = conn.recv(4096)

        if not chunk:
            return None, buffer

        buffer += chunk

    message, buffer = buffer.split(b"\n", 1)

    return message, buffer


def send_message(conn, data):
    message = json.dumps(data) + "\n"
    conn.sendall(message.encode("utf-8"))


def handle_client(conn, address):
    print(f"Connected by {address}")

    buffer = b""

    try:
        send_message(conn, {
            "status": "success",
            "message": "Connected to Expense Tracker server"
        })

        while True:
            raw_message, buffer = receive_message(conn, buffer)

            if raw_message is None:
                print(f"Client {address} disconnected.")
                break

            try:
                data = json.loads(raw_message.decode("utf-8"))

                print(f"Request from {address}: {data}")

                action = data.get("action")

                # Check server
                if action == "ping":
                    response = {
                        "status": "success",
                        "message": "Server is running"
                    }

                # Add expense to MySQL
                elif action == "add_expense":
                    amount = data["amount"]
                    category = data["category"]
                    description = data.get("description", "")

                    expense_id = add_expense(
                        amount,
                        category,
                        description
                    )

                    response = {
                        "status": "success",
                        "message": "Expense added successfully",
                        "expense_id": expense_id
                    }

                # View all expenses
                elif action == "view_expenses":
                    expenses = get_expenses()

                    response = {
                        "status": "success",
                        "expenses": expenses
                    }

                elif action == "expense_summary":
                    summary = get_expense_summary()

                    response = {
                        "status": "success",
                        "summary": summary
                    }

                elif action == "category_summary":
                    categories = get_category_summary()

                    response = {
                        "status": "success",
                        "categories": categories
                    }

                elif action == "delete_expense":
                    expense_id = data["expense_id"]
                    deleted = delete_expense(expense_id)
                    if deleted:
                        response = {
                            "status": "success",
                            "message": "Expense deleted successfully"
                        }
                    else:
                        response = {
                            "status": "error",
                            "message": "Expense ID not found"
                        }
            
                elif action == "update_expense":
                    expense_id = data["expense_id"]
                    amount = data["amount"]
                    category = data["category"]
                    description = data.get("description", "")

                    if float(amount) <= 0:
                        response = {
                            "status": "error",
                            "message": "Amount must be greater than zero"
                        }

                    elif not str(category).strip():
                        response = {
                            "status": "error",
                            "message": "Category cannot be empty"
                        }

                    else:
                        updated = update_expense(
                            expense_id,
                            amount,
                            category,
                            description
                        )

                        if updated:
                            response = {
                                "status": "success",
                                "message": "Expense updated successfully"
                            }
                        else:
                            response = {
                                "status": "error",
                                "message": "Expense ID not found or no changes made"
                            }
                # Exit
                elif action == "exit":
                    send_message(conn, {
                        "status": "success",
                        "message": "Goodbye!"
                    })
                    break

                # Unknown request
                else:
                    response = {
                        "status": "error",
                        "message": "Unknown action"
                    }

                send_message(conn, response)

            except (json.JSONDecodeError, UnicodeDecodeError):
                send_message(conn, {
                    "status": "error",
                    "message": "Invalid JSON message"
                })

            except KeyError as e:
                send_message(conn, {
                    "status": "error",
                    "message": f"Missing field: {e}"
                })

            except (TypeError, ValueError) as e:
                send_message(conn, {
                    "status": "error",
                    "message": f"Invalid data: {e}"
                })

            except Exception as e:
                print("Request failed:", repr(e))

                send_message(conn, {
                    "status": "error",
                    "message": str(e)
                })

    except OSError as e:
        print(f"Communication error with {address}: {e}")

    finally:
        conn.close()
        print(f"Connection closed: {address}")


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(5)

print(f"Server listening on port {PORT}...")

try:
    while True:
        conn, address = server.accept()

        thread = threading.Thread(
            target=handle_client,
            args=(conn, address),
            daemon=True
        )

        thread.start()

except KeyboardInterrupt:
    print("\nServer shutting down.")

finally:
    server.close()