import socket
import json

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


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.settimeout(30)

buffer = b""

try:
    # Connect to server
    client.connect((HOST, PORT))
    print("Connected to server!")

    greeting, buffer = receive_message(client, buffer)
    print("Server:", greeting.get("message", greeting))

    while True:
        print("\n========== EXPENSE TRACKER ==========")
        print("1. Check server")
        print("2. Add expense")
        print("3. View expenses")
        print("4. Delete expense")
        print("5. Update expense")
        print("6. Exit")
        print("7. View expense summary")
        print("8. View category-wise spending")

        choice = input("Choose an option: ").strip()

        # 1. Check server
        if choice == "1":
            request = {
                "action": "ping"
            }

        # 2. Add expense
        elif choice == "2":
            try:
                amount = float(input("Enter amount: "))

                if amount <= 0:
                    print("Amount must be greater than zero.")
                    continue

                category = input("Enter category: ").strip()
                description = input("Enter description: ").strip()

                if not category:
                    print("Category cannot be empty.")
                    continue

                request = {
                    "action": "add_expense",
                    "amount": amount,
                    "category": category,
                    "description": description
                }

            except ValueError:
                print("Please enter a valid amount.")
                continue

        # 3. View expenses
        elif choice == "3":
            request = {
                "action": "view_expenses"
            }

        # 4. Delete expense
        elif choice == "4":
            try:
                expense_id = int(
                    input("Enter expense ID to delete: ")
                )

                if expense_id <= 0:
                    print("Expense ID must be greater than zero.")
                    continue

                request = {
                    "action": "delete_expense",
                    "expense_id": expense_id
                }

            except ValueError:
                print("Please enter a valid expense ID.")
                continue

        # 5. Update expense
        elif choice == "5":
            try:
                expense_id = int(
                    input("Enter expense ID to update: ")
                )

                if expense_id <= 0:
                    print("Expense ID must be greater than zero.")
                    continue

                amount = float(input("Enter new amount: "))

                if amount <= 0:
                    print("Amount must be greater than zero.")
                    continue

                category = input("Enter new category: ").strip()

                if not category:
                    print("Category cannot be empty.")
                    continue

                description = input(
                    "Enter new description: "
                ).strip()

                request = {
                    "action": "update_expense",
                    "expense_id": expense_id,
                    "amount": amount,
                    "category": category,
                    "description": description
                }

            except ValueError:
                print("Please enter valid numeric values.")
                continue

        # 6. Exit
        elif choice == "6":
            request = {
                "action": "exit"
            }

        # 7. Expense summary
        elif choice == "7":
            request = {
                "action": "expense_summary"
            }

        # 8. Category-wise spending
        elif choice == "8":
            request = {
                "action": "category_summary"
            }

        else:
            print("Invalid choice. Try again.")
            continue

        # Send request to server
        send_message(client, request)

        # Receive response from server
        response, buffer = receive_message(client, buffer)

        print("\n========== SERVER RESPONSE ==========")

        if response.get("status") != "success":
            print(
                "Error:",
                response.get("message", "Request failed.")
            )

        # Response: Check server
        elif choice == "1":
            print(response.get("message", "Server is running."))

        # Response: Add expense
        elif choice == "2":
            print(
                response.get(
                    "message",
                    "Expense request completed."
                )
            )

            if "expense_id" in response:
                print("Expense ID:", response["expense_id"])

        # Response: View expenses
        elif choice == "3":
            expenses = response.get("expenses", [])

            if not expenses:
                print("No expenses found.")

            else:
                print("-" * 75)

                print(
                    f"{'ID':<6}"
                    f"{'Amount':<12}"
                    f"{'Category':<20}"
                    f"{'Description'}"
                )

                print("-" * 75)

                for expense in expenses:
                    print(
                        f"{expense['id']:<6}"
                        f"{expense['amount']:<12.2f}"
                        f"{expense['category']:<20}"
                        f"{expense.get('description') or ''}"
                    )

                print("-" * 75)

        # Response: Delete expense
        elif choice == "4":
            print(
                response.get(
                    "message",
                    "Delete operation completed."
                )
            )

        # Response: Update expense
        elif choice == "5":
            print(
                response.get(
                    "message",
                    "Update operation completed."
                )
            )

        # Response: Exit
        elif choice == "6":
            print(response.get("message", "Goodbye!"))
            break

        # Response: Expense summary
        elif choice == "7":
            summary = response.get("summary", {})

            print("\n========== EXPENSE SUMMARY ==========")
            print(
                f"Total transactions: "
                f"{summary.get('total_transactions', 0)}"
            )
            print(
                f"Total spending: "
                f"₹{summary.get('total_amount', 0):,.2f}"
            )
            print(
                f"Average expense: "
                f"₹{summary.get('average_amount', 0):,.2f}"
            )

        # Response: Category-wise spending
        elif choice == "8":
            categories = response.get("categories", [])

            print("\n======= CATEGORY-WISE SPENDING =======")

            if not categories:
                print("No expenses found.")

            else:
                print("-" * 45)
                print(f"{'Category':<25}{'Total Spending':>20}")
                print("-" * 45)

                for item in categories:
                    print(
                        f"{item['category']:<25}"
                        f"₹{item['total_amount']:>19,.2f}"
                    )

                print("-" * 45)

except (OSError, ConnectionError, json.JSONDecodeError) as e:
    print("Communication error:", e)

finally:
    client.close()
    print("Client closed.")